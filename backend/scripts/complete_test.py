"""
Полное приемочное тестирование с созданными данными
"""
import asyncio
import sys
from pathlib import Path
import httpx
from datetime import datetime
import json
import uuid

sys.path.insert(0, str(Path(__file__).parent.parent))

BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

TOKEN = None


async def get_token(client: httpx.AsyncClient):
    """Получить токен"""
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
            return True
        return False
    except:
        return False


async def test_with_auth(client: httpx.AsyncClient, method: str, url: str, 
                        expected: int = 200, json_data: dict = None, params: dict = None):
    """Тест с авторизацией"""
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
    try:
        if method == "GET":
            response = await client.get(url, headers=headers, params=params)
        elif method == "POST":
            response = await client.post(url, headers=headers, json=json_data)
        elif method == "PATCH":
            response = await client.patch(url, headers=headers, json=json_data)
        else:
            return False, None
        
        status = "[OK]" if response.status_code == expected else "[FAIL]"
        print(f"  {status} {method} {url}")
        print(f"     Status: {response.status_code} (expected: {expected})")
        
        if response.status_code == expected:
            try:
                data = response.json()
                return True, data
            except:
                return True, None
        else:
            print(f"     Response: {response.text[:200]}")
            return False, None
    except Exception as e:
        print(f"  [FAIL] {method} {url}")
        print(f"     Error: {e}")
        return False, None


