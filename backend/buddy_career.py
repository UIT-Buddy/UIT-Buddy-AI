"""Career service — wraps /webhook/career-support endpoint."""

from __future__ import annotations

from config.app_config import UIT_BUDDY_WEBHOOK_URL
from client.buddy_client import UITBuddyClient
from exception.buddy.buddy_exception import BackendAPIError


async def get_career_roadmap(
    client: UITBuddyClient, token: str, keywords: str = "", lang: str = "en"
) -> dict:
    """
    POST /webhook/career-support — fetch career roadmap and skills.
    """
    # Use full URL to bypass the port 8080 base URL in the client
    path = f"{UIT_BUDDY_WEBHOOK_URL}/webhook/career-support"
    body = {"keywords": keywords, "lang": lang}

    response = await client.post(path, token=token, json=body)
    if not response.is_success:
        raise BackendAPIError(response.status_code, response.text)
    return response.json()
