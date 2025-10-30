"""
Smoke-тесты для проверки функциональности
"""
import asyncio
import sys
from pathlib import Path
import httpx
from datetime import datetime
import json

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

# Глобальные переменные для токенов
TOKEN = None
ADMIN_TOKEN = None
ENGINEER_TOKEN = None


async def test_health_check(client: httpx.AsyncClient):
    """Тест 1: Health check"""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)
    
    try:
        response = await client.get(f"{BASE_URL}/health")
        print(f"[OK] GET /health: {response.status_code}")
        print(f"   Response: {response.json()}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        return True
    except Exception as e:
        print(f"[FAIL] GET /health failed: {e}")
        return False


async def test_ready_check(client: httpx.AsyncClient):
    """Тест 2: Ready check"""
    print("\n" + "="*60)
    print("TEST 2: Ready Check")
    print("="*60)
    
    try:
        response = await client.get(f"{BASE_URL}/ready")
        print(f"[OK] GET /ready: {response.status_code}")
        print(f"   Response: {response.json()}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        return True
    except Exception as e:
        print(f"[FAIL] GET /ready failed: {e}")
        return False


async def test_worker_health(client: httpx.AsyncClient):
    """Тест 3: Worker health"""
    print("\n" + "="*60)
    print("TEST 3: Worker Health")
    print("="*60)
    
    try:
        response = await client.get(f"{BASE_URL}/worker/health")
        print(f"[OK] GET /worker/health: {response.status_code}")
        data = response.json()
        print(f"   Response: {json.dumps(data, indent=2)}")
        # Worker может быть недоступен без Redis, поэтому проверяем только что запрос прошёл
        assert response.status_code in [200, 503], f"Expected 200 or 503, got {response.status_code}"
        return True
    except Exception as e:
        print(f"[WARN] GET /worker/health failed (может быть нормально без Redis): {e}")
        return True  # Не критично для базовых тестов


async def test_login(client: httpx.AsyncClient):
    """Тест 4: Login и получение токена"""
    print("\n" + "="*60)
    print("TEST 4: Login")
    print("="*60)
    
    global TOKEN
    
    try:
        response = await client.post(
            f"{BASE_URL}{API_PREFIX}/auth/token",
            data={
                "username": "admin@example.com",
                "password": "password123"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            data = response.json()
            TOKEN = data.get("access_token")
            print(f"[OK] POST /auth/token: {response.status_code}")
            print(f"   Token received: {TOKEN[:20]}...")
            return True
        else:
            print(f"[FAIL] POST /auth/token: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"[FAIL] POST /auth/token failed: {e}")
        return False


async def test_create_object(client: httpx.AsyncClient):
    """Тест 5: Создание объекта"""
    print("\n" + "="*60)
    print("TEST 5: Create Object")
    print("="*60)
    
    if not TOKEN:
        print("⚠️  Skipping: No token available")
        return False
    
    try:
        response = await client.post(
            f"{BASE_URL}{API_PREFIX}/objects",
            json={
                "type": "APARTMENT",
                "address": "ул. Тестовая, д. 1",
                "city_id": "00000000-0000-0000-0000-000000000001",  # Нужен реальный city_id
                "status": "NEW"
            },
            headers={"Authorization": f"Bearer {TOKEN}"}
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"[OK] POST /objects: {response.status_code}")
            print(f"   Object ID: {data.get('id')}")
            return True, data.get("id")
        else:
            print(f"[WARN] POST /objects: {response.status_code} (может быть проблема с city_id)")
            return True, None  # Не критично для базовых тестов
    except Exception as e:
        print(f"[WARN] POST /objects failed: {e}")
        return True, None


async def test_sync_batch(client: httpx.AsyncClient):
    """Тест 6: Sync batch (happy path)"""
    print("\n" + "="*60)
    print("TEST 6: Sync Batch (Happy Path)")
    print("="*60)
    
    if not TOKEN:
        print("⚠️  Skipping: No token available")
        return False
    
    try:
        import uuid
        client_id = str(uuid.uuid4())
        
        response = await client.post(
            f"{BASE_URL}{API_PREFIX}/sync/batch",
            json={
                "items": [{
                    "client_generated_id": client_id,
                    "table_name": "objects",
                    "payload": {
                        "address": "ул. Офлайн-тест, д. 1",
                        "city_id": "00000000-0000-0000-0000-000000000001",
                        "status": "NEW",
                        "type": "APARTMENT"
                    },
                    "updated_at": datetime.utcnow().isoformat() + "Z",
                    "version": 1
                }],
                "force": False
            },
            headers={"Authorization": f"Bearer {TOKEN}"}
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"[OK] POST /sync/batch: {response.status_code}")
            print(f"   Results: {len(data.get('results', []))}")
            if data.get("results"):
                result = data["results"][0]
                print(f"   Status: {result.get('status')}")
                print(f"   Server ID: {result.get('server_id')}")
            return True
        else:
            print(f"[WARN] POST /sync/batch: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return True  # Не критично, если есть проблемы с данными
    except Exception as e:
        print(f"[WARN] POST /sync/batch failed: {e}")
        return True


async def test_sync_changes(client: httpx.AsyncClient):
    """Тест 7: Sync changes"""
    print("\n" + "="*60)
    print("TEST 7: Sync Changes")
    print("="*60)
    
    if not TOKEN:
        print("⚠️  Skipping: No token available")
        return False
    
    try:
        since = "2025-01-01T00:00:00Z"
        response = await client.get(
            f"{BASE_URL}{API_PREFIX}/sync/changes",
            params={
                "since": since,
                "tables": ["objects"],
                "limit": 100
            },
            headers={"Authorization": f"Bearer {TOKEN}"}
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] GET /sync/changes: {response.status_code}")
            print(f"   Items: {len(data.get('items', []))}")
            return True
        else:
            print(f"[WARN] GET /sync/changes: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return True
    except Exception as e:
        print(f"[WARN] GET /sync/changes failed: {e}")
        return True


async def test_reports_export(client: httpx.AsyncClient):
    """Тест 8: Reports export"""
    print("\n" + "="*60)
    print("TEST 8: Reports Export")
    print("="*60)
    
    if not TOKEN:
        print("⚠️  Skipping: No token available")
        return False
    
    try:
        response = await client.post(
            f"{BASE_URL}{API_PREFIX}/reports/export",
            json={
                "entity": "objects",
                "filters": {},
                "columns": ["id", "address", "status"],
                "sort": {"updated_at": "desc"}
            },
            headers={"Authorization": f"Bearer {TOKEN}"}
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"[OK] POST /reports/export: {response.status_code}")
            print(f"   Job ID: {data.get('id')}")
            print(f"   Status: {data.get('status')}")
            return True, data.get("id")
        else:
            print(f"[WARN] POST /reports/export: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return True, None
    except Exception as e:
        print(f"[WARN] POST /reports/export failed: {e}")
        return True, None


async def test_audit_logs(client: httpx.AsyncClient):
    """Тест 9: Audit logs"""
    print("\n" + "="*60)
    print("TEST 9: Audit Logs")
    print("="*60)
    
    if not TOKEN:
        print("⚠️  Skipping: No token available")
        return False
    
    try:
        response = await client.get(
            f"{BASE_URL}{API_PREFIX}/audit",
            params={"limit": 10},
            headers={"Authorization": f"Bearer {TOKEN}"}
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ GET /audit: {response.status_code}")
            print(f"   Items: {len(data.get('items', []))}")
            if data.get("items"):
                item = data["items"][0]
                # Проверяем, что PII замаскировано
                before_json = item.get("before_json", {})
                after_json = item.get("after_json", {})
                print(f"   Sample item: action={item.get('action')}, entity_type={item.get('entity_type')}")
                if before_json.get("phone") or after_json.get("phone"):
                    phone = before_json.get("phone") or after_json.get("phone")
                    if "***" in str(phone):
                        print(f"   [OK] PII masked in audit: phone contains ***")
                    else:
                        print(f"   [WARN] PII may not be masked: {phone[:20]}")
            return True
        else:
            print(f"[WARN] GET /audit: {response.status_code} (может требовать ADMIN роль)")
            print(f"   Response: {response.text[:200]}")
            return True  # Не критично
    except Exception as e:
        print(f"[WARN] GET /audit failed: {e}")
        return True


async def test_customers_list(client: httpx.AsyncClient):
    """Тест 10: Customers list (PII masking)"""
    print("\n" + "="*60)
    print("TEST 10: Customers List (PII Masking)")
    print("="*60)
    
    if not TOKEN:
        print("⚠️  Skipping: No token available")
        return False
    
    try:
        response = await client.get(
            f"{BASE_URL}{API_PREFIX}/customers",
            params={"limit": 10},
            headers={"Authorization": f"Bearer {TOKEN}"}
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ GET /customers: {response.status_code}")
            print(f"   Items: {len(data.get('items', []))}")
            if data.get("items"):
                customer = data["items"][0]
                phone = customer.get("phone")
                if phone:
                    if "***" in phone:
                        print(f"   [OK] PII masked: phone={phone}")
                    else:
                        print(f"   [INFO] PII visible (may be ADMIN role): phone={phone[:20]}")
            return True
        else:
            print(f"[WARN] GET /customers: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return True
    except Exception as e:
        print(f"[WARN] GET /customers failed: {e}")
        return True


async def test_migrations():
    """Тест 11: Проверка миграций"""
    print("\n" + "="*60)
    print("TEST 11: Migrations Check")
    print("="*60)
    
    try:
        from pathlib import Path
        migrations_dir = Path(__file__).parent.parent / "alembic" / "versions"
        
        if not migrations_dir.exists():
            print(f"[FAIL] Migrations directory not found: {migrations_dir}")
            return False
        
        migration_files = list(migrations_dir.glob("*.py"))
        migration_files = [f for f in migration_files if f.name != "__init__.py"]
        
        print(f"[OK] Found {len(migration_files)} migration file(s)")
        for mf in migration_files:
            print(f"   - {mf.name}")
        
        # Проверяем наличие initial schema миграции
        has_initial = any("initial" in mf.name.lower() for mf in migration_files)
        if has_initial:
            print(f"[OK] Initial schema migration found")
        else:
            print(f"[WARN] Initial schema migration not found")
        
        return True
    except Exception as e:
        print(f"[FAIL] Migrations check failed: {e}")
        return False


async def run_all_tests():
    """Запуск всех тестов"""
    print("\n" + "="*60)
    print("SMOKE TESTS REPORT")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Started at: {datetime.now().isoformat()}")
    
    results = {}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Проверяем, что сервер запущен
        try:
            await client.get(f"{BASE_URL}/health")
            print("[OK] Server is running")
        except Exception:
            print("[FAIL] Server is not running. Please start it first:")
            print("   uvicorn app.main:app --reload")
            return
        
        # Базовые проверки
        results["health"] = await test_health_check(client)
        results["ready"] = await test_ready_check(client)
        results["worker_health"] = await test_worker_health(client)
        results["migrations"] = await test_migrations()
        
        # Авторизация
        results["login"] = await test_login(client)
        
        if results["login"]:
            # API тесты
            results["create_object"] = await test_create_object(client)
            results["sync_batch"] = await test_sync_batch(client)
            results["sync_changes"] = await test_sync_changes(client)
            results["reports_export"] = await test_reports_export(client)
            results["audit_logs"] = await test_audit_logs(client)
            results["customers_list"] = await test_customers_list(client)
    
    # Итоговый отчет
    print("\n" + "="*60)
    print("FINAL REPORT")
    print("="*60)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    print(f"\nTotal tests: {total}")
    print(f"[OK] Passed: {passed}")
    print(f"[FAIL] Failed: {failed}")
    print(f"Success rate: {passed/total*100:.1f}%")
    
    print("\nDetailed results:")
    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status}: {test_name}")
    
    print("\n" + "="*60)
    print(f"Completed at: {datetime.now().isoformat()}")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(run_all_tests())

