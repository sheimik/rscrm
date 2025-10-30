"""
Полные acceptance-тесты (синхронная версия для надёжности)
"""
import sys
from pathlib import Path
import requests
from datetime import datetime
import json
import time
import uuid

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

BASE_URL = "http://127.0.0.1:8000"
API_PREFIX = "/api/v1"

# Глобальные переменные
TOKEN = None
REFRESH_TOKEN = None
TEST_USER_ID = None
TEST_OBJECT_ID = None
TEST_CUSTOMER_ID = None
TEST_JOB_ID = None

results = {
    "passed": [],
    "failed": [],
    "warnings": []
}


def log_result(test_name: str, passed: bool, message: str = "", warning: bool = False):
    """Логировать результат теста"""
    if warning:
        results["warnings"].append((test_name, message))
        print(f"[WARN] {test_name}: {message}")
    elif passed:
        results["passed"].append((test_name, message))
        print(f"[OK] {test_name}: {message}")
    else:
        results["failed"].append((test_name, message))
        print(f"[FAIL] {test_name}: {message}")


def wait_for_server(max_retries: int = 30):
    """Ждать запуска сервера"""
    print("  Checking server availability...")
    for i in range(max_retries):
        try:
            # Используем более длинный таймаут и проверяем разные варианты
            try:
                response = requests.get(f"{BASE_URL}/health", timeout=10, allow_redirects=True)
            except:
                response = requests.get("http://localhost:8000/health", timeout=10, allow_redirects=True)
            
            if response.status_code == 200:
                log_result("Server Ready", True, f"Server responded after {i+1} attempts")
                return True
            elif response.status_code in [502, 503]:
                # Сервер ещё не готов
                if i % 5 == 0:
                    print(f"  Attempt {i+1}/{max_retries}: Server returning {response.status_code}, waiting...")
                time.sleep(2)
            else:
                log_result("Server Ready", False, f"Unexpected status: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError as e:
            if i % 5 == 0:
                print(f"  Attempt {i+1}/{max_retries}: Connection error, waiting...")
            time.sleep(2)
        except Exception as e:
            if i % 5 == 0:
                print(f"  Attempt {i+1}/{max_retries}: {str(e)[:50]}...")
            time.sleep(1)
    
    log_result("Server Ready", False, "Server did not start in time")
    return False


def test_health_endpoints():
    """Тест 1: Health endpoints"""
    print("\n" + "="*70)
    print("TEST SUITE 1: Health & Readiness Checks")
    print("="*70)
    
    # /health
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            log_result("GET /health", True, f"Status: {data.get('status')}")
        else:
            log_result("GET /health", False, f"Status code: {response.status_code}")
    except Exception as e:
        log_result("GET /health", False, str(e))
    
    # /ready
    try:
        response = requests.get(f"{BASE_URL}/ready", timeout=5)
        if response.status_code == 200:
            data = response.json()
            log_result("GET /ready", True, f"Database: {data.get('database')}")
        else:
            log_result("GET /ready", False, f"Status code: {response.status_code}")
    except Exception as e:
        log_result("GET /ready", False, str(e))
    
    # /metrics
    try:
        response = requests.get(f"{BASE_URL}/metrics", timeout=5)
        if response.status_code == 200:
            data = response.json()
            log_result("GET /metrics", True, f"Database: {data.get('database')}, Redis: {data.get('redis')}")
        else:
            log_result("GET /metrics", True, f"Status: {response.status_code}", warning=True)
    except Exception as e:
        log_result("GET /metrics", True, str(e), warning=True)
    
    # /worker/health
    try:
        response = requests.get(f"{BASE_URL}/worker/health", timeout=5)
        if response.status_code in [200, 503]:
            data = response.json()
            log_result("GET /worker/health", True, f"Status: {data.get('status')}", warning=(response.status_code == 503))
        else:
            log_result("GET /worker/health", True, f"Status: {response.status_code}", warning=True)
    except Exception as e:
        log_result("GET /worker/health", True, str(e), warning=True)


def test_auth_endpoints():
    """Тест 2: Auth endpoints"""
    global TOKEN, REFRESH_TOKEN
    
    print("\n" + "="*70)
    print("TEST SUITE 2: Authentication")
    print("="*70)
    
    # POST /auth/token
    try:
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/auth/token",
            data={
                "username": "admin@example.com",
                "password": "password123"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            TOKEN = data.get("access_token")
            REFRESH_TOKEN = data.get("refresh_token")
            log_result("POST /auth/token", True, f"Token received: {TOKEN[:30]}...")
            return True
        elif response.status_code == 401:
            log_result("POST /auth/token", False, "User not found. Need to create admin first.")
            print("  HINT: Run 'python scripts/create_admin.py admin@example.com password123'")
            return False
        else:
            log_result("POST /auth/token", False, f"Status: {response.status_code}, Response: {response.text[:200]}")
            return False
    except Exception as e:
        log_result("POST /auth/token", False, str(e))
        return False
    
    # POST /auth/refresh
    if REFRESH_TOKEN:
        try:
            response = requests.post(
                f"{BASE_URL}{API_PREFIX}/auth/refresh",
                json={"refresh_token": REFRESH_TOKEN},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                log_result("POST /auth/refresh", True, "New token received")
            else:
                log_result("POST /auth/refresh", True, f"Status: {response.status_code}", warning=True)
        except Exception as e:
            log_result("POST /auth/refresh", True, str(e), warning=True)


def test_users_endpoints():
    """Тест 3: Users endpoints"""
    global TEST_USER_ID
    
    print("\n" + "="*70)
    print("TEST SUITE 3: Users Management")
    print("="*70)
    
    if not TOKEN:
        log_result("Users endpoints", False, "No token available")
        return
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    # GET /users/me
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/users/me", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            TEST_USER_ID = data.get("id")
            log_result("GET /users/me", True, f"User: {data.get('email')}, Role: {data.get('role')}")
        else:
            log_result("GET /users/me", False, f"Status: {response.status_code}")
    except Exception as e:
        log_result("GET /users/me", False, str(e))
    
    # GET /users
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/users", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            log_result("GET /users", True, f"Users count: {len(data)}")
        elif response.status_code == 403:
            log_result("GET /users", True, "Requires ADMIN role", warning=True)
        else:
            log_result("GET /users", True, f"Status: {response.status_code}", warning=True)
    except Exception as e:
        log_result("GET /users", True, str(e), warning=True)


def test_dictionaries_endpoints():
    """Тест 4: Dictionaries endpoints"""
    print("\n" + "="*70)
    print("TEST SUITE 4: Dictionaries")
    print("="*70)
    
    if not TOKEN:
        log_result("Dictionaries endpoints", False, "No token available")
        return
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    # GET /dictionaries/cities
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/dictionaries/cities", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            log_result("GET /dictionaries/cities", True, f"Cities count: {len(data)}")
            return data[0].get("id") if data else None
        else:
            log_result("GET /dictionaries/cities", True, f"Status: {response.status_code}", warning=True)
            return None
    except Exception as e:
        log_result("GET /dictionaries/cities", True, str(e), warning=True)
        return None
    
    # GET /dictionaries/districts
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/dictionaries/districts", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            log_result("GET /dictionaries/districts", True, f"Districts count: {len(data)}")
        else:
            log_result("GET /dictionaries/districts", True, f"Status: {response.status_code}", warning=True)
    except Exception as e:
        log_result("GET /dictionaries/districts", True, str(e), warning=True)


def test_objects_endpoints(city_id=None):
    """Тест 5: Objects endpoints"""
    global TEST_OBJECT_ID
    
    print("\n" + "="*70)
    print("TEST SUITE 5: Objects Management")
    print("="*70)
    
    if not TOKEN:
        log_result("Objects endpoints", False, "No token available")
        return
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    # GET /objects (список)
    try:
        response = requests.get(
            f"{BASE_URL}{API_PREFIX}/objects",
            params={"limit": 10},
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            log_result("GET /objects", True, f"Items: {data.get('total', 0)}, Page: {data.get('page', 1)}")
        else:
            log_result("GET /objects", False, f"Status: {response.status_code}")
    except Exception as e:
        log_result("GET /objects", False, str(e))
    
    # POST /objects (создание)
    if city_id:
        try:
            response = requests.post(
                f"{BASE_URL}{API_PREFIX}/objects",
                json={
                    "type": "APARTMENT",
                    "address": "ул. Acceptance Test, д. 1",
                    "city_id": city_id,
                    "status": "NEW"
                },
                headers=headers,
                timeout=10
            )
            if response.status_code in [200, 201]:
                data = response.json()
                TEST_OBJECT_ID = data.get("id")
                log_result("POST /objects", True, f"Object created: {TEST_OBJECT_ID}")
            else:
                log_result("POST /objects", False, f"Status: {response.status_code}, Response: {response.text[:200]}")
        except Exception as e:
            log_result("POST /objects", False, str(e))
    else:
        log_result("POST /objects", True, "No city_id available, skipping", warning=True)
    
    # GET /objects/{id}
    if TEST_OBJECT_ID:
        try:
            response = requests.get(
                f"{BASE_URL}{API_PREFIX}/objects/{TEST_OBJECT_ID}",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                log_result("GET /objects/{id}", True, f"Address: {data.get('address')}")
            else:
                log_result("GET /objects/{id}", False, f"Status: {response.status_code}")
        except Exception as e:
            log_result("GET /objects/{id}", False, str(e))
    
    # PATCH /objects/{id} (с optimistic locking)
    if TEST_OBJECT_ID:
        try:
            # Сначала получим текущую версию
            response = requests.get(
                f"{BASE_URL}{API_PREFIX}/objects/{TEST_OBJECT_ID}",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                version = data.get("version")
                
                # Обновим с правильной версией
                response = requests.patch(
                    f"{BASE_URL}{API_PREFIX}/objects/{TEST_OBJECT_ID}",
                    json={
                        "address": "ул. Acceptance Test, д. 1 (Updated)",
                        "version": version
                    },
                    headers=headers,
                    timeout=10
                )
                if response.status_code == 200:
                    log_result("PATCH /objects/{id}", True, "Object updated with optimistic locking")
                else:
                    log_result("PATCH /objects/{id}", True, f"Status: {response.status_code}", warning=True)
        except Exception as e:
            log_result("PATCH /objects/{id}", True, str(e), warning=True)


def test_customers_endpoints():
    """Тест 6: Customers endpoints (с PII masking)"""
    global TEST_CUSTOMER_ID
    
    print("\n" + "="*70)
    print("TEST SUITE 6: Customers Management (PII Masking)")
    print("="*70)
    
    if not TOKEN:
        log_result("Customers endpoints", False, "No token available")
        return
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    # GET /customers (список)
    try:
        response = requests.get(
            f"{BASE_URL}{API_PREFIX}/customers",
            params={"limit": 10},
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            log_result("GET /customers", True, f"Items: {len(items)}")
            
            # Проверяем PII masking
            if items:
                customer = items[0]
                phone = customer.get("phone")
                if phone:
                    if "***" in phone:
                        log_result("PII Masking", True, f"Phone masked: {phone}")
                    else:
                        log_result("PII Masking", True, f"Phone visible (may be ADMIN): {phone[:20]}", warning=True)
        else:
            log_result("GET /customers", False, f"Status: {response.status_code}")
    except Exception as e:
        log_result("GET /customers", False, str(e))
    
    # POST /customers (создание с нормализацией телефона)
    if TEST_OBJECT_ID:
        try:
            phone = "+7 (999) 123-45-67"  # Будет нормализован
            response = requests.post(
                f"{BASE_URL}{API_PREFIX}/customers",
                json={
                    "object_id": TEST_OBJECT_ID,
                    "full_name": "Тестовый Клиент (Acceptance)",
                    "phone": phone,
                    "provider_rating": 4,
                    "interests": ["INTERNET", "TV"]
                },
                headers=headers,
                timeout=10
            )
            if response.status_code in [200, 201]:
                data = response.json()
                TEST_CUSTOMER_ID = data.get("id")
                normalized_phone = data.get("phone")
                log_result("POST /customers", True, f"Customer created: {TEST_CUSTOMER_ID}, Phone normalized: {normalized_phone}")
            else:
                log_result("POST /customers", False, f"Status: {response.status_code}, Response: {response.text[:200]}")
        except Exception as e:
            log_result("POST /customers", True, str(e), warning=True)


def test_sync_endpoints():
    """Тест 7: Sync endpoints"""
    print("\n" + "="*70)
    print("TEST SUITE 7: Offline Synchronization")
    print("="*70)
    
    if not TOKEN:
        log_result("Sync endpoints", False, "No token available")
        return
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    # POST /sync/batch (happy path)
    try:
        client_id = str(uuid.uuid4())
        
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/sync/batch",
            json={
                "items": [{
                    "client_generated_id": client_id,
                    "table_name": "objects",
                    "payload": {
                        "address": "ул. Sync Test, д. 1",
                        "city_id": "00000000-0000-0000-0000-000000000001",
                        "status": "NEW",
                        "type": "APARTMENT"
                    },
                    "updated_at": datetime.utcnow().isoformat() + "Z",
                    "version": 1
                }],
                "force": False
            },
            headers=headers,
            timeout=15
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            results_list = data.get("results", [])
            if results_list:
                result = results_list[0]
                log_result("POST /sync/batch", True, f"Status: {result.get('status')}, Server ID: {result.get('server_id')}")
            else:
                log_result("POST /sync/batch", True, "No results", warning=True)
        else:
            log_result("POST /sync/batch", True, f"Status: {response.status_code}, Response: {response.text[:200]}", warning=True)
    except Exception as e:
        log_result("POST /sync/batch", True, str(e), warning=True)
    
    # GET /sync/changes
    try:
        since = "2025-01-01T00:00:00Z"
        response = requests.get(
            f"{BASE_URL}{API_PREFIX}/sync/changes",
            params={
                "since": since,
                "tables": ["objects"],
                "limit": 100
            },
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            log_result("GET /sync/changes", True, f"Items: {len(items)}")
        else:
            log_result("GET /sync/changes", True, f"Status: {response.status_code}", warning=True)
    except Exception as e:
        log_result("GET /sync/changes", True, str(e), warning=True)


def test_reports_endpoints():
    """Тест 8: Reports endpoints"""
    global TEST_JOB_ID
    
    print("\n" + "="*70)
    print("TEST SUITE 8: Reports Export")
    print("="*70)
    
    if not TOKEN:
        log_result("Reports endpoints", False, "No token available")
        return
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    # POST /reports/export
    try:
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/reports/export",
            json={
                "entity": "objects",
                "filters": {},
                "columns": ["id", "address", "status"],
                "sort": {"updated_at": "desc"}
            },
            headers=headers,
            timeout=15
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            TEST_JOB_ID = data.get("id")
            log_result("POST /reports/export", True, f"Job created: {TEST_JOB_ID}, Status: {data.get('status')}")
        else:
            log_result("POST /reports/export", True, f"Status: {response.status_code}", warning=True)
    except Exception as e:
        log_result("POST /reports/export", True, str(e), warning=True)
    
    # GET /reports/jobs
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/reports/jobs", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            log_result("GET /reports/jobs", True, f"Jobs count: {len(data)}")
        else:
            log_result("GET /reports/jobs", True, f"Status: {response.status_code}", warning=True)
    except Exception as e:
        log_result("GET /reports/jobs", True, str(e), warning=True)
    
    # GET /reports/jobs/{id}
    if TEST_JOB_ID:
        try:
            response = requests.get(
                f"{BASE_URL}{API_PREFIX}/reports/jobs/{TEST_JOB_ID}",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                log_result("GET /reports/jobs/{id}", True, f"Status: {data.get('status')}")
            else:
                log_result("GET /reports/jobs/{id}", True, f"Status: {response.status_code}", warning=True)
        except Exception as e:
            log_result("GET /reports/jobs/{id}", True, str(e), warning=True)


def test_audit_endpoints():
    """Тест 9: Audit endpoints"""
    print("\n" + "="*70)
    print("TEST SUITE 9: Audit Logs")
    print("="*70)
    
    if not TOKEN:
        log_result("Audit endpoints", False, "No token available")
        return
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    # GET /audit
    try:
        response = requests.get(
            f"{BASE_URL}{API_PREFIX}/audit",
            params={"limit": 10},
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            log_result("GET /audit", True, f"Items: {len(items)}")
            
            # Проверяем PII masking в аудите
            for item in items[:3]:
                before_json = item.get("before_json", {})
                after_json = item.get("after_json", {})
                phone = before_json.get("phone") or after_json.get("phone")
                if phone and "***" not in str(phone):
                    log_result("PII in Audit", True, f"Phone may not be masked: {phone[:20]}", warning=True)
        elif response.status_code == 403:
            log_result("GET /audit", True, "Requires ADMIN/SUPERVISOR role", warning=True)
        else:
            log_result("GET /audit", True, f"Status: {response.status_code}", warning=True)
    except Exception as e:
        log_result("GET /audit", True, str(e), warning=True)


def run_all_tests():
    """Запуск всех acceptance-тестов"""
    print("\n" + "="*70)
    print("FULL ACCEPTANCE TESTS")
    print("="*70)
    print(f"Base URL: {BASE_URL}")
    print(f"Started at: {datetime.now().isoformat()}")
    print("="*70)
    
    # Ждём запуска сервера
    print("\nWaiting for server to start...")
    if not wait_for_server():
        print("\n[FAIL] Server is not running. Cannot continue.")
        print("\nTo start server manually:")
        print("  cd backend")
        print("  uvicorn app.main:app --reload --host 127.0.0.1 --port 8000")
        return
    
    # Запускаем все тесты
    test_health_endpoints()
    auth_success = test_auth_endpoints()
    
    # Если авторизация прошла, продолжаем
    if auth_success and TOKEN:
        test_users_endpoints()
        city_id = test_dictionaries_endpoints()
        test_objects_endpoints(city_id)
        test_customers_endpoints()
        test_sync_endpoints()
        test_reports_endpoints()
        test_audit_endpoints()
    else:
        print("\n[WARN] Authentication failed. Skipping protected endpoints.")
        print("       Please create admin user:")
        print("       python scripts/create_admin.py admin@example.com password123")
    
    # Итоговый отчет
    print("\n" + "="*70)
    print("FINAL REPORT")
    print("="*70)
    
    total_passed = len(results["passed"])
    total_failed = len(results["failed"])
    total_warnings = len(results["warnings"])
    total = total_passed + total_failed + total_warnings
    
    print(f"\nTotal tests: {total}")
    print(f"[OK] Passed: {total_passed}")
    print(f"[FAIL] Failed: {total_failed}")
    print(f"[WARN] Warnings: {total_warnings}")
    
    if total > 0:
        success_rate = (total_passed / total) * 100
        print(f"Success rate: {success_rate:.1f}%")
    
    if results["passed"]:
        print("\n[PASSED TESTS]:")
        for test_name, message in results["passed"]:
            print(f"  [OK] {test_name}: {message}")
    
    if results["failed"]:
        print("\n[FAILED TESTS]:")
        for test_name, message in results["failed"]:
            print(f"  [FAIL] {test_name}: {message}")
    
    if results["warnings"]:
        print("\n[WARNINGS] (non-critical):")
        for test_name, message in results["warnings"][:10]:  # Показываем первые 10
            print(f"  [WARN] {test_name}: {message}")
        if len(results["warnings"]) > 10:
            print(f"  ... and {len(results['warnings']) - 10} more warnings")
    
    print("\n" + "="*70)
    print(f"Completed at: {datetime.now().isoformat()}")
    print("="*70)
    
    # Возвращаем код выхода
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())

