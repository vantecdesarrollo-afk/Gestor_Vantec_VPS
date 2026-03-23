import os

with open('drives_list.txt', 'w', encoding='utf-8') as f:
    for drive in ['D:\\', 'E:\\', 'G:\\']:
        f.write(f"=== {drive} ===\n")
        try:
            if os.path.exists(drive):
                items = os.listdir(drive)
                for item in items:
                    f.write(f"{item}\n")
            else:
                f.write("Drive not found\n")
        except Exception as e:
            f.write(f"Error: {e}\n")
    f.write("\n")
