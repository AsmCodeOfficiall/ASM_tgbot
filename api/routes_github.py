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
    x_hub_signature_256: str = Header(None), # The security signature
    x_github_event: str = Header(None)       # The type of event (push, pull_request, etc.)
):
    # Verify it actually came from GitHub
    payload_body = await request.body()
    if not x_hub_signature_256:
        raise HTTPException(status_code=401, detail="Missing signature")
        
    expected_signature = "sha256=" + hmac.new(
        GITHUB_SECRET.encode(), payload_body, hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(expected_signature, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse the JSON payload
    data = await request.json()
    
    # ---------------------------------------------------------
    # SCENARIO A: A Direct Push to Main
    # ---------------------------------------------------------
    if x_github_event == "push":
        if data.get("ref") == "refs/heads/main":
            pusher = data.get("pusher", {}).get("name", "Unknown Developer")
            commits = data.get("commits", [])
            
            text = f"🚀 <b>New Push to Main!</b>\n"
            text += f"👤 <b>Author:</b> {pusher}\n\n"
            text += "<b>Commits:</b>\n"
            
            for commit in commits:
                text += f"• <code>{commit['id'][:7]}</code>: {commit['message']}\n"
                
            await send_github_alert(text)

    # ---------------------------------------------------------
    # SCENARIO B: A Pull Request is Merged to Main
    # ---------------------------------------------------------
    elif x_github_event == "pull_request":
        action = data.get("action")
        pr = data.get("pull_request", {})
        
        # Check if the PR was closed, actually merged (not just rejected), and targeting main
        if action == "closed" and pr.get("merged") is True:
            base_branch = pr.get("base", {}).get("ref")
            
            if base_branch == "main":
                pr_title = pr.get("title")
                pr_url = pr.get("html_url")
                # user who clicked the merge button
                merger = pr.get("merged_by", {}).get("login", "Someone") 
                # user who wrote the code
                author = pr.get("user", {}).get("login", "A developer")  
                
                text = f"🔀 <b>PR Merged into Main!</b>\n"
                text += f"👷 <b>Author:</b> {author}\n"
                text += f"✅ <b>Merged by:</b> {merger}\n\n"
                text += f"📌 <b>{pr_title}</b>\n"
                text += f"🔗 <a href='{pr_url}'>View Pull Request</a>"
                
                await send_github_alert(text)

    # Always return a 200 OK so GitHub knows we received it
    return {"status": "ok"}