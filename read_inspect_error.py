with open("C:\\Test_Antigravity\\Gestor_CFDI_Vantec\\inspect_error.txt", "r") as f:
    text = f.read()
import json
with open("C:\\Test_Antigravity\\Gestor_CFDI_Vantec\\inspect_error.json", "w") as f:
    json.dump({"error": text}, f)
print("ERROR JSON SAVED")
