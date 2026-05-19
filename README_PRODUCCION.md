# VCore VPS - Server Playbook (L6 Hardening)

Este es el manual oficial de despliegue de Infraestructura VCore en entornos Cloud/VPS (Linux) mediante **Coolify** y **Docker**.

## 1. Requisitos Previos en Coolify
1. En tu panel de Coolify, crea un nuevo **Project** y un **Resource** de tipo *Docker Compose* o *Dockerfile* (basado en este repositorio git).
2. Necesitarás tener tu dominio enrutado (ej. `api.vantec.com.mx`) apuntando a la IP pública de tu servidor. Coolify genera automáticamente los certificados Let's Encrypt (SSL).

## 2. Variables de Entorno (Environment Variables)
El contenedor **NO** debe almacenar credenciales en disco. Define las siguientes variables en la sección "Environment Variables" de Coolify:

```env
DATABASE_URL=postgresql+asyncpg://usuario:password@host:5432/vcore_db
JWT_SECRET=tu_secreto_super_seguro
JWT_ALGORITHM=HS256
```

> **IMPORTANTE**: No uses la base de datos local (SQLite). Debes apuntar a la base de datos gestionada de PostgreSQL.

## 3. Mapeo de Volúmenes (Persistencia de Datos)
El sistema ha sido adaptado para realizar almacenamiento en la ruta `/app/Operacion_CFDI`. Es crítico mapear un disco externo o persistente de Coolify a esta ruta.

1. En la configuración del servicio en Coolify, ve a la pestaña **Storages**.
2. Añade un volumen:
   - **Host Path**: `/mnt/vcore_data/operacion_cfdi` (o cualquier ruta segura de tu servidor host).
   - **Container Path**: `/app/Operacion_CFDI`

Si omites este paso, al reconstruir la imagen en Coolify se perderán los archivos (Ghost PDFs, logs y repositorios de Tenants).

## 4. Migración de Base de Datos y Auto-Seeding
Antes de arrancar en caliente, debes preparar la DB en PostgreSQL:
1. Conéctate a la base de datos destino usando DBeaver o DataGrip.
2. Ejecuta el script `master_schema_vcore_vps.sql` o `dump_maestro.sql` incluido en la raíz de este proyecto para estructurar las 19 tablas maestras del estándar de integridad Vantec.
3. Asegúrate de insertar al menos un `tenant` para generar su `api_key` y dársela al cliente.

> [!NOTE]
> **Resiliencia de Arranque (Lifespan Auto-Seeding)**: El sistema está equipado con un manejador de contexto `lifespan` en `src/main.py` que ejecuta la inyección automática del usuario semilla (`admin / @dm1n***`) de forma asíncrona al arrancar. Si las tablas de base de datos no se han creado o la base de datos no está disponible temporalmente, el sistema registrará una advertencia en los logs (`⚠️ [STARTUP WARNING]`) pero **se mantendrá online**, evitando bucles de caída y errores `502 Bad Gateway` en Coolify.

## 5. Configuración de Puerto y Enrutamiento
El contenedor del backend está configurado para escuchar en el **puerto `8000`** en producción (alineado con la directiva técnica de VCore L6):
- **Dockerfile**: `EXPOSE 8000` y ejecuta Uvicorn con `--port 8000`.
- **Coolify**: Asegúrate de que las reglas de balanceo e ingreso HTTP de Coolify enruten el tráfico directamente al puerto `8000` del contenedor.

## 6. Diccionario de Errores (Troubleshooting)
Si el cliente reporta errores en la ingesta, revisa los códigos HTTP:
- **400 Bad Request**: El XML o PDF está corrupto. Faltan datos (ej. Nodo Emisor) o el payload venía vacío.
- **401 Unauthorized**: La llave enviada en el header `X-API-KEY` es incorrecta o no existe.
- **403 Forbidden**: (Zero Trust) El RFC del XML no coincide con el RFC asociado al Tenant en la BD. O bien, el Tenant fue marcado como `is_active=false`.
- **422 Unprocessable Entity**: Problemas de validación de FastAPI (Pydantic). Generalmente un error en el tipo de archivo enviado (`multipart/form-data`).
- **500 Internal Server Error**: Hubo un error de persistencia, se cayó el parser L6 o no hay permisos en la carpeta `/app/Operacion_CFDI`. Revisa los logs del contenedor.
