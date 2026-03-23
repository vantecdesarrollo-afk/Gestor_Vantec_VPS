import os

path = r"C:\ITC\FAppeal"

with open('planeta_folders.txt', 'w', encoding='utf-8') as f:
    for root, dirs, files in os.walk(path):
        if 'OutFile' in root or 'Outfile' in root or 'Planeta' in root:
            f.write(f"{root} - dirs: {len(dirs)} - files: {len(files)}\n")
f.close()
print("Done")
