"""
GitHub Webhook handler.

Verifies the X-Hub-Signature-256 HMAC signature, then parses
push-to-main and PR-merged-to-main events and sends a formatted
alert to the team Telegram chat.

NOTE: This module no longer imports anything from bot/ — it talks
to the Telegram Bot API directly via httpx so FastAPI can start
independently of the bot process.
"""
import hashlib
import hmac
import logging

import httpx
from fastapi import APIRouter, Header, HTTPException, Request

from api.config import settings

router = APIRouter(prefix="/api/webhook")


async def _send_telegram_alert(text: str) -> None:
    """Send an HTML-formatted message to TELEGRAM_ALERT_CHAT_ID."""
    if not settings.BOT_TOKEN or not settings.TELEGRAM_ALERT_CHAT_ID:
        logging.warning("Telegram alert skipped: BOT_TOKEN or TELEGRAM_ALERT_CHAT_ID not set.")
        return
    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                url,
                json={
                    "chat_id": settings.TELEGRAM_ALERT_CHAT_ID,
                    "text": text,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True,
                },
            )
            resp.raise_for_status()
    except Exception as exc:
        logging.error("Failed to send Telegram alert: %s", exc)


def _verify_github_signature(payload: bytes, header_sig: str) -> None:
    """Raise HTTP 401 if the HMAC signature does not match."""
    if not settings.GITHUB_WEBHOOK_SECRET:
        logging.warning("GITHUB_WEBHOOK_SECRET is not set — skipping signature check.")
        return

    expected = "sha256=" + hmac.new(
        settings.GITHUB_WEBHOOK_SECRET.encode(), payload, hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, header_sig):
        raise HTTPException(status_code=401, detail="Invalid GitHub signature")


@router.post("/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None),
    x_github_event: str = Header(None),
):
    payload_body = await request.body()

    if not x_hub_signature_256:
        raise HTTPException(status_code=401, detail="Missing X-Hub-Signature-256 header")

    _verify_github_signature(payload_body, x_hub_signature_256)

    data = await request.json()

    # ------------------------------------------------------------------
    # SCENARIO A: Direct push to main
    # ------------------------------------------------------------------
    if x_github_event == "push":
        if data.get("ref") == "refs/heads/main":
            pusher = data.get("pusher", {}).get("name", "Unknown Developer")
            commits = data.get("commits", [])

            text = "🚀 <b>New Push to Main!</b>\n"
            text += f"👤 <b>Author:</b> {pusher}\n\n"
            text += "<b>Commits:</b>\n"
            for commit in commits:
                msg = commit.get("message", "").splitlines()[0]  # first line only
                text += f"• <code>{commit['id'][:7]}</code>: {msg}\n"

            await _send_telegram_alert(text)

    # ------------------------------------------------------------------
    # SCENARIO B: Pull Request merged into main
    # ------------------------------------------------------------------
    elif x_github_event == "pull_request":
        action = data.get("action")
        pr = data.get("pull_request", {})

        if action == "closed" and pr.get("merged") is True:
            base_branch = pr.get("base", {}).get("ref")
            if base_branch == "main":
                pr_title = pr.get("title", "")
                pr_url = pr.get("html_url", "")
                merger = pr.get("merged_by", {}).get("login", "Someone")
                author = pr.get("user", {}).get("login", "A developer")

                text = "🔀 <b>PR Merged into Main!</b>\n"
                text += f"👷 <b>Author:</b> {author}\n"
                text += f"✅ <b>Merged by:</b> {merger}\n\n"
                text += f"📌 <b>{pr_title}</b>\n"
                text += f"🔗 <a href='{pr_url}'>View Pull Request</a>"

                await _send_telegram_alert(text)

    # Always return 200 so GitHub marks the delivery as successful
    return {"status": "ok"}