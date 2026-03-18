import sys
import traceback
import asyncio

async def test():
    with open("v100_start.log", "w", encoding="utf-8") as f:
        try:
             from src.main import app
             f.write("✅ APP IMPORT SUCCESS\n")
        except Exception:
             f.write("❌ APP IMPORT FAILED:\n")
             f.write(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(test())
