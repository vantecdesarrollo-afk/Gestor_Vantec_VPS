# 🛡️ Manual de Instalación Técnica - Vantec VCORE (v4.5)

Este documento detalla el procedimiento de despliegue del ecosistema **Vantec VCore** en servidores locales bajo el **Estándar de Oro**.

---

## 🏗️ 1. Requisitos del Sistema
- **S.O:** Windows 10/Server 2019+
- **Python:** 3.9+ (Agregado al PATH)
- **Base de Datos:** PostgreSQL 13+
- **Memoria:** 8GB RAM (Mínimo para procesamiento masivo de $2.5M)

---

## 🚀 2. Instalación en 3 Pasos (Clic y Listo)

1.  **Clonación:** Extraer el paquete de software en la raíz del disco duro (Ej: `C:\Vantec_VCore`).
2.  **Ejecución:** Hacer doble clic en `install_vcore.bat`.
    -   Este script instalará las dependencias vía `pip`.
    -   Creará automáticamente la estructura operativa en `Operacion_CFDI`.
3.  **Base de Datos:** Cuando el instalador lo solicite, presione **'S'** para inicializar los esquemas SQL (`init_schema.sql` e `init_schema_vantec_v2.sql`).

---

## ⚙️ 3. Configuración de Entorno (.env)
Cree o edite el archivo `.env` en la raíz con las siguientes variables:

```ini
# Configuración de Base de Datos
DATABASE_URL=postgresql+asyncpg://postgres:prueba01@localhost:5432/gestor_cfdi

# Rutas de Operación (Dinámicas v4.5)
# No requiere rutas absolutas de desarrollo
VANTEC_CFDI_ROOT=./Operacion_CFDI/Files
```

---

## 💓 4. Puesta en Marcha
Para iniciar el sistema integral (Motor + Dashboard), ejecute el gestor de procesos:
```powershell
python vcore_manager.py
```
El sistema reportará un `HEARTBEAT` cada 5 minutos en el archivo `vcore_manager_err.log`.

---

**Soporte Técnico VCORE**
*Garantía de Disponibilidad 99.9%*
🏁 **ESTÁNDAR DE ORO v4.5 ACTIVO**
