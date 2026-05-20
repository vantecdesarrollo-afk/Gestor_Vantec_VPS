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

# Hardening L6: Remover scripts de test, instaladores legacy y seeders de DB local
RUN rm -f seed_admin.py seed_adminBK.py install_vcore.bat start_vcore.bat stop_vcore.bat 00_*.bat arranque_silencioso.vbs vcore_manager.py watcher.py vcore_watcher_service.py execute_v6.py force_tenant_log.py

# Persistencia Real (Zero-Waste Storage para Coolify)
VOLUME ["/app/Operacion_CFDI"]

# Exponer puerto de FastAPI
EXPOSE 8000

# Comando para ejecutar la aplicación
# Comando para ejecutar la aplicación con blindaje de PATH
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

