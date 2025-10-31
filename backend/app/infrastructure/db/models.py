"""
SQLAlchemy ORM модели
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.infrastructure.db.base import Base


# Enums
class UserRole(str, enum.Enum):
    """Роли пользователей"""
    ADMIN = "ADMIN"
    SUPERVISOR = "SUPERVISOR"
    ENGINEER = "ENGINEER"


class ObjectType(str, enum.Enum):
    """Типы объектов"""
    MKD = "MKD"
    HOTEL = "HOTEL"
    CAFE = "CAFE"
    SCHOOL = "SCHOOL"
    HOSPITAL = "HOSPITAL"
    BUSINESS_CENTER = "BUSINESS_CENTER"
    SHOPPING_CENTER = "SHOPPING_CENTER"
    OTHER = "OTHER"


class ObjectStatus(str, enum.Enum):
    """Статусы объектов"""
    NEW = "NEW"
    INTEREST = "INTEREST"
    CALLBACK = "CALLBACK"
    REJECTED = "REJECTED"
    DONE = "DONE"


class VisitStatus(str, enum.Enum):
    """Статусы визитов"""
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    CANCELLED = "CANCELLED"


class InterestType(str, enum.Enum):
    """Типы интересов клиентов"""
    INTERNET = "INTERNET"
    TV = "TV"
    CCTV = "CCTV"
    BABY_MONITOR = "BABY_MONITOR"
    OTHER = "OTHER"


class EntityType(str, enum.Enum):
    """Типы сущностей для комментариев и аудита"""
    OBJECT = "object"
    UNIT = "unit"
    CUSTOMER = "customer"
    VISIT = "visit"


class ActionType(str, enum.Enum):
    """Типы действий для аудита"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"
    LOGIN = "login"
    LOGOUT = "logout"


# Модели
class City(Base):
    """Города (справочник)"""
    __tablename__ = "cities"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class District(Base):
    """Районы (справочник)"""
    __tablename__ = "districts"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    city_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cities.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    city: Mapped["City"] = relationship("City", lazy="selectin")


class User(Base):
    """Пользователи"""
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), nullable=False, default=UserRole.ENGINEER)
    city_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("cities.id"), nullable=True)
    district_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("districts.id"), nullable=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    scopes: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True, default=list)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    city: Mapped[Optional["City"]] = relationship("City", lazy="selectin")
    district: Mapped[Optional["District"]] = relationship("District", lazy="selectin")


class Object(Base):
    """Объекты (здания/места)"""
    __tablename__ = "objects"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type: Mapped[ObjectType] = mapped_column(SQLEnum(ObjectType), nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    
    city_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cities.id"), nullable=False)
    district_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("districts.id"), nullable=True)
    
    gps_lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    gps_lng: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    status: Mapped[ObjectStatus] = mapped_column(SQLEnum(ObjectStatus), default=ObjectStatus.NEW, nullable=False)
    tags: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True, default=list)
    
    responsible_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    contact_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    
    visits_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_visit_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # Для optimistic locking
    
    # Relationships
    city: Mapped["City"] = relationship("City", lazy="selectin")
    district: Mapped[Optional["District"]] = relationship("District", lazy="selectin")
    responsible_user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[responsible_user_id], lazy="selectin")
    
    # Индексы
    __table_args__ = (
        Index("ix_objects_city_id", "city_id"),
        Index("ix_objects_district_id", "district_id"),
        Index("ix_objects_status", "status"),
        Index("ix_objects_city_status", "city_id", "status"),
        Index("ix_objects_updated_at", "updated_at"),
        Index("ix_objects_responsible_user", "responsible_user_id"),
        Index("ix_objects_version", "version"),
        Index("ix_objects_last_visit_at", "last_visit_at"),
        Index("ix_objects_gps", "gps_lat", "gps_lng"),  # Для гео-поиска (в Postgres будет GIST)
        Index("ix_objects_contact_phone", "contact_phone"),
    )


class Unit(Base):
    """Единицы (квартиры/помещения)"""
    __tablename__ = "units"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    object_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("objects.id"), nullable=False)
    unit_number: Mapped[str] = mapped_column(String(50), nullable=False)
    floor: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    entrance: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    attributes: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    object: Mapped["Object"] = relationship("Object", lazy="selectin")
    
    # Индексы
    __table_args__ = (
        Index("ix_units_object_id", "object_id"),
    )


