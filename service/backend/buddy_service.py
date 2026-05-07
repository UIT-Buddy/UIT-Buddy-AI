"""BuddyService — wires FastAPI endpoints to UIT Buddy Backend services."""

from __future__ import annotations

from backend import buddy_calendar as calendar_svc
from backend import buddy_document as document_svc
from backend import buddy_user as user_svc
from backend import buddy_grade as grade_svc
from backend import buddy_career as career_svc
from client.buddy_client import UITBuddyClient
from exception.buddy.buddy_exception import BackendAPIError
from exception.buddy.buddy_error_code import BuddyErrorCode


class BuddyService:
    """Thin async wrapper around UIT Buddy Backend services."""

    def __init__(self):
        self.client = UITBuddyClient()

    @staticmethod
    def _validate_token(token: str) -> None:
        if not token or not str(token).strip():
            raise BackendAPIError.from_definition(BuddyErrorCode.MISSING_TOKEN)
        raw = str(token).strip()
        if raw.count(".") != 2:
            raise BackendAPIError.from_definition(BuddyErrorCode.INVALID_TOKEN)

    @staticmethod
    def _normalize_backend_error(exc: BackendAPIError) -> BackendAPIError:
        if exc.status_code == 401:
            return BackendAPIError.from_definition(BuddyErrorCode.INVALID_TOKEN)
        if exc.status_code == 504:
            return BackendAPIError.from_definition(BuddyErrorCode.BACKEND_TIMEOUT)
        if exc.status_code >= 500:
            return BackendAPIError.from_definition(BuddyErrorCode.BACKEND_UNAVAILABLE)
        return exc

    async def get_deadlines(
        self,
        token: str,
        page: int = 1,
        limit: int = 15,
        sortType: str = "desc",
        sortBy: str = "created_at",
        month: int = 1,
        year: int = 1,
    ) -> dict:
        self._validate_token(token)
        async with self.client:
            try:
                return await calendar_svc.get_deadlines(
                    self.client,
                    token,
                    page=page,
                    limit=limit,
                    sortType=sortType,
                    sortBy=sortBy,
                    month=month,
                    year=year,
                )
            except BackendAPIError as exc:
                raise self._normalize_backend_error(exc)

    async def create_deadline(
        self,
        token: str,
        exerciseName: str,
        classCode: str,
        dueDate: str,
    ) -> dict:
        self._validate_token(token)
        async with self.client:
            try:
                return await calendar_svc.create_deadline(
                    self.client,
                    token,
                    exerciseName=exerciseName,
                    classCode=classCode,
                    dueDate=dueDate,
                )
            except BackendAPIError as exc:
                raise self._normalize_backend_error(exc)

    async def get_calendar(
        self,
        token: str,
        year: str = "",
        semester: str = "",
    ) -> dict:
        self._validate_token(token)
        async with self.client:
            try:
                return await calendar_svc.get_calendar(
                    self.client,
                    token,
                    year=year,
                    semester=semester,
                )
            except BackendAPIError as exc:
                raise self._normalize_backend_error(exc)

    async def get_user_profile(self, token: str) -> dict:
        self._validate_token(token)
        async with self.client:
            try:
                return await user_svc.get_me(self.client, token)
            except BackendAPIError as exc:
                raise self._normalize_backend_error(exc)

    async def get_folder(
        self,
        token: str,
        folderId: str = "",
        page: int = 1,
        limit: int = 15,
        sortType: str = "desc",
        sortBy: str = "createdAt",
    ) -> dict:
        self._validate_token(token)
        async with self.client:
            try:
                return await document_svc.get_folder(
                    self.client,
                    token,
                    folderId=folderId,
                    page=page,
                    limit=limit,
                    sortType=sortType,
                    sortBy=sortBy,
                )
            except BackendAPIError as exc:
                raise self._normalize_backend_error(exc)

    async def search_documents(
        self,
        token: str,
        keyword: str = "",
        page: int = 1,
        limit: int = 15,
        sortType: str = "desc",
        sortBy: str = "createdAt",
    ) -> dict:
        self._validate_token(token)
        async with self.client:
            try:
                return await document_svc.search_documents(
                    self.client,
                    token,
                    keyword=keyword,
                    page=page,
                    limit=limit,
                    sortType=sortType,
                    sortBy=sortBy,
                )
            except BackendAPIError as exc:
                raise self._normalize_backend_error(exc)

    async def get_shared_documents(
        self,
        token: str,
        keyword: str = "",
        page: int = 1,
        limit: int = 15,
    ) -> dict:
        self._validate_token(token)
        async with self.client:
            try:
                return await document_svc.get_shared_documents(
                    self.client,
                    token,
                    keyword=keyword,
                    page=page,
                    limit=limit,
                )
            except BackendAPIError as exc:
                raise self._normalize_backend_error(exc)

    async def download_document(self, token: str, fileId: str) -> bytes:
        self._validate_token(token)
        async with self.client:
            try:
                return await document_svc.download_document(self.client, token, fileId)
            except BackendAPIError as exc:
                raise self._normalize_backend_error(exc)

    async def get_grade_summary(self, token: str, semester_code: str) -> dict:
        self._validate_token(token)
        async with self.client:
            try:
                return await grade_svc.get_grade_summary(
                    self.client, token, semester_code=semester_code
                )
            except BackendAPIError as exc:
                raise self._normalize_backend_error(exc)

    async def get_all_grades(self, token: str) -> dict:
        self._validate_token(token)
        async with self.client:
            try:
                return await grade_svc.get_all_grades(self.client, token)
            except BackendAPIError as exc:
                raise self._normalize_backend_error(exc)

    async def get_career_support(
        self, token: str, keywords: str = "", lang: str = "vi"
    ) -> dict:
        self._validate_token(token)
        async with self.client:
            try:
                return await career_svc.get_career_roadmap(
                    self.client, token, keywords=keywords, lang=lang
                )
            except BackendAPIError as exc:
                raise self._normalize_backend_error(exc)


_buddy_service: BuddyService | None = None


def get_buddy_service() -> BuddyService:
    global _buddy_service
    if _buddy_service is None:
        _buddy_service = BuddyService()
    return _buddy_service
