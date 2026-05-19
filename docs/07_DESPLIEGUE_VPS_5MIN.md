# 🚀 MANUAL DE DESPLIEGUE EXPRES: VANTEC VCORE VPS (5 MINUTOS)

Este manual técnico describe el flujo de despliegue automatizado "Plug & Play" para entornos VPS, Docker y Coolify. Gracias a la reingeniería de la versión L6, el sistema se auto-provisiona en su arranque inicial sin intervención humana y sin necesidad de ejecutar scripts semilla manuales.

---

## 🏗️ 1. Las Dos Correcciones de Raíz Aplicadas

Para garantizar que el sistema funcione de manera autónoma e inmediata al instalarse, se aplicaron dos parches estructurales en el núcleo del sistema:

### A. JWT Seguro para Súper Administradores (`src/api/endpoints/auth.py`)
Anteriormente, el sistema arrojaba un Error 500 al intentar iniciar sesión con una cuenta de Súper Administrador debido a que su campo `tenant_id` es nativamente `NULL` (ya que no pertenece a ningún Tenant individual, sino que gestiona a todos). 
* **Solución Aplicada:** Añadimos un filtro seguro en la creación del JWT para encapsular el ID de inquilino de forma opcional:
  ```python
  tenant_id_str = str(user.tenant_id) if getattr(user, "tenant_id", None) else None
  ```
  De esta forma, el Súper Administrador entra de forma nativa e independiente, con acceso total ("Modo Neutral"), sin requerir un Tenant falso asignado.

### B. Visibilidad Total en Auto-Seeding (`src/main.py`)
El motor de auto-seeding fallaba silenciosamente al inicializar la base de datos por primera vez en entornos Docker/Coolify, ocultando los detalles de la excepción en la salida estándar de logs.
* **Solución Aplicada:** Vinculamos el bloque de captura de excepciones en el `lifespan` de FastAPI directamente al logger de Uvicorn:
  ```python
  except Exception as e:
      logger.error(f"⚠️ [STARTUP WARNING] Error en auto-seeding de base de datos: {str(e)}")
  ```
  Ahora, cualquier error de migración, conexión de red o permisos de base de datos se reporta inmediatamente en los logs del contenedor en tiempo real.

---

## 🛠️ 2. Flujo de Despliegue en 5 Minutos (Docker & Coolify)

### Paso 1: Configurar Variables de Entorno (`.env`)
En el panel de Coolify o en tu archivo `.env` en la raíz del VPS, define las variables mínimas esenciales:

```env
# --- CONFIGURACIÓN DEL SISTEMA ---
SECRET_KEY=super_secret_jwt_encryption_key_vcore_l6
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24

# --- CONEXIÓN DE BASE DE DATOS ---
# Reemplaza con las credenciales de tu PostgreSQL en el VPS
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/vcore_db
```

> [!IMPORTANT]
> El sistema utiliza conexión asíncrona mediante `asyncpg`. Asegúrate de que el prefijo del driver de base de datos sea siempre `postgresql+asyncpg://`.

### Paso 2: Construir y Lanzar el Contenedor
El despliegue está completamente dockerizado. En la raíz del proyecto, ejecuta el comando estándar:

```bash
docker compose up -d --build
```
*Si estás usando **Coolify**, simplemente haz clic en **Deploy** y la imagen se reconstruirá automáticamente a partir del Dockerfile existente.*

### Paso 3: Inicialización Automática (Zero-Touch)
1. Al levantar, el proceso `lifespan` de la aplicación se conecta a la base de datos PostgreSQL.
2. Si detecta que no existe ningún administrador global, **crea automáticamente la cuenta semilla**.
3. **Credenciales maestras de arranque:**
   * **Usuario:** `admin`
   * **Contraseña:** `admin123` *(Esta contraseña se cifra de manera segura en el arranque usando salt bcrypt de 12 iteraciones)*

---

## 🔍 3. Verificación de Arranque Limpio

Para comprobar que el servidor se levantó perfectamente en menos de 5 minutos, ejecuta:

```bash
docker logs -f <nombre_del_contenedor_api>
```

Deberás observar una salida limpia como la siguiente en tu terminal:

```ansi
[LIFESPAN] Iniciando VCore VPS Backend...
[SEEDING] Base de datos inaugurada exitosamente con el Usuario Semilla Global.
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## 🚨 4. Protocolo de Higiene Posterior al Despliegue

Una vez que el sistema esté en línea (accediendo a `http://tu-vps-ip:8000`), es obligatorio seguir estas dos directrices para blindar la instalación:

1. **Cambiar Contraseña Maestra:** Ve a la sección de perfil y actualiza la contraseña predeterminada (`admin123`) por una clave robusta corporativa.
2. **Entrar en Modo Producción:** La base de datos asimilará de inmediato la nueva clave y deshabilitará automáticamente cualquier intento de reinyección de claves genéricas en posteriores arranques del servidor.
