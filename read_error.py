with open("C:\\Test_Antigravity\\Gestor_CFDI_Vantec\\error_log.txt", "r") as f:
    text = f.read()
    for i in range(0, len(text), 60):
        print(text[i:i+60])
