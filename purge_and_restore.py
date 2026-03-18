import asyncio
import os
import shutil
from src.database.session import AsyncSessionLocal
from sqlalchemy import text

async def main():
    # 1. Wipe DB (Step 1)
    print("Wiping 'cfdis' table...")
    async with AsyncSessionLocal() as db:
        await db.execute(text("DELETE FROM cfdis;"))
        await db.commit()
    print("DB fully cleaned.")

    # 2. Find and Move files back
    wd = os.getcwd()
    storage_dir = os.path.join(wd, "storage", "tenants")
    target_dir = r"C:\Vantec\DropZone"
    print(f"Searching in: {storage_dir}")
    print(f"Targeting: {target_dir}")
    
    os.makedirs(target_dir, exist_ok=True)
    
    count = 0
    if os.path.exists(storage_dir):
        for root, dirs, files in os.walk(storage_dir):
            for f in files:
                if f.lower().endswith(".xml") or f.lower().endswith(".pdf"):
                    src = os.path.join(root, f)
                    dst = os.path.join(target_dir, f)
                    print(f"Moving back: {f}")
                    shutil.move(src, dst)
                    count += 1
    else:
        print("Storage directory not found, assume no files to move back.")

    print(f"Moved {count} files back to DropZone.")

if __name__ == '__main__':
    asyncio.run(main())
