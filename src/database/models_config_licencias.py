from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, Date, CheckConstraint, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
import uuid

Base = declarative_base()

class CatEntity(Base):
    """
    Catálogo de Entidades (Reemplaza al CatEntity del Legacy)
    Soporta el esquema de licenciamiento.
    """
    __tablename__ = "cat_entities"
    
    entity_id = Column(Integer, primary_key=True, autoincrement=True)
    rfc = Column(String(13), unique=True, nullable=False)
    business_name = Column(String(200), nullable=False)
    is_legal_person = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    
    # Control de Licenciamiento
    # ('1_MES', '3_MESES', '1_ANIO')
    license_tier = Column(String(20))
    license_issue_date = Column(Date, nullable=False, server_default=func.current_date())
    license_expiration_date = Column(Date, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "license_tier IN ('1_MES', '3_MESES', '1_ANIO')",
            name="check_license_tier"
        ),
    )

    memberships = relationship("SysUserRole", back_populates="entity", cascade="all, delete-orphan")


class SysUser(Base):
    """
    Tabla de Usuarios (Reemplaza a Scisa_User)
    Contiene los campos para Edición y Deshabilitación.
    """
    __tablename__ = "sys_users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(150), nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(150))
    
    is_active = Column(Boolean, default=True)
    login_attempts = Column(Integer, default=0)
    last_login = Column(DateTime)
    
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    memberships = relationship("SysUserRole", back_populates="user", cascade="all, delete-orphan")


class SysUserRole(Base):
    """
    Relación Usuario-Entidad y Roles (Reemplaza a Scisa_UsersRoles)
    """
    __tablename__ = "sys_user_roles"
    
    membership_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("sys_users.user_id", ondelete="CASCADE"), nullable=False)
    entity_id = Column(Integer, ForeignKey("cat_entities.entity_id", ondelete="CASCADE"), nullable=False)
    role_name = Column(String(50), nullable=False) # Ej: 'ADMIN', 'OPERADOR'

    user = relationship("SysUser", back_populates="memberships")
    entity = relationship("CatEntity", back_populates="memberships")

    __table_args__ = (
        UniqueConstraint('user_id', 'entity_id', name='uix_user_entity'),
    )

