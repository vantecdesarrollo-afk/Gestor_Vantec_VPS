FROM python:3.11-slim

# Directorio de trabajo
WORKDIR /app

# Instalación de dependencias del sistema para psycopg2/asyncpg
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia de requisitos e instalación
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia del código fuente
COPY . .

# Exponer puerto de FastAPI
EXPOSE 8000

# Comando para ejecutar la aplicación (suponiendo src.main:app)
# TODO: Verificar si el punto de entrada es src.main:app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
