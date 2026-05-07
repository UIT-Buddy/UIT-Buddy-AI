"""Grade service — wraps /api/grade endpoints."""

from __future__ import annotations

from client.buddy_client import UITBuddyClient
from exception.buddy.buddy_exception import BackendAPIError


async def get_grade_summary(
    client: UITBuddyClient, token: str, semester_code: str
) -> dict:
    """
    GET /api/grade/semester/{semesterCode} — get grades for a specific semester.
    """
    response = await client.get(f"/api/grade/semester/{semester_code}", token=token)
    if not response.is_success:
        raise BackendAPIError(response.status_code, response.text)
    return response.json()


async def get_all_grades(client: UITBuddyClient, token: str) -> dict:
    """
    GET /api/grade/all — get entire academic transcript.
    """
    response = await client.get("/api/grade/all", token=token)
    if not response.is_success:
        raise BackendAPIError(response.status_code, response.text)
    return response.json()
