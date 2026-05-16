# 📜 CHANGELOG v5.0.0 (VCORE INTEGRATED)

Historial de cambios críticos y mejoras estructurales bajo la Directiva L6.

## [v5.0.0] - Patch: SENTINEL TIMEOUT (L6 v3.5)
*Fecha: 2026-04-03*

### 🚀 Mejoras de Seguridad
- **Sentinel Activity Monitor**: Sistema dinámico para monitorear la inactividad del usuario en el frontend (`sentinel.js`).
- **Gobernanza por Inactividad**: Cierre de sesión automático (15 mins) y vida máxima de sesión (30 mins) configurable vía `.env`.
- **Limpieza de Estado Post-Logout**: Ahora el logout forzado por Sentinel asegura que la limpieza de `localStorage` sea total (Token y X-Entidad-ID).

### 🔑 Recuperación de Acceso (Motor Atómico)
- **Email Tokenization Core**: Implementada la tabla `auth_recovery_tokens` para gestión de tokens atómicos de 1 hora.
- **Validación Contra SQL**: Los tokens se validan estrictamente contra la base de datos antes de permitir cambios de contraseña.
- **Secure BCrypt Persistence**: Hashing de contraseñas de recuperación bajo estándar industrial.
- **Integración SMTP Multi-tenant**: El motor de recuperación utiliza el servidor SMTP de la entidad o el fallback configurado.

### 🎨 Mejoras de UX (v3.6 Anti-Freeze)
- **Fluidez Post-Envío (Recovery)**: 
    - Botón de recuperación dinámico (cambia a verde con icono check al éxito).
    - Redirección automática al `/login` tras 4 segundos del envío exitoso.
    - Feedback visual de "Solicitud Recibida" con animación de pulso.

### 🛠️ Configuración de Servidor
- **VCore Integrated Manager**: El servidor ahora se gestiona mediante `vcore_manager.py`, automatizando el reinicio de servicios (Engine + Dashboard).
- **Consistencia de DB**: Sincronización de esquema SQL para nuevas tablas de seguridad.
