# Manual de Despliegue de Producción: Gestor Vantec VPS 🚀

Este manual contiene las directrices oficiales para implementar el sistema **Gestor Vantec VPS** en entornos de producción cloud usando **Coolify** y **Docker**.

El sistema ha sido reestructurado como una **"Caja Negra" autónoma y auto-suficiente**. Al iniciar, autodetecta si la base de datos está vacía, genera todo el esquema relacional en milisegundos y siembra las credenciales del administrador global por sí mismo. **No se requieren scripts SQL, importaciones manuales ni uso de DBeaver para el arranque.**

---

## 🛡️ Arquitectura L6 de Red y Aislamiento de Datos

> [!IMPORTANT]
> **REGLA DE CONVIVENCIA Y CORRESPONSABILIDAD L6**: La base de datos de Gestor Vantec debe residir en un contenedor PostgreSQL **100% independiente** y aislado.
> * **Puerto Público VPS (`5434`)**: Reservado exclusivamente para auditoría externa y herramientas de escritorio (DBeaver, DataGrip).
> * **Puerto del Proyecto Amazon Arbitrage (`5433`)**: Queda estrictamente prohibido compartir el mismo contenedor o puerto de base de datos entre ambos proyectos para evitar fallos de escalabilidad y caídas por saturación.

```mermaid
flowchart TD
    subgraph Internet / VPS Public Access
        DNS[Dominio: api.vantec.com.mx] -->|HTTPS SSL - Puerto 443| CoolifyProxy[Coolify Reverse Proxy]
        DBeaver[DBeaver / DataGrip] -.->|Acceso Seguro - Puerto 5434| DBCont
    end

    subgraph Red Interna de Docker / Coolify Network
        CoolifyProxy -->|Proxy Pass - Puerto 8000| APICont[FastAPI Backend: vantec_api]
        APICont -->|Red Privada - Puerto 5432| DBCont[PostgreSQL: vantec_db]
    end
    
    style DBCont fill:#1b263b,stroke:#00b4d8,stroke-width:2px,color:#fff;
    style APICont fill:#0d1b2a,stroke:#3a86c8,stroke-width:2px,color:#fff;
    style CoolifyProxy fill:#415a77,stroke:#e0e1dd,stroke-width:1px,color:#fff;
```

---

## 📦 Receta de Despliegue en 3 Clics (Coolify)

Sigue estos sencillos pasos para realizar una instalación limpia de 5 minutos en cualquier VPS:

### 1️⃣ Clic 1: Levantar el Recurso de PostgreSQL Aislado
1. En el panel de control de tu proyecto en **Coolify**, haz clic en **New Resource** > **Databases** > **PostgreSQL**.
2. Configura los parámetros principales del servicio:
   * **Destination/Network**: Selecciona la red interna del proyecto actual.
   * **Port Mapping (Mapeo de Puertos Host)**: Define el puerto público del VPS mapeado al puerto interno nativo del contenedor de Postgres de esta forma:
     ```text
     5434:5432
     ```
     > [!TIP]
     > Esto asegura que las herramientas de escritorio (como DBeaver) accedan de forma segura al puerto `5434` del VPS, mientras que **internamente** el tráfico de datos del backend se ejecuta en el puerto estándar `5432`.
3. Haz clic en **Start** para levantar el motor de base de datos.

### 2️⃣ Clic 2: Configurar las Variables de Entorno del Backend
Crea una nueva aplicación en Coolify basada en el repositorio Git del backend. Ve a la pestaña **Environment Variables** y define las variables de producción de forma interna.

> [!WARNING]
> **CONEXIÓN INTERNA OBLIGATORIA (Zero-Firewall)**: El host de la variable `DATABASE_URL` debe ser el nombre del contenedor o ID de servicio de base de datos generado por Coolify (ej. `cgkgg0g8gggw0oww04kk0gg4`), y el puerto de conexión debe ser el **`5432`** (el puerto interno privado).
> 
> **NUNCA** uses la dirección IP pública del VPS o el puerto expuesto `5434` para el backend. La velocidad de consulta local interna es 10 veces más rápida y es impenetrable desde el exterior.

#### Tabla de Variables a Configurar en Coolify:

