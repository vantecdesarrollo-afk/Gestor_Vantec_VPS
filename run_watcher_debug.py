import asyncio
import os
import traceback

async def run():
    try:
        import watcher
        print("Imported watcher successfully.")
        await watcher.main()
        print("Finished watcher.main()")
    except Exception as e:
        print(f"CRASH IN WATCHER: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run())
