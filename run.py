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

from api.main import app

def main():
    # Disable uvloop, use standard asyncio to prevent SSL handshake drops
    uvicorn.run(app, host="0.0.0.0", port=7860, loop="asyncio")

if __name__ == "__main__":
    main()
