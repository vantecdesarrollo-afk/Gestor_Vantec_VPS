import os

def list_files(path):
    found = []
    try:
        for root, dirs, files in os.walk(path):
             for f in files:
                  if f.lower() == "wkhtmltopdf.exe":
                       found.append(os.path.join(root, f))
    except Exception: pass
    return found

roots = [r"C:\Test_Antigravity", r"C:\Program Files", r"C:\Program Files (x86)", r"C:\wkhtmltopdf"]
found = []
for r in roots:
    print(f"Scanning {r}...")
    found.extend(list_files(r))

with open("/tmp/wkhtml_found.txt", "w") as f:
    for item in found:
        f.write(f"{item}\n")
    
print(f"Search done, found {len(found)}")
if found:
    print(f"BEST MATCH: {found[0]}")
