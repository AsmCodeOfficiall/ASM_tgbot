import sys
from pathlib import Path
from fastapi import APIRouter, Request

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

router = APIRouter(prefix="/api/webhook")


@router.post("/github")
async def github_webhook(request: Request):
    payload = await request.json()

    try:
        from bot.notify import send_github_alert
        
        event_type = request.headers.get("X-GitHub-Event", "unknown")
        repo = payload.get("repository", {}).get("name", "unknown")
        sender = payload.get("sender", {}).get("login", "unknown")
        
        message = f"GitHub Event: {event_type}\nRepo: {repo}\nUser: {sender}"
        await send_github_alert(message)
    except ImportError:
        pass

    return {"status": "ok"}
