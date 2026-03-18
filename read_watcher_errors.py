import os

# Filter for Fallo en or Error
if os.path.exists("watcher_live.log"):
    try:
        content = open("watcher_live.log", "r", encoding="utf-16").read()
        print("--- Filtering for exceptions ---")
        for line in content.split("\n"):
            if "Fallo en" in line or "Error" in line or "Exception" in line or "logger.error" in line:
                print(line)
    except Exception as e:
         print("Read Error:", e)
else:
    print("watcher_live.log does not exist")
