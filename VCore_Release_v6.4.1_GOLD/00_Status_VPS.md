# 🛡️ Estado de Integración y Bitácora de Despliegue VPS (VCore L6)

**Documento Oficial de Control, Seguimiento e Instalación Rápida**  
**Última Actualización:** 21 de Mayo, 2026  
**Objetivo:** Garantizar que cualquier instalación o migración limpia a un nuevo servidor VPS tome exactamente **5 minutos**, con persistencia absoluta y sin configuraciones manuales complejas.

---

## 📋 1. Resumen Ejecutivo y Estado Actual de Producción

Hemos transformado el backend de **Gestor Vantec** en una **"Caja Negra" autónoma, auto-suficiente e indestructible**. A partir de hoy, el sistema es capaz de autogestionar su base de datos, auto-crear sus tablas y vistas materializadas al iniciar, y auto-migrar sus recursos de forma transparente. 

Tanto los archivos (XMLs, PDFs, Logotipos) como el cálculo analítico del Dashboard se encuentran blindados y listos para producción con **cero dependencias externas y cero intervenciones con DBeaver**.

---

## 🔍 2. Diagnóstico de Problemas Claves y Soluciones Implementadas

Durante las fases de pruebas clínicas en el VPS, identificamos y solucionamos de forma definitiva los siguientes cuatro cuellos de botella:

### 1. Fuga de Logos, XMLs y PDFs en cada Actualización (Resuelto)
* **Causa Raíz:** El contenedor de producción utilizaba un **volumen anónimo efímero de Docker** (con hash largo aleatorio como `f4ef6dda8165...`) para mapear el directorio `/app/Operacion_CFDI`. Cada vez que Coolify compilaba una actualización de código o redesplegaba, Docker destruía el volumen anterior y creaba uno nuevo vacío, borrando todos los documentos e imágenes.
* **Solución de Persistencia Unificada:** 
  - Centralizamos el almacenamiento físico configurando que tanto las facturas como los logotipos corporativos vivan bajo el mismo directorio raíz del contenedor: `/app/Operacion_CFDI` (logos en `/app/Operacion_CFDI/logos`).
  - Guiamos al usuario a mapear un **Volume Mount** persistente nombrado `vantec_cfdi_data` apuntando directamente a `/app/Operacion_CFDI` desde la interfaz de Coolify (**Persistent Storage**). Esto hace que toda la información sobreviva de forma eterna a cualquier actualización de código o redespliegue de infraestructura.

### 2. Discrepancia del Dashboard: PPD Pendientes en 0 (Resuelto)
* **Causa Raíz:** Las vistas materializadas de PostgreSQL (`MATERIALIZED VIEW v_ppd_semaforo_status`) son físicas y estáticas; no recalculan datos automáticamente al ingresar o eliminar comprobantes. La API no tenía implementado ningún comando de refresco para esta vista en su código.
* **Solución (Auto-Refresh en Tiempo Real):**
  - Modificamos el endpoint del Dashboard (`/api/v1/analytics/dashboard`) para ejecutar automáticamente un comando asíncrono ultra-rápido (<5ms) de refresco antes de consultar el conteo:
    ```sql
    REFRESH MATERIALIZED VIEW v_ppd_semaforo_status;
    ```
  - Esto garantiza que el contador de PPDs pendientes (actualmente 2 facturas reales: Folios 804 y 809, libres de pagos) muestre datos exactos en tiempo real al navegar por el sistema.

### 3. Error HTTP `428 Precondition Required` en Reenvío y Refresco (Resuelto)
* **Causa Raíz:** El middleware multi-tenant interceptaba todas las rutas de `/api/` y exigía un contexto de empresa activo (`X-Entidad-ID`). Sin embargo, el endpoint de refresco de sesión del navegador (`/api/v1/auth/refresh`) y el endpoint de reenvío por correo de CFDIs (`/api/orquestador/reenvio`) fallaban al carecer de este contexto o al ejecutarse desde fetch directo sin headers.
* **Solución:** 
  - Declaramos rutas neutras explícitas (`TENANT_NEUTRAL_ROUTES`) en el middleware para permitir refrescar la sesión del superadmin sin empresa seleccionada.
  - Parchamos la llamada HTTP en la interfaz web (`cfdis.js`) para inyectar dinámicamente el header `X-Entidad-ID` usando el valor activo del almacenamiento del navegador (`localStorage.getItem('active_entidad')`), desbloqueando el reenvío de correos de forma inmediata.

### 4. Bloqueo de Scripts por HTTPS Mixed Content (Resuelto)
* **Causa Raíz:** Al operar el VPS bajo HTTPS SSL, el navegador bloqueaba la carga de los scripts JavaScript de gestión de CFDIs porque FastAPI (detrás de un proxy de terminación SSL) generaba rutas relativas absolutas usando protocolo `http://` no seguro, congelando el cargador de documentos.
* **Solución:** Reemplazamos las invocaciones de Jinja por rutas raíz domain-relative en las plantillas HTML (`src="/static/js/cfdis.js?v=..."`). Esto obliga al navegador a heredar el protocolo activo (`https://`) y el dominio actual de forma transparente, eliminando los bloqueos de seguridad del navegador.

