import os

if os.path.exists("check_paths.txt"):
    try:
        content = open("check_paths.txt", "r", encoding="utf-16").read()
        with open("missing_paths.txt", "w", encoding="utf-8") as f:
            for line in content.split("\n"):
                if line.startswith("UUID:") and ("Exists: False" in line):
                    f.write(line + "\n")
        print("Missing written to missing_paths.txt")
    except Exception as e:
        print("Error:", e)
else:
    print("check_paths.txt does not exist")