| Variable | Valor Recomendado / Ejemplo | Descripción |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:Admin123@cgkgg0g8gggw0oww04kk0gg4:5432/vcore_vps` | URL de conexión asíncrona interna usando el ID del recurso Postgres de Coolify en el puerto `5432`. |
| `VANTEC_SECRET_KEY` | `un_secreto_super_seguro_jwt_generado_con_openssl` | Llave criptográfica para firmas de tokens de autenticación JWT. |
| `SESSION_INACTIVITY_TIMEOUT_MINUTES` | `15` | Límite máximo de inactividad de sesión (minutos) antes de desconexión. |
| `SESSION_MAX_LIFETIME_MINUTES` | `30` | Expiración absoluta de la sesión de usuario (minutos) por seguridad L6. |
| `STORAGE_PATH` | `/app/Operacion_CFDI` | Ruta interna del volumen persistente del backend para la ingesta de archivos. |

### 3️⃣ Clic 3: Mapear Volúmenes y Persistencia
Para evitar que los XMLs, PDFs y repositorios de Tenants se eliminen en las futuras actualizaciones o despliegues del contenedor backend:
1. Ve a la pestaña **Storages** (Almacenamiento) en la configuración de la aplicación backend en Coolify.
2. Agrega un volumen persistente configurando los siguientes mapeos:
   * **Host Path**: `/mnt/vcore_data/operacion_cfdi` (ruta persistente dentro del disco duro del VPS).
   * **Container Path**: `/app/Operacion_CFDI`
3. Haz clic en **Deploy** (Desplegar).

---

## ⚡ Inicialización Autónoma ("Caja Negra")

Una vez disparado el despliegue del Backend en Coolify, la API iniciará de forma 100% automatizada gracias a su motor resiliente:

* **Generación Dinámica de Tablas**: En el evento `lifespan` de inicio, el motor ejecuta `Base.metadata.create_all` en PostgreSQL de manera asíncrona. Si la base de datos está totalmente vacía, autogenera las tablas operativas (`tenants`, `users`, `comprobantes`, `entidad_smtp_configs`, `financial_anomalies_logs`, `cfdi_relacionados`, `cfdi_conceptos`, `usuario_entidad_acceso`, `auth_recovery_tokens`) de inmediato.
* **Auto-Sembrado de Superusuario**: Acto seguido, el sistema verifica e introduce al usuario semilla global con rol de administración general si no está presente en la base de datos:
  * **Usuario / Nombre de Usuario**: `admin`
  * **Email Asociado**: `admin@vcore.com`
  * **Contraseña por Defecto**: `@dm1n***`
* **Cero Configuración Manual**: No necesitas abrir DBeaver, ni restaurar dumps de bases de datos, ni correr archivos `.sql`. El sistema autoconstruye su propio esquema listo para usarse.

---

## 🧩 Diccionario de Diagnóstico y Respuestas HTTP

Si se presentan fallos en integraciones externas o clientes, este diccionario te guiará para diagnosticar el problema en segundos:

* **`400 Bad Request`**: El XML o PDF enviado tiene daños estructurales, faltan nodos de validación obligatorios del SAT (ej. nodo Emisor o Receptor), o el archivo no tiene contenido.
* **`401 Unauthorized`**: El token JWT de sesión ha expirado o el header `X-API-KEY` de las peticiones automáticas de ingesta es inválido.
* **`403 Forbidden`**: Regla Zero-Trust. El RFC del emisor o receptor del XML procesado no coincide con el RFC asignado a ese Tenant en VCore, o el Tenant ha sido inhabilitado administrativamente (`is_active = false`).
* **`422 Unprocessable Entity`**: Error en la estructura del request de FastAPI/Pydantic. Normalmente ocurre al enviar tipos de archivos o formularios incorrectos en endpoints de carga múltiple (`multipart/form-data`).
* **`500 Internal Server Error`**: Falla general. Usualmente se debe a:
  1. Pérdida de conexión con el contenedor de la base de datos (Postgres apagado).
  2. Problemas de permisos de escritura del sistema en el volumen `/app/Operacion_CFDI`.
  Revisa la consola de logs en Coolify para confirmar la traza exacta.

---

## 🧪 Pruebas Rápidas de Diagnóstico Post-Instalación

Para garantizar que el backend y la base de datos se comunican exitosamente tras completar los 3 clics, puedes realizar dos llamadas rápidas vía navegador o curl:

1. **Estado del Servicio (`/ping`)**:
   * **URL**: `http://tu-dominio-o-ip/ping`
   * **Respuesta Esperada**: `"pong"` (confirma que el contenedor backend está vivo).
2. **Inspección de Conexión y Sembrado (`/api/v1/debug/users`)**:
   * **URL**: `http://tu-dominio-o-ip/api/v1/debug/users`
   * **Respuesta Esperada**:
     ```json
     {
       "count": 1,
       "users": [
         {
           "id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
           "username": "admin",
           "is_superadmin": true
         }
       ]
     }
     ```
     *(Esta respuesta confirma que la API se conectó con PostgreSQL, autogeneró las tablas y sembró con éxito al administrador).*