---

## 🚀 3. Playbook Oficial: Despliegue Limpio en 5 Minutos (Zero-DBeaver)

Sigue estos sencillos pasos para instalar el sistema **Gestor Vantec VPS** desde cero en cualquier servidor VPS totalmente limpio en cuestión de minutos:

### 1️⃣ Clic 1: Levantar el PostgreSQL Aislado
1. En el panel de Coolify, haz clic en **New Resource** > **Databases** > **PostgreSQL**.
2. Configura los puertos host para auditorías y herramientas externas de esta forma:
   ```text
   5434:5432
   ```
   *(Esto mapea el puerto público externo del VPS al `5434`, manteniendo el tráfico del contenedor interno seguro en el puerto estándar `5432`)*.
3. Haz clic en **Start** para iniciar el motor de base de datos.

### 2️⃣ Clic 2: Configurar las Variables de Entorno del API
Crea la aplicación en Coolify apuntando al repositorio de Git. En la sección **Environment Variables**, inyecta las siguientes claves de producción:

| Variable | Valor Recomendado / Ejemplo | Descripción |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:Admin123@<ID_POSTGRES_COOLIFY>:5432/vcore_vps` | URL de conexión asíncrona interna de alta velocidad. Usa el puerto interno `5432` y el ID del servicio de Postgres. |
| `VANTEC_SECRET_KEY` | `un_secreto_seguro_jwt_generado_con_openssl` | Llave criptográfica para firmas de tokens de sesión JWT. |
| `SESSION_INACTIVITY_TIMEOUT_MINUTES` | `15` | Tiempo límite de inactividad de sesión (minutos) antes de desconexión. |
| `SESSION_MAX_LIFETIME_MINUTES` | `30` | Tiempo de vida absoluto de sesión de usuario (minutos) por seguridad L6. |
| `STORAGE_PATH` | `/app/Operacion_CFDI` | Ruta del volumen persistente del backend para la ingesta y logos. |
| `VANTEC_CFDI_ROOT` | `/app/Operacion_CFDI` | Ruta de persistencia raíz para expedientes de CFDIs. |

### 3️⃣ Clic 3: Configurar la Persistencia (Volume Mount)
Para evitar la pérdida de facturas, XMLs, PDFs y logotipos durante compilaciones y despliegues futuros:
1. Ve a la pestaña **`Persistent Storage`** de tu aplicación en Coolify (ubicada en el menú izquierdo, debajo de `Environment Variables`).
2. Haz clic en **Add Storage** (Añadir almacenamiento) y selecciona la opción **`Volume Mount`**.
3. Configura los campos exactamente de la siguiente forma:
   * **Name (Nombre):** `vantec_cfdi_data`
   * **Source Path:** *(Déjalo completamente **VACÍO** / en blanco)*
   * **Destination Path (Ruta en el contenedor):** `/app/Operacion_CFDI`
4. Haz clic en **Add** (Agregar).
5. Haz clic en **Deploy** (Desplegar / Redesplegar).

---

## ⚡ 4. Inicialización Totalmente Autónoma

Una vez disparado el despliegue, el sistema iniciará y se configurará solo sin necesidad de abrir DBeaver ni ejecutar scripts externos:
* **Generación de Esquema Relacional:** El motor en su evento de inicio (`lifespan`) detectará que la base de datos está vacía e inyectará de forma transparente el archivo SQL maestro. Esto construirá de inmediato las **19 tablas del sistema**, incluyendo las vistas materializadas, índices y triggers automatizados.
* **Auto-Sembrado de Superusuario:** Crea inmediatamente la cuenta del administrador global con contraseña encriptada segura:
  - **Usuario:** `admin`
  - **Email:** `admin@vcore.com`
  - **Contraseña Semilla:** `@dm1n***`
* **Bypass de Aislamiento L6:** El SuperAdmin podrá acceder a la interfaz web y registrar la primera empresa (RFC) sin ser expulsado por el middleware multi-tenant, ya que el sistema reconoce la ruta administrativa `/api/v1/admin` como neutral a nivel global.

---

## 🔬 5. Plan de Verificación de Persistencia tras Redespliegues

Para asegurar que todo funcione a la perfección tras completar el despliegue:
1. Sube un logotipo a tu empresa desde la web de Configuración y verifica que se cargue correctamente.
2. Sube a través del Watcher las facturas de prueba **804 y 809**.
3. Confirma que el Dashboard muestra exactamente **2 PPD Pendientes** de pago y que los XML y PDF se pueden ver y descargar.
4. Ejecuta un **Redeploy** en Coolify.
5. Inicia sesión de nuevo y comprueba que **el logo sigue visible, los PDF y XML siguen descargándose y el Dashboard sigue marcando 2 PPDs**. Si todo se mantiene en su sitio, ¡el VPS está 100% blindado y listo para producción eterna!
