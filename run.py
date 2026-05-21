import asyncio
import uvicorn
from api.main import app
from bot.main import main as start_bot

async def run_api():
    config = uvicorn.Config(app, host="0.0.0.0", port=7860)
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    await asyncio.gather(
        run_api(),
        start_bot()
    )

if __name__ == "__main__":
    asyncio.run(main())
