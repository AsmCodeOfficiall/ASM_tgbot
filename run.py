import asyncio
import socket
import uvicorn

# Force IPv4 globally to prevent 60-second IPv6 fallback delays on Hugging Face
_orig_getaddrinfo = socket.getaddrinfo
def patched_getaddrinfo(*args, **kwargs):
    if len(args) >= 3:
        args = list(args)
        args[2] = socket.AF_INET
    else:
        kwargs['family'] = socket.AF_INET
    return _orig_getaddrinfo(*args, **kwargs)
socket.getaddrinfo = patched_getaddrinfo

import os
import sys
from api.main import app

def main():
    if os.environ.get("SPACE_ID"):
        print("Running on Hugging Face Spaces is disabled due to network restrictions.")
        print("This prevents Hugging Face from stealing Telegram updates from Render.")
        sys.exit(0)
        
    # Render assigns a dynamic port via the PORT env variable. Default to 7860.
    port = int(os.environ.get("PORT", 7860))
    # Disable uvloop, use standard asyncio to prevent SSL handshake drops
    uvicorn.run(app, host="0.0.0.0", port=port, loop="asyncio")

if __name__ == "__main__":
    main()
