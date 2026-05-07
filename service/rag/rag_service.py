"""service/rag/rag_service.py — orchestrates LightRAG operations.

Mirrors the pattern of service/backend/buddy_service.py.
No FastAPI dependencies here — pure async business logic.
"""

from __future__ import annotations

import json
import asyncio
import re
from rag import (
    query,
    query_context,
    index_file,
)
from markitdown import MarkItDown
from starlette.concurrency import run_in_threadpool
import tempfile
import os
from client.rag_client import get_llm_func
from config.rag_config import RAG_WORKING_DIR
from enums.backend_endpoint import BackendEndpoint
from enums.faculty import extract_major_code, get_major_from_subject
from prompts.backend_planner import (
    BACKEND_ENDPOINT_PLANNER_SYSTEM,
    BACKEND_ENDPOINT_PLANNER_USER_TEMPLATE,
)
from prompts.chat_answer import (
    CHAT_ANSWER_SYSTEM,
    CHAT_ANSWER_USER_TEMPLATE,
)
from enums import AuthStatus
from service.backend.buddy_service import get_buddy_service
from exception.buddy.buddy_exception import BackendAPIError
from exception.chat.chat_exception import ChatException
from exception.chat.chat_error_code import ChatErrorCode
from dto import (
    ChatRequest,
    ChatResponse,
)


