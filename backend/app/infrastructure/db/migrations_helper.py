"""
Вспомогательные функции для работы с миграциями
"""
from sqlalchemy import Index
from app.infrastructure.db.models import (
    Object, Visit, Customer, Unit, AuditLog, SyncToken, ReportJob
)


def get_all_indexes_info() -> dict[str, list[dict]]:
    """Получить информацию о всех индексах для документации"""
    
    indexes_info = {
        "objects": [
            {"name": "ix_objects_city_id", "fields": ["city_id"], "purpose": "Фильтрация по городу"},
            {"name": "ix_objects_district_id", "fields": ["district_id"], "purpose": "Фильтрация по району"},
            {"name": "ix_objects_status", "fields": ["status"], "purpose": "Фильтрация по статусу"},
            {"name": "ix_objects_city_status", "fields": ["city_id", "status"], "purpose": "Составной для частых запросов"},
            {"name": "ix_objects_updated_at", "fields": ["updated_at"], "purpose": "Сортировка и диапазоны"},
            {"name": "ix_objects_last_visit_at", "fields": ["last_visit_at"], "purpose": "Выборки по периоду визитов"},
            {"name": "ix_objects_responsible_user", "fields": ["responsible_user_id"], "purpose": "Фильтрация по ответственному"},
            {"name": "ix_objects_version", "fields": ["version"], "purpose": "Оптимистические блокировки"},
            {"name": "ix_objects_gps", "fields": ["gps_lat", "gps_lng"], "purpose": "Гео-поиск"},
        ],
        "visits": [
            {"name": "ix_visits_engineer_id", "fields": ["engineer_id"], "purpose": "Фильтрация по инженеру"},
            {"name": "ix_visits_object_id", "fields": ["object_id"], "purpose": "Фильтрация по объекту"},
            {"name": "ix_visits_status", "fields": ["status"], "purpose": "Фильтрация по статусу"},
            {"name": "ix_visits_scheduled_at", "fields": ["scheduled_at"], "purpose": "Диапазоны планирования"},
            {"name": "ix_visits_finished_at", "fields": ["finished_at"], "purpose": "Диапазоны завершения"},
            {"name": "ix_visits_next_action_due_at", "fields": ["next_action_due_at"], "purpose": "Выборки 'к прозвону'"},
            {"name": "ix_visits_engineer_scheduled", "fields": ["engineer_id", "scheduled_at"], "purpose": "Маршруты инженера"},
            {"name": "ix_visits_object_status", "fields": ["object_id", "status"], "purpose": "Визиты объекта по статусу"},
            {"name": "ix_visits_version", "fields": ["version"], "purpose": "Проверки конфликтов"},
        ],
        "customers": [
            {"name": "uq_customer_phone", "fields": ["phone"], "purpose": "UNIQUE - быстрый поиск по телефону"},
            {"name": "ix_customers_object_id", "fields": ["object_id"], "purpose": "Фильтрация по объекту"},
            {"name": "ix_customers_unit_id", "fields": ["unit_id"], "purpose": "Фильтрация по квартире"},
            {"name": "ix_customers_updated_at", "fields": ["updated_at"], "purpose": "Сортировка и диапазоны"},
        ],
        "audit_logs": [
            {"name": "ix_audit_entity_type_id_date", "fields": ["entity_type", "entity_id", "occurred_at"], "purpose": "История изменений сущности"},
            {"name": "ix_audit_actor_date", "fields": ["actor_id", "occurred_at"], "purpose": "Действия пользователя"},
            {"name": "ix_audit_occurred_at", "fields": ["occurred_at"], "purpose": "Диапазоны дат (через index=True)"},
        ],
        "sync_tokens": [
            {"name": "uq_sync_token_client_id", "fields": ["client_generated_id"], "purpose": "UNIQUE - идемпотентность"},
            {"name": "ix_sync_token_table_seen", "fields": ["table_name", "last_seen_at"], "purpose": "Очистка старых токенов"},
            {"name": "ix_sync_token_server_id", "fields": ["server_id"], "purpose": "Поиск по серверному ID"},
        ],
        "report_jobs": [
            {"name": "ix_report_job_owner_created", "fields": ["owner_id", "created_at"], "purpose": "История задач пользователя"},
            {"name": "ix_report_job_status_created", "fields": ["status", "created_at"], "purpose": "Поиск pending/processing задач"},
        ],
    }
    
    return indexes_info

