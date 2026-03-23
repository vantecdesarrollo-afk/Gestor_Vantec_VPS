import os

paths_to_check = [r"C:\Test_Antigravity", r"C:\Vantec", r"C:\ITC"]

with open('large_folders_search.txt', 'w', encoding='utf-8') as f:
    for path in paths_to_check:
        f.write(f"=== Checking {path} ===\n")
        if not os.path.exists(path):
            f.write("Path not found\n")
            continue
        for root, dirs, files in os.walk(path):
            if len(files) > 100:
                f.write(f"Folder: {root} - Files count: {len(files)}\n")
    f.write("\n")
f.close()
print("Done")
