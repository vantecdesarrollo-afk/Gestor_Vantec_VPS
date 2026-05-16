import uvicorn
# 1. Importamos 'app' para que el instalador (uvicorn main:app) lo encuentre
from src.main import app 

if __name__ == "__main__":
    # 2. En tu máquina de desarrollo, pasamos el objeto 'app' directamente.
    # Al pasar el objeto y no el texto "src.main:app", 
    # evitamos que uvicorn cargue el archivo por segunda vez.
    uvicorn.run(app, host="127.0.0.1", port=8000)
    
