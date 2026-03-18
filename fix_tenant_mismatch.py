import asyncio
import os
import shutil
from src.database.session import AsyncSessionLocal
from sqlalchemy import text

async def main():
    # 1. Wipe DB (Clean Slate)
    print("Wiping 'cfdis' table...")
    async with AsyncSessionLocal() as db:
        await db.execute(text("DELETE FROM cfdis;"))
        await db.commit()
    print("DB fully cleaned.")

    # 2. Find files in early tenant folder
    wd = os.getcwd()
    wrong_tenant = "00000000-0000-0000-0000-446655440000"
    storage_dir = os.path.join(wd, "storage", "tenants", wrong_tenant)
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
        print("Storage directory for wrong tenant not found.")

    print(f"Moved {count} files back to DropZone for RE-INDEXING.")

if __name__ == '__main__':
    asyncio.run(main())
