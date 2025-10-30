"""
Полное приемочное тестирование всех API endpoints
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

TOKEN = None
ADMIN_TOKEN = None
ENGINEER_TOKEN = None


class Colors:
    OK = "\033[92m"
    FAIL = "\033[91m"
    WARN = "\033[93m"
    INFO = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


async def test_endpoint(client: httpx.AsyncClient, name: str, method: str, url: str, 
                       expected_status: int = 200, headers: dict = None, json_data: dict = None,
                       params: dict = None, description: str = ""):
    """Универсальный тест endpoint"""
    try:
        if method.upper() == "GET":
            response = await client.get(url, headers=headers, params=params)
        elif method.upper() == "POST":
            response = await client.post(url, headers=headers, json=json_data)
        elif method.upper() == "PATCH":
            response = await client.patch(url, headers=headers, json=json_data)
        elif method.upper() == "DELETE":
            response = await client.delete(url, headers=headers)
        else:
            return False, f"Unknown method: {method}"
        
        success = response.status_code == expected_status
        
        status_icon = "[OK]" if success else "[FAIL]"
        print(f"  {status_icon} {method} {url}")
        print(f"     Status: {response.status_code} (expected: {expected_status})")
        
        if description:
            print(f"     {description}")
        
        if success:
            try:
                data = response.json()
                if isinstance(data, dict) and len(str(data)) < 200:
                    print(f"     Response: {json.dumps(data, indent=6, ensure_ascii=False)[:150]}")
            except:
                pass
        else:
            print(f"     Response: {response.text[:200]}")
        
        return success, response
    except Exception as e:
        print(f"  [FAIL] {method} {url}")
        print(f"     Error: {str(e)}")
        return False, None


async def test_health_checks(client: httpx.AsyncClient):
    """Тесты health checks"""
    print("\n" + "="*70)
    print("HEALTH CHECKS")
    print("="*70)
    
    results = {}
    
    results["health"] = await test_endpoint(client, "Health", "GET", f"{BASE_URL}/health", 200)
    results["ready"] = await test_endpoint(client, "Ready", "GET", f"{BASE_URL}/ready", 200)
    results["metrics"] = await test_endpoint(client, "Metrics", "GET", f"{BASE_URL}/metrics", 200)
    results["worker_health"] = await test_endpoint(client, "Worker Health", "GET", 
                                                   f"{BASE_URL}/worker/health", 200)
    results["worker_ready"] = await test_endpoint(client, "Worker Ready", "GET", 
                                                  f"{BASE_URL}/worker/ready", 200)
    
    return results


async def test_auth(client: httpx.AsyncClient):
    """Тесты авторизации"""
    global TOKEN, ADMIN_TOKEN
    
    print("\n" + "="*70)
    print("AUTHENTICATION")
    print("="*70)
    
    results = {}
    
    # Сначала создадим админа если его нет
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
            TOKEN = ADMIN_TOKEN = data.get("access_token")
            results["login"] = True
            print(f"  [OK] POST /auth/token")
            print(f"     Token received: {TOKEN[:30]}..." if TOKEN else "")
        else:
            results["login"] = False
            print(f"  [FAIL] POST /auth/token: {response.status_code}")
            print(f"     Response: {response.text[:200]}")
    except Exception as e:
        results["login"] = False
        print(f"  [FAIL] POST /auth/token failed: {e}")
    
    if TOKEN:
        # Test refresh token
        results["refresh"] = await test_endpoint(
            client, "Refresh", "POST", f"{BASE_URL}{API_PREFIX}/auth/refresh",
            expected_status=200,
            headers={"Authorization": f"Bearer {TOKEN}"},
            json_data={"refresh_token": "test"}  # В реальности нужен refresh token
        )
    
    return results


async def test_users(client: httpx.AsyncClient):
    """Тесты пользователей"""
    print("\n" + "="*70)
    print("USERS ENDPOINTS")
    print("="*70)
    
    results = {}
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
    
    results["me"] = await test_endpoint(
        client, "Get Me", "GET", f"{BASE_URL}{API_PREFIX}/users/me",
        headers=headers, expected_status=200
    )
    
    results["list_users"] = await test_endpoint(
        client, "List Users", "GET", f"{BASE_URL}{API_PREFIX}/users",
        headers=headers, expected_status=200
    )
    
    return results


async def test_objects(client: httpx.AsyncClient):
    """Тесты объектов"""
    print("\n" + "="*70)
    print("OBJECTS ENDPOINTS")
    print("="*70)
    
    results = {}
    object_id = None
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
    
    # Получить city_id для создания объекта
    city_id = "00000000-0000-0000-0000-000000000001"  # Заглушка
    
    # Список объектов
    success, response = await test_endpoint(
        client, "List Objects", "GET", f"{BASE_URL}{API_PREFIX}/objects",
        headers=headers, params={"limit": 10}, expected_status=200
    )
    results["list"] = success
    
    # Создание объекта
    if success and response:
        try:
            create_response = await client.post(
                f"{BASE_URL}{API_PREFIX}/objects",
                headers=headers,
                json={
                    "type": "APARTMENT",
                    "address": "ул. Тестовая, д. 1",
                    "city_id": city_id,
                    "status": "NEW"
                }
            )
            
            if create_response.status_code in [200, 201]:
                data = create_response.json()
                object_id = data.get("id")
                results["create"] = True
                print(f"  [OK] POST /objects")
                print(f"     Object ID: {object_id}")
            else:
                results["create"] = False
                print(f"  [WARN] POST /objects: {create_response.status_code}")
        except Exception as e:
            results["create"] = False
            print(f"  [WARN] POST /objects failed: {e}")
    
    # Получить объект
    if object_id:
        results["get"] = await test_endpoint(
            client, "Get Object", "GET", f"{BASE_URL}{API_PREFIX}/objects/{object_id}",
            headers=headers, expected_status=200
        )
    else:
        results["get"] = False
    
    return results


async def test_customers(client: httpx.AsyncClient):
    """Тесты клиентов"""
    print("\n" + "="*70)
    print("CUSTOMERS ENDPOINTS")
    print("="*70)
    
    results = {}
    customer_id = None
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
    
    # Список клиентов
    success, response = await test_endpoint(
        client, "List Customers", "GET", f"{BASE_URL}{API_PREFIX}/customers",
        headers=headers, params={"limit": 10}, expected_status=200
    )
    results["list"] = success
    
    # Проверка PII masking
    if success and response:
        try:
            data = response.json()
            items = data.get("items", [])
            if items:
                customer = items[0]
                phone = customer.get("phone", "")
                if phone and "***" in str(phone):
                    print(f"  [OK] PII masking works: phone={phone}")
                    results["pii_masking"] = True
                elif phone:
                    print(f"  [INFO] PII visible (may be ADMIN): phone={phone[:20]}")
                    results["pii_masking"] = True  # Не ошибка для ADMIN
        except:
            pass
    
    return results


async def test_sync(client: httpx.AsyncClient):
    """Тесты синхронизации"""
    print("\n" + "="*70)
    print("SYNC ENDPOINTS")
    print("="*70)
    
    results = {}
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
    
    import uuid
    client_id = str(uuid.uuid4())
    
    # Sync batch
    success, response = await test_endpoint(
        client, "Sync Batch", "POST", f"{BASE_URL}{API_PREFIX}/sync/batch",
        headers=headers,
        json_data={
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
        expected_status=200
    )
    results["batch"] = success
    
    # Sync changes
    results["changes"] = await test_endpoint(
        client, "Sync Changes", "GET", f"{BASE_URL}{API_PREFIX}/sync/changes",
        headers=headers,
        params={
            "since": "2025-01-01T00:00:00Z",
            "tables": ["objects"],
            "limit": 100
        },
        expected_status=200
    )
    
    return results


async def test_reports(client: httpx.AsyncClient):
    """Тесты отчётов"""
    print("\n" + "="*70)
    print("REPORTS ENDPOINTS")
    print("="*70)
    
    results = {}
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
    job_id = None
    
    # Создать задачу экспорта
    success, response = await test_endpoint(
        client, "Create Export", "POST", f"{BASE_URL}{API_PREFIX}/reports/export",
        headers=headers,
        json_data={
            "entity": "objects",
            "filters": {},
            "columns": ["id", "address", "status"],
            "sort": {"updated_at": "desc"}
        },
        expected_status=201
    )
    results["create_export"] = success
    
    if success and response:
        try:
            data = response.json()
            job_id = data.get("id")
            print(f"     Job ID: {job_id}")
        except:
            pass
    
    # Список задач
    results["list_jobs"] = await test_endpoint(
        client, "List Jobs", "GET", f"{BASE_URL}{API_PREFIX}/reports/jobs",
        headers=headers, expected_status=200
    )
    
    # Получить задачу
    if job_id:
        results["get_job"] = await test_endpoint(
            client, "Get Job", "GET", f"{BASE_URL}{API_PREFIX}/reports/jobs/{job_id}",
            headers=headers, expected_status=200
        )
    
    return results


async def test_audit(client: httpx.AsyncClient):
    """Тесты аудита"""
    print("\n" + "="*70)
    print("AUDIT ENDPOINTS")
    print("="*70)
    
    results = {}
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
    
    # Список логов аудита
    success, response = await test_endpoint(
        client, "List Audit Logs", "GET", f"{BASE_URL}{API_PREFIX}/audit",
        headers=headers,
        params={"limit": 10},
        expected_status=200
    )
    results["list"] = success
    
    # Проверка PII masking в аудите
    if success and response:
        try:
            data = response.json()
            items = data.get("items", [])
            if items:
                item = items[0]
                before_json = item.get("before_json", {})
                after_json = item.get("after_json", {})
                
                phone = before_json.get("phone") or after_json.get("phone")
                if phone and "***" in str(phone):
                    print(f"  [OK] PII masked in audit: phone contains ***")
                    results["pii_masking"] = True
                elif phone:
                    print(f"  [WARN] PII may not be masked in audit: {str(phone)[:20]}")
                    results["pii_masking"] = False
        except Exception as e:
            print(f"  [WARN] Could not check PII masking: {e}")
    
    return results


async def test_dictionaries(client: httpx.AsyncClient):
    """Тесты справочников"""
    print("\n" + "="*70)
    print("DICTIONARIES ENDPOINTS")
    print("="*70)
    
    results = {}
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
    
    results["cities"] = await test_endpoint(
        client, "List Cities", "GET", f"{BASE_URL}{API_PREFIX}/dictionaries/cities",
        headers=headers, expected_status=200
    )
    
    results["districts"] = await test_endpoint(
        client, "List Districts", "GET", f"{BASE_URL}{API_PREFIX}/dictionaries/districts",
        headers=headers, expected_status=200
    )
    
    return results


async def run_full_acceptance_test():
    """Полное приемочное тестирование"""
    print("\n" + "="*70)
    print("FULL ACCEPTANCE TEST REPORT")
    print("="*70)
    print(f"Base URL: {BASE_URL}")
    print(f"Started at: {datetime.now().isoformat()}")
    
    all_results = {}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Проверка доступности сервера
        try:
            await client.get(f"{BASE_URL}/health", timeout=5.0)
            print("\n[OK] Server is running and accessible")
        except Exception as e:
            print(f"\n[FAIL] Server is not accessible: {e}")
            print("Please start server first: uvicorn app.main:app --reload")
            return
        
        # Запускаем все тесты
        all_results["health"] = await test_health_checks(client)
        all_results["auth"] = await test_auth(client)
        all_results["users"] = await test_users(client)
        all_results["objects"] = await test_objects(client)
        all_results["customers"] = await test_customers(client)
        all_results["sync"] = await test_sync(client)
        all_results["reports"] = await test_reports(client)
        all_results["audit"] = await test_audit(client)
        all_results["dictionaries"] = await test_dictionaries(client)
    
    # Итоговый отчет
    print("\n" + "="*70)
    print("FINAL ACCEPTANCE TEST RESULTS")
    print("="*70)
    
    total_tests = 0
    passed_tests = 0
    
    for category, results in all_results.items():
        print(f"\n{category.upper()}:")
        if isinstance(results, dict):
            for test_name, result in results.items():
                total_tests += 1
                if result:
                    passed_tests += 1
                    status = "[PASS]"
                else:
                    status = "[FAIL]"
                print(f"  {status} {test_name}")
    
    print("\n" + "="*70)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {passed_tests/total_tests*100:.1f}%" if total_tests > 0 else "N/A")
    print("="*70)
    print(f"Completed at: {datetime.now().isoformat()}")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(run_full_acceptance_test())

