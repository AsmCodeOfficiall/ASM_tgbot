import sys
from pathlib import Path
from fastapi import APIRouter, Request
from bot.config import settings
from bot.notify import send_github_alert

import hmac
import hashlib
from fastapi import HTTPException, Header

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

router = APIRouter(prefix="/api/webhook")

GITHUB_SECRET = settings.GITHUB_WEBHOOK_SECRET 

@router.post("/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None) # GitHub's security signature
):
    # Read the raw body for signature verification
    payload_body = await request.body()
    
    # Verify it actually came from GitHub
    if not x_hub_signature_256:
        raise HTTPException(status_code=401, detail="Missing signature")
        
    expected_signature = "sha256=" + hmac.new(
        GITHUB_SECRET.encode(), payload_body, hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(expected_signature, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse the JSON payload
    data = await request.json()
    
    # Check if it's a push to the main branch
    if data.get("ref") == "refs/heads/main":
        pusher = data.get("pusher", {}).get("name", "Unknown Developer")
        commits = data.get("commits", [])
        
        # Format the message
        text = f"🚀 <b>New Push to Main!</b>\n"
        text += f"👤 <b>Author:</b> {pusher}\n\n"
        text += "<b>Commits:</b>\n"
        
        for commit in commits:
            text += f"• <code>{commit['id'][:7]}</code>: {commit['message']}\n"
            
        # Send it to Telegram
        await send_github_alert(text)
        
    return {"status": "ok"}