async def run_complete_test():
    """Полное тестирование"""
    print("\n" + "="*70)
    print("COMPLETE ACCEPTANCE TEST")
    print("="*70)
    print(f"Started: {datetime.now().isoformat()}")
    
    results = {}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Проверка сервера
        try:
            health = await client.get(f"{BASE_URL}/health")
            print(f"\n[OK] Server is running: {health.status_code}")
        except:
            print("\n[FAIL] Server is not running")
            return
        
        # Авторизация
        print("\n" + "-"*70)
        print("AUTHENTICATION")
        print("-"*70)
        results["login"] = await get_token(client)
        if not results["login"]:
            print("  [FAIL] Cannot login - admin user may not exist")
            print("  Run: python scripts/create_admin.py admin@example.com password123 'Admin User'")
            return
        
        print(f"  [OK] Login successful")
        print(f"     Token: {TOKEN[:40]}...")
        
        # Health checks
        print("\n" + "-"*70)
        print("HEALTH CHECKS")
        print("-"*70)
        results["health"] = await test_with_auth(client, "GET", f"{BASE_URL}/health", 200)
        results["ready"] = await test_with_auth(client, "GET", f"{BASE_URL}/ready", 200)
        results["metrics"] = await test_with_auth(client, "GET", f"{BASE_URL}/metrics", 200)
        
        # Users
        print("\n" + "-"*70)
        print("USERS")
        print("-"*70)
        results["users_me"] = await test_with_auth(client, "GET", f"{BASE_URL}{API_PREFIX}/users/me", 200)
        results["users_list"] = await test_with_auth(client, "GET", f"{BASE_URL}{API_PREFIX}/users", 200)
        
        # Dictionaries
        print("\n" + "-"*70)
        print("DICTIONARIES")
        print("-"*70)
        results["cities"] = await test_with_auth(client, "GET", f"{BASE_URL}{API_PREFIX}/dictionaries/cities", 200)
        results["districts"] = await test_with_auth(client, "GET", f"{BASE_URL}{API_PREFIX}/dictionaries/districts", 200)
        
        # Получить city_id для тестов
        city_id = None
        if results["cities"][0]:
            try:
                cities_data = results["cities"][1]
                if cities_data and len(cities_data) > 0:
                    city_id = str(cities_data[0].get("id"))
                    print(f"     Using city_id: {city_id}")
            except:
                pass
        
        # Objects
        print("\n" + "-"*70)
        print("OBJECTS")
        print("-"*70)
        results["objects_list"] = await test_with_auth(client, "GET", f"{BASE_URL}{API_PREFIX}/objects", 200, params={"limit": 10})
        
        object_id = None
        if city_id:
            # Создать объект
            success, data = await test_with_auth(
                client, "POST", f"{BASE_URL}{API_PREFIX}/objects", 201,
                json_data={
                    "type": "APARTMENT",
                    "address": "ул. Тестовая, д. 1",
                    "city_id": city_id,
                    "status": "NEW"
                }
            )
            results["objects_create"] = success
            if success and data:
                object_id = data.get("id")
                print(f"     Created object: {object_id}")
        
        if object_id:
            # Получить объект
            results["objects_get"] = await test_with_auth(client, "GET", f"{BASE_URL}{API_PREFIX}/objects/{object_id}", 200)
        
        # Customers
        print("\n" + "-"*70)
        print("CUSTOMERS")
        print("-"*70)
        results["customers_list"] = await test_with_auth(client, "GET", f"{BASE_URL}{API_PREFIX}/customers", 200, params={"limit": 10})
        
        customer_id = None
        if object_id:
            # Создать клиента
            success, data = await test_with_auth(
                client, "POST", f"{BASE_URL}{API_PREFIX}/customers", 201,
                json_data={
                    "object_id": object_id,
                    "full_name": "Иван Иванов",
                    "phone": "+7 (999) 123-45-67",
                    "provider_rating": 4
                }
            )
            results["customers_create"] = success
            if success and data:
                customer_id = data.get("id")
                phone = data.get("phone")
                print(f"     Created customer: {customer_id}")
                print(f"     Phone normalized: {phone}")
        
        # Sync
        print("\n" + "-"*70)
        print("SYNC")
        print("-"*70)
        client_id = str(uuid.uuid4())
        success, data = await test_with_auth(
            client, "POST", f"{BASE_URL}{API_PREFIX}/sync/batch", 200,
            json_data={
                "items": [{
                    "client_generated_id": client_id,
                    "table_name": "objects",
                    "payload": {
                        "address": "ул. Офлайн-тест, д. 2",
                        "city_id": city_id,
                        "status": "NEW",
                        "type": "APARTMENT"
                    },
                    "updated_at": datetime.utcnow().isoformat() + "Z",
                    "version": 1
                }],
                "force": False
            }
        )
        results["sync_batch"] = success
        if success and data:
            if data.get("results"):
                result = data["results"][0]
                print(f"     Status: {result.get('status')}, Server ID: {result.get('server_id')}")
        
        # Sync changes
        results["sync_changes"] = await test_with_auth(
            client, "GET", f"{BASE_URL}{API_PREFIX}/sync/changes", 200,
            params={"since": "2025-01-01T00:00:00Z", "tables": ["objects"], "limit": 100}
        )
        
        # Reports
        print("\n" + "-"*70)
        print("REPORTS")
        print("-"*70)
        success, data = await test_with_auth(
            client, "POST", f"{BASE_URL}{API_PREFIX}/reports/export", 201,
            json_data={
                "entity": "objects",
                "filters": {},
                "columns": ["id", "address", "status"],
                "sort": {"updated_at": "desc"}
            }
        )
        results["reports_create"] = success
        job_id = None
        if success and data:
            job_id = data.get("id")
            print(f"     Job ID: {job_id}, Status: {data.get('status')}")
        
        results["reports_list"] = await test_with_auth(client, "GET", f"{BASE_URL}{API_PREFIX}/reports/jobs", 200)
        
        if job_id:
            results["reports_get"] = await test_with_auth(client, "GET", f"{BASE_URL}{API_PREFIX}/reports/jobs/{job_id}", 200)
        
        # Audit
        print("\n" + "-"*70)
        print("AUDIT")
        print("-"*70)
        success, data = await test_with_auth(client, "GET", f"{BASE_URL}{API_PREFIX}/audit", 200, params={"limit": 10})
        results["audit_list"] = success
        if success and data:
            items = data.get("items", [])
            print(f"     Found {len(items)} audit log entries")
            if items:
                item = items[0]
                before_json = item.get("before_json", {})
                after_json = item.get("after_json", {})
                phone = before_json.get("phone") or after_json.get("phone")
                if phone and "***" in str(phone):
                    print(f"     [OK] PII masked in audit: phone contains ***")
        
        # PII Masking check
        if customer_id:
            print("\n" + "-"*70)
            print("PII MASKING")
            print("-"*70)
            success, data = await test_with_auth(client, "GET", f"{BASE_URL}{API_PREFIX}/customers/{customer_id}", 200)
            results["pii_check"] = success
            if success and data:
                phone = data.get("phone", "")
                if phone and "***" not in phone:
                    print(f"     [INFO] PII visible (ADMIN role): {phone}")
                elif phone and "***" in phone:
                    print(f"     [OK] PII masked: {phone}")
    
    # Итоговый отчет
    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    
    total = len(results)
    passed = sum(1 for v in results.values() if isinstance(v, tuple) and v[0] or (isinstance(v, bool) and v))
    failed = total - passed
    
    print(f"\nTotal Tests: {total}")
    print(f"[OK] Passed: {passed}")
    print(f"[FAIL] Failed: {failed}")
    print(f"Success Rate: {passed/total*100:.1f}%" if total > 0 else "N/A")
    
    print("\nDetailed Results:")
    for test_name, result in results.items():
        if isinstance(result, tuple):
            status = "[PASS]" if result[0] else "[FAIL]"
        else:
            status = "[PASS]" if result else "[FAIL]"
        print(f"  {status}: {test_name}")
    
    print("\n" + "="*70)
    print(f"Completed: {datetime.now().isoformat()}")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(run_complete_test())

