with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\templates\cfdis.html", "r", encoding="utf-8") as f:
    html = f.read()

# Verify headers for filters
print("HEADERS IN HTML:")
import re
ths = re.findall(r'<th[^>]*>(.*?)</th>', html, re.DOTALL)
for th in ths:
    print(f"TH: {th.strip()}")

# Read pip list
try:
    with open(r"C:\tmp\pip_list_full.txt", "r", encoding="utf-16") as f:
         c = f.read()
         print("\nPIP LIST (PDF CHECK):")
         for l in c.split('\n'):
              if 'reportlab' in l.lower() or 'fpdf' in l.lower() or 'pdfkit' in l.lower():
                   print(l.strip())
except Exception as e:
    print(f"Error reading pip list: {str(e)}")
