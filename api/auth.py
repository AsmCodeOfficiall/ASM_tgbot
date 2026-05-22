import hashlib
import hmac
import json
from urllib.parse import parse_qs, unquote

from fastapi import HTTPException, Request

from api.config import settings


def _verify_init_data(init_data_raw: str, bot_token: str) -> dict:
    parsed = parse_qs(init_data_raw)
    received_hash = parsed.pop("hash", [None])[0]
    if not received_hash:
        raise HTTPException(status_code=401, detail="missing hash")

    data_check_pairs = []
    for key in sorted(parsed.keys()):
        data_check_pairs.append(f"{key}={unquote(parsed[key][0])}")
    data_check_string = "\n".join(data_check_pairs)

    secret_key = hmac.new(
        b"WebAppData", bot_token.encode(), hashlib.sha256
    ).digest()

    calculated_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise HTTPException(status_code=401, detail="invalid signature")

    return parsed


async def get_current_user(request: Request) -> dict:
    init_data = request.headers.get("Authorization", "")
    if not init_data:
        raise HTTPException(status_code=401, detail="no auth header")

    parsed = _verify_init_data(init_data, settings.BOT_TOKEN)

    user_data = parsed.get("user", [None])[0]
    if not user_data:
        raise HTTPException(status_code=401, detail="no user in initData")

    return json.loads(unquote(user_data))
