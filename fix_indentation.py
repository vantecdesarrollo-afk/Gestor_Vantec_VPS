with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Indent lines between try (line 113 approx) and except (line 188 approx)
# Let's find exactly the line 'for r in rows:' and 'try:'
start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if "for r in rows:" in line:
         # check if next is try:
         if i + 1 < len(lines) and "try:" in lines[i+1]:
              start_idx = i + 2 # start indenting from here
              break

if start_idx != -1:
    for j in range(start_idx, len(lines)):
         if "except Exception as e_row:" in lines[j]:
              end_idx = j
              break

if start_idx != -1 and end_idx != -1:
    print(f"Indenting from line {start_idx+1} to {end_idx+1}...")
    for k in range(start_idx, end_idx):
         lines[k] = "    " + lines[k] # Add 4 spaces

    with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py", "w", encoding="utf-8") as f:
         f.write("".join(lines))
    print("Indentation error fixed")
else:
    print(f"Failed to find bounds: start={start_idx}, end={end_idx}")
