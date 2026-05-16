# 🛡️ GESTIÓN DE CUENTA SEMILLA (SUPER ADMIN ROOT)

La "Cuenta Semilla" es el núcleo de identidad inicial de VCore v5.0.0. Es la única cuenta inyectada directamente durante el despliegue de la base de datos que posee permisos de **Global Governance**.

## 🔑 Especificaciones de la Cuenta

- **Nivel**: Super Admin Root.
- **Usuario por Defecto**: `admin` (o el RFC máster de Vantec).
- **Password Inicial**: `Vantec2026@Core!` (Consulte su hoja de despliegue para la enviada en producción).
- **Función**:
  - Iniciar el ecosistema multi-tenant.
  - Creación de **Entidades (Tenants)**.
  - Asignación de **Administradores de Empresa**.
  - Configuración global del servidor SMTP para notificaciones de recuperación.

## 🔒 Proceso de Seguridad Industrial (Hardening)

Es **OBLIGATORIO** seguir el protocolo de "Primer Ingreso":

1. **Acceso Inicial**: Ingresar con las credenciales semilla.
2. **Cambio Forzado**: El sistema solicitará inmediatamente un cambio de contraseña por razones de seguridad industrial.
3. **Cifrado BCrypt**: La nueva clave se almacena bajo el estándar de hashing BCrypt 12 rounds.
4. **Resguardo de Llave**: La contraseña root no es recuperable mediante el proceso estándar de "pérdida de contraseña" (ya que no hay un nivel superior que la autorice), por lo que debe ser resguardada físicamente en la bóveda de la empresa.

> [!CAUTION]
> La pérdida del acceso Seed Account requiere intervención directa en la base de datos SQL para resetear el hash, lo cual genera alertas extremas en la Bitácora de Auditoría L6.
