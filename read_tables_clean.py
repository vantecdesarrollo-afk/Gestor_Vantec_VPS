import os

if os.path.exists("tables_out.txt"):
    try:
        content = open("tables_out.txt", "r", encoding="utf-16").read()
        with open("tables_summary.txt", "w", encoding="utf-8") as f:
            for line in content.split("\n"):
                if "Table" in line or "Found" in line:
                    f.write(line + "\n")
        print("Summary written.")
    except Exception as e:
        print("Error:", e)
else:
    print("tables_out.txt does not exist")