class RagService:
    """Thin async wrapper around LightRAG operations."""

    @staticmethod
    def _extract_token(authentication: str) -> str | None:
        """Extract raw JWT token from either 'Bearer <jwt>' or '<jwt>' input."""
        if not authentication:
            return None

        token = authentication.strip()
        if token.lower().startswith("bearer "):
            token = token[7:].strip()

        if token.count(".") != 2:
            return None
        return token

    async def _plan_backend_endpoints(self, question: str, has_auth: bool) -> dict:
        llm_func = get_llm_func()
        user_prompt = BACKEND_ENDPOINT_PLANNER_USER_TEMPLATE.format(
            question=question,
            has_auth=str(has_auth).lower(),
        )
        default_plan = {
            "endpoints": [],
            "reasoning": "default backend plan",
            "needDocument": False,
        }

        try:
            raw = await llm_func(
                prompt=user_prompt,
                system_prompt=BACKEND_ENDPOINT_PLANNER_SYSTEM,
                history=None,
            )
            # Clean and parse JSON
            cleaned_raw = raw.strip()
            if "```" in cleaned_raw:
                # Basic markdown extraction: take everything between the first { and last }
                start = cleaned_raw.find("{")
                end = cleaned_raw.rfind("}")
                if start != -1 and end != -1:
                    cleaned_raw = cleaned_raw[start : end + 1]

            if not cleaned_raw:
                print("Warning: LLM returned empty or non-JSON response")
                return default_plan

            data = json.loads(cleaned_raw)
            endpoints = data.get("endpoints", [])
            if not isinstance(endpoints, list):
                endpoints = []

            allowed = set(BackendEndpoint.values())
            filtered = []

            for ep in endpoints:
                if not isinstance(ep, dict):
                    continue

                name = str(ep.get("name", "")).strip()
                if name not in allowed:
                    continue

                query_params = ep.get("query_params", {})
                body = ep.get("body", {})

                if not isinstance(query_params, dict):
                    query_params = {}
                if not isinstance(body, dict):
                    body = {}

                filtered.append(
                    {
                        "name": name,
                        "query_params": query_params,
                        "body": body,
                    }
                )
            return {
                "endpoints": filtered,
                "reasoning": str(data.get("reasoning", "")).strip(),
                "needDocument": bool(data.get("needDocument", True)),
                "external_questions": bool(data.get("external_questions", False)),
            }

        except Exception as e:
            print("Exception when clarify user question", e)
            return default_plan

    async def _build_backend_context(
        self, question: str, token: str | None, plan: dict | None = None
    ) -> dict:
        if not token:
            return {
                "auth_status": AuthStatus.MISSING_OR_INVALID.value,
                "profile": None,
                "deadlines": None,
                "calendar": None,
                "shared_documents": None,
                "documents": None,
                "errors": [],
            }

        buddy_service = get_buddy_service()
        if not plan:
            plan = await self._plan_backend_endpoints(question=question, has_auth=True)
        print("plan", plan)
        selected_endpoints: list[dict] = plan.get("endpoints", [])
        endpoint_map = {
            ep["name"]: ep
            for ep in selected_endpoints
            if isinstance(ep, dict) and isinstance(ep.get("name"), str)
        }

        context: dict = {
            "auth_status": AuthStatus.OK.value,
            "profile": None,
            "deadlines": None,
            "calendar": None,
            "shared_documents": None,
            "documents": None,
            "errors": [],
        }

        if BackendEndpoint.USER_PROFILE.value in endpoint_map:
            try:
                context["profile"] = await buddy_service.get_user_profile(token=token)
            except BackendAPIError as exc:
                context["errors"].append(
                    f"user_profile_error: {exc.status_code} {exc.detail}"
                )

        if BackendEndpoint.GRADE_SUMMARY.value in endpoint_map:
            try:
                params = endpoint_map[BackendEndpoint.GRADE_SUMMARY.value].get(
                    "query_params", {}
                )
                context["grades"] = await buddy_service.get_grade_summary(
                    token=token,
                    semester_code=params.get("semesterCode"),
                )
            except BackendAPIError as exc:
                context["errors"].append(
                    f"grade_summary_error: {exc.status_code} {exc.detail}"
                )

        if BackendEndpoint.ALL_GRADES.value in endpoint_map:
            try:
                context["all_grades"] = await buddy_service.get_all_grades(token=token)
            except BackendAPIError as exc:
                context["errors"].append(
                    f"all_grades_error: {exc.status_code} {exc.detail}"
                )

        if BackendEndpoint.CAREER_SUPPORT.value in endpoint_map:
            try:
                body = endpoint_map[BackendEndpoint.CAREER_SUPPORT.value].get(
                    "body", {}
                )
                context["career_roadmap"] = await buddy_service.get_career_support(
                    token=token,
                    keywords=body.get("keywords", ""),
                    lang=body.get("lang", "en"),
                )
                print("career_roadmap", context["career_roadmap"])
            except BackendAPIError as exc:
                context["errors"].append(
                    f"career_support_error: {exc.status_code} {exc.detail}"
                )

        if BackendEndpoint.SCHEDULE_DEADLINE_GET.value in endpoint_map:
            try:
                params = endpoint_map[BackendEndpoint.SCHEDULE_DEADLINE_GET.value].get(
                    "query_params", {}
                )
                context["deadlines"] = await buddy_service.get_deadlines(
                    token=token,
                    page=params.get("page", 1),
                    limit=params.get("limit", 15),
                    sortType=params.get("sortType", "desc"),
                    sortBy=params.get("sortBy", "created_at"),
                    month=params.get("month"),
                    year=params.get("year"),
                )
            except BackendAPIError as exc:
                context["errors"].append(
                    f"deadline_error: {exc.status_code} {exc.detail}"
                )
        if BackendEndpoint.SCHEDULE_DEADLINE_CREATE.value in endpoint_map:
            try:
                params = endpoint_map[
                    BackendEndpoint.SCHEDULE_DEADLINE_CREATE.value
                ].get("body", {})
                context["deadline"] = await buddy_service.create_deadline(
                    token=token,
                    exerciseName=params.get("exerciseName"),
                    classCode=params.get("classCode"),
                    dueDate=params.get("dueDate"),
                )
            except BackendAPIError as exc:
                context["errors"].append(
                    f"deadline_error: {exc.status_code} {exc.detail}"
                )

        if BackendEndpoint.SCHEDULE_CALENDAR.value in endpoint_map:
            try:
                params = endpoint_map[BackendEndpoint.SCHEDULE_CALENDAR.value].get(
                    "query_params", {}
                )
                context["calendar"] = await buddy_service.get_calendar(
                    token=token,
                    year=params.get("year"),
                    semester=params.get("semester"),
                )
            except BackendAPIError as exc:
                context["errors"].append(
                    f"calendar_error: {exc.status_code} {exc.detail}"
                )

        if BackendEndpoint.DOCUMENT_SHARED.value in endpoint_map:
            try:
                params = endpoint_map[BackendEndpoint.DOCUMENT_SHARED.value].get(
                    "query_params", {}
                )
                context["shared_documents"] = await buddy_service.get_shared_documents(
                    token=token,
                    page=params.get("page", 1),
                    limit=params.get("limit", 15),
                    sortType=params.get("sortType", "desc"),
                    sortBy=params.get("sortBy", "createdAt"),
                    keyword=params.get("keyword", ""),
                )
            except BackendAPIError as exc:
                context["errors"].append(
                    f"shared_documents_error: {exc.status_code} {exc.detail}"
                )

        if BackendEndpoint.DOCUMENT_SEARCH.value in endpoint_map:
            try:
                params = endpoint_map[BackendEndpoint.DOCUMENT_SEARCH.value].get(
                    "query_params", {}
                )
                context["documents"] = await buddy_service.search_documents(
                    token=token,
                    keyword=params.get("keyword", question),
                    page=params.get("page", 1),
                    limit=params.get("limit", 10),
                    sortType=params.get("sortType", "desc"),
                    sortBy=params.get("sortBy", "createdAt"),
                )
            except BackendAPIError as exc:
                context["errors"].append(
                    f"document_error: {exc.status_code} {exc.detail}"
                )

        if BackendEndpoint.DOCUMENT_DOWNLOAD.value in endpoint_map:
            try:
                params = endpoint_map[BackendEndpoint.DOCUMENT_DOWNLOAD.value].get(
                    "query_params", {}
                )
                context["document"] = await buddy_service.download_document(
                    token=token,
                    fileId=params.get("fileId"),
                )
            except BackendAPIError as exc:
                context["errors"].append(
                    f"document_error: {exc.status_code} {exc.detail}"
                )

        return context

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """
        Main chat handler.

        Every question goes through the same pipeline:
          1. Fetch user-specific backend context (skipped gracefully if no token).
          2. Retrieve academic context from LightRAG (hybrid mode).
          3. Call the LLM with both contexts and an improved system prompt.
          4. Fall back to a direct RAG answer if the final LLM call fails.
        """
        try:
            token = self._extract_token(request.authentication)

            # 1. Plan endpoints and check if documents are needed
            plan = await self._plan_backend_endpoints(
                request.question, has_auth=(token is not None)
            )
            need_document = plan.get("needDocument", True)

            # 2. Build context
            backend_context = {}
            external_questions = plan.get("external_questions", False)

            if token and not external_questions:
                backend_context = await self._build_backend_context(
                    request.question, token, plan=plan
                )

            rag_context = ""
            if need_document:
                # Extract major anchor (e.g., 'KTPM' from 'KTPM2024.3')
                major_anchor = None
                if backend_context.get("profile"):
                    class_name = backend_context["profile"].get("className")
                    major_anchor = extract_major_code(class_name)

                # Priority: If question mentions a specific subject, anchor by that subject's major
                subject_match = re.search(
                    r"([A-Z]{2,3}\d{3})", request.question.upper()
                )
                if subject_match:
                    subject_major = get_major_from_subject(subject_match.group(1))
                    if subject_major:
                        major_anchor = subject_major

                rag_context = await query_context(
                    question=request.question, mode="hybrid", major_anchor=major_anchor
                )

                # 3. Check for career skills and augment RAG context
                career_roadmap = backend_context.get("career_roadmap")
                if career_roadmap:
                    skills = []
                    try:
                        # Extract skills from the career roadmap JSON
                        data_list = (
                            career_roadmap
                            if isinstance(career_roadmap, list)
                            else [career_roadmap]
                        )
                        for item in data_list:
                            suggestion = item.get("output", {}).get(
                                "career_suggestion", {}
                            )
                            for skill in suggestion.get("skills", []):
                                if skill.get("name"):
                                    skills.append(skill["name"])

                        if skills:
                            skill_query = f"UIT courses teaching these skills: {', '.join(skills)}"
                            print(f"Augmenting RAG with career skills: {skills}")
                            skill_context = await query_context(
                                question=skill_query,
                                mode="hybrid",
                                major_anchor=major_anchor,
                            )
                            rag_context = (
                                (rag_context or "")
                                + "\n\n=== RELEVANT UIT COURSES FOR REQUIRED SKILLS ===\n"
                                + skill_context
                            )
                    except Exception as e:
                        print(f"Error parsing career skills for RAG: {e}")

            print("backend_context", backend_context)

            llm_func = get_llm_func()
            user_prompt = CHAT_ANSWER_USER_TEMPLATE.format(
                question=request.question,
                backend_context=json.dumps(
                    backend_context, ensure_ascii=False, indent=2
                ),
                rag_context=rag_context or "No relevant academic context found.",
            )
            try:
                answer = await llm_func(
                    prompt=user_prompt,
                    system_prompt=CHAT_ANSWER_SYSTEM,
                    history=None,
                )
                print("answer", answer)
            except Exception as exc:
                print(f"[LLM final-answer error] {exc}")
                answer = await query(question=request.question, mode="hybrid")

            return ChatResponse(answer=answer)

        except ChatException:
            raise
        except Exception as exc:
            raise ChatException.from_definition(
                ChatErrorCode.PROCESSING_ERROR,
                message=f"{ChatErrorCode.PROCESSING_ERROR.message}: {exc}",
            )

    async def index_file(self, content: bytes, filename: str) -> dict:
        """Extract text from an uploaded file and index it into LightRAG."""
        md = MarkItDown()

        # MarkItDown.convert currently prefers file paths
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=os.path.splitext(filename)[1]
        ) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            # Extract text in a thread pool as it might be CPU intensive
            result = await run_in_threadpool(md.convert, tmp_path)
            text = result.text_content

            if not text or not text.strip():
                return {"error": "No text content extracted from file"}

            doc_id = await index_file(text=text)

            # Record the upload in a simple JSON tracker
            tracker_path = os.path.join(RAG_WORKING_DIR, "uploads.json")
            uploads = {}
            if os.path.exists(tracker_path):
                try:
                    with open(tracker_path, "r", encoding="utf-8") as f:
                        uploads = json.load(f)
                except Exception:
                    pass

            uploads[doc_id] = {
                "filename": filename,
                "timestamp": (
                    os.path.getmtime(tmp_path) if os.path.exists(tmp_path) else 0
                ),
            }

            with open(tracker_path, "w", encoding="utf-8") as f:
                json.dump(uploads, f, ensure_ascii=False, indent=2)

            return {"document_id": doc_id, "filename": filename, "status": "indexed"}
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    async def list_uploads(self) -> dict:
        """Return the list of all indexed documents from the tracker."""
        tracker_path = os.path.join(RAG_WORKING_DIR, "uploads.json")
        if not os.path.exists(tracker_path):
            return {"documents": []}

        try:
            with open(tracker_path, "r", encoding="utf-8") as f:
                uploads = json.load(f)

            # Convert dict to a list for easier consumption
            doc_list = []
            for doc_id, info in uploads.items():
                doc_list.append(
                    {
                        "document_id": doc_id,
                        "filename": info.get("filename", "unknown"),
                        "timestamp": info.get("timestamp", 0),
                    }
                )
            return {"documents": doc_list}
        except Exception as e:
            print(f"[list_uploads error] {e}")
            return {"documents": [], "error": str(e)}


_rag_service: RagService | None = None


def get_rag_service() -> RagService:
    global _rag_service
    if _rag_service is None:
        _rag_service = RagService()
    return _rag_service