class Customer(Base):
    """Клиенты"""
    __tablename__ = "customers"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    object_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("objects.id"), nullable=False)
    unit_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("units.id"), nullable=True)
    
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, unique=True, index=True)  # UNIQUE для быстрого поиска
    portrait_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    current_provider: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    provider_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-5
    satisfied: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    
    interests: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True, default=list)  # InterestType enum values
    preferred_call_time: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # HH:MM format
    desired_price: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    gdpr_consent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    last_interaction_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    object: Mapped["Object"] = relationship("Object", lazy="selectin")
    unit: Mapped[Optional["Unit"]] = relationship("Unit", lazy="selectin")
    
    # Индексы
    __table_args__ = (
        Index("ix_customers_object_id", "object_id"),
        Index("ix_customers_unit_id", "unit_id"),
        Index("ix_customers_updated_at", "updated_at"),
    )


class Visit(Base):
    """Визиты"""
    __tablename__ = "visits"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    object_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("objects.id"), nullable=False)
    unit_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("units.id"), nullable=True)
    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True)
    
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    engineer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    status: Mapped[VisitStatus] = mapped_column(SQLEnum(VisitStatus), default=VisitStatus.PLANNED, nullable=False)
    
    interests: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True, default=list)
    outcome_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    next_action_due_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    geo_captured_lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    geo_captured_lng: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    object: Mapped["Object"] = relationship("Object", lazy="selectin")
    unit: Mapped[Optional["Unit"]] = relationship("Unit", lazy="selectin")
    customer: Mapped[Optional["Customer"]] = relationship("Customer", lazy="selectin")
    engineer: Mapped["User"] = relationship("User", lazy="selectin")
    
    # Индексы
    __table_args__ = (
        Index("ix_visits_engineer_id", "engineer_id"),
        Index("ix_visits_object_id", "object_id"),
        Index("ix_visits_status", "status"),
        Index("ix_visits_scheduled_at", "scheduled_at"),
        Index("ix_visits_finished_at", "finished_at"),
        Index("ix_visits_engineer_scheduled", "engineer_id", "scheduled_at"),
        Index("ix_visits_object_status", "object_id", "status"),
        Index("ix_visits_version", "version"),
        Index("ix_visits_next_action_due_at", "next_action_due_at"),  # Для выборок "к прозвону"
    )


class Comment(Base):
    """Комментарии"""
    __tablename__ = "comments"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type: Mapped[EntityType] = mapped_column(SQLEnum(EntityType), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    
    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    attachments: Mapped[Optional[list[uuid.UUID]]] = mapped_column(JSON, nullable=True)  # Attachment IDs
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    author: Mapped["User"] = relationship("User", lazy="selectin")


class Attachment(Base):
    """Вложения (файлы)"""
    __tablename__ = "attachments"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bucket: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    
    entity_type: Mapped[Optional[EntityType]] = mapped_column(SQLEnum(EntityType), nullable=True)
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    creator: Mapped["User"] = relationship("User", lazy="selectin")


class ReportJob(Base):
    """Задачи экспорта отчётов"""
    __tablename__ = "report_jobs"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    entity: Mapped[str] = mapped_column(String(50), nullable=False)  # objects, visits, customers
    filters_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    columns: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)
    sort: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)  # pending, processing, done, failed
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    rq_job_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    owner: Mapped["User"] = relationship("User", lazy="selectin")
    
    # Индексы
    __table_args__ = (
        Index("ix_report_job_owner_created", "owner_id", "created_at"),
        Index("ix_report_job_status_created", "status", "created_at"),
    )


class AuditLog(Base):
    """Лог аудита"""
    __tablename__ = "audit_logs"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action: Mapped[ActionType] = mapped_column(SQLEnum(ActionType), nullable=False)
    entity_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    
    before_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    after_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    actor: Mapped[Optional["User"]] = relationship("User", lazy="selectin")
    
    # Индексы
    __table_args__ = (
        Index("ix_audit_entity_type_id_date", "entity_type", "entity_id", "occurred_at"),
        Index("ix_audit_actor_date", "actor_id", "occurred_at"),
    )


class SyncToken(Base):
    """Токены для офлайн-синхронизации"""
    __tablename__ = "sync_tokens"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_generated_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), unique=True, nullable=False, index=True)
    table_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    server_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    checksum: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="synced", nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Индексы
    __table_args__ = (
        Index("ix_sync_token_table_seen", "table_name", "last_seen_at"),
    )
