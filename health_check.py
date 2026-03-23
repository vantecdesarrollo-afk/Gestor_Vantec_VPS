try:
    import sys, os
    sys.path.insert(0, r"C:\Test_Antigravity\Gestor_CFDI_Vantec")
    
    print("Iniciando Health Check de FastAPI...")
    from src.main import app
    print("✅ Autenticado: El Servidor FastAPI Compila correctamente y está listo para encender.")
    sys.exit(0)
except Exception as e:
    import traceback
    print("\n❌ FALLO DE COMPILACIÓN DETECTADO:")
    traceback.print_exc()
    sys.exit(1)
