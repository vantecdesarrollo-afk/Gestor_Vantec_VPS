import glob
import os

folio = "800"
clean_folio = "800"

historical_xml = [
  f"C:\\ITC\\**\\{folio}.xml",
  f"C:\\ITC\\**\\{clean_folio}.xml"
]

historical_pdf = [
  f"C:\\ITC\\**\\{folio}.pdf",
  f"C:\\ITC\\**\\{clean_folio}.pdf"
]

xml_path = None
pdf_path = None

for h in historical_xml:
    m = glob.glob(h, recursive=True)
    if m:
         xml_path = os.path.abspath(m[0])
         break

for h in historical_pdf:
    m = glob.glob(h, recursive=True)
    if m:
         pdf_path = os.path.abspath(m[0])
         break

print(f"XML: {xml_path}")
print(f"PDF: {pdf_path}")
