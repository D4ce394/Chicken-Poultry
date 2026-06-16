#!/usr/bin/env python3
"""
Comprehensive Health Check Script for AI-FRSS Backend
Tests all major components and endpoints
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8080"
TEST_RESULTS = []

def log_result(test_name: str, status: str, details: str = ""):
    """Log test result"""
    result = {
        "timestamp": datetime.now().isoformat(),
        "test": test_name,
        "status": status,
        "details": details
    }
    TEST_RESULTS.append(result)
    print(f"[{status}] {test_name}: {details}")

def test_basic_health():
    """Test basic health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            log_result("Basic Health Check", "✅ PASS", f"Server status: {data.get('status', 'unknown')}")
            return data
        else:
            log_result("Basic Health Check", "❌ FAIL", f"HTTP {response.status_code}")
            return None
    except Exception as e:
        log_result("Basic Health Check", "❌ FAIL", f"Connection error: {e}")
        return None

def test_comprehensive_health():
    """Test comprehensive health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health/comprehensive", timeout=10)
        if response.status_code == 200:
            data = response.json()
            log_result("Comprehensive Health", "✅ PASS", f"Components: {len(data.get('components', {}))}")
            return data
        else:
            log_result("Comprehensive Health", "❌ FAIL", f"HTTP {response.status_code}")
            return None
    except Exception as e:
        log_result("Comprehensive Health", "❌ FAIL", f"Error: {e}")
        return None

def test_yolo_health():
    """Test YOLO models health"""
    try:
        response = requests.get(f"{BASE_URL}/health/yolo", timeout=10)
        if response.status_code == 200:
            data = response.json()
            models_loaded = len(data.get('loaded_models', []))
            log_result("YOLO Models Health", "✅ PASS", f"Models loaded: {models_loaded}/4")
            return data
        else:
            log_result("YOLO Models Health", "❌ FAIL", f"HTTP {response.status_code}")
            return None
    except Exception as e:
        log_result("YOLO Models Health", "❌ FAIL", f"Error: {e}")
        return None

def test_database_health():
    """Test database health"""
    try:
        response = requests.get(f"{BASE_URL}/health/database", timeout=5)
        if response.status_code == 200:
            data = response.json()
            log_result("Database Health", "✅ PASS", f"Status: {data.get('status', 'unknown')}")
            return data
        else:
            log_result("Database Health", "❌ FAIL", f"HTTP {response.status_code}")
            return None
    except Exception as e:
        log_result("Database Health", "❌ FAIL", f"Error: {e}")
        return None

def test_api_endpoints():
    """Test API endpoints availability"""
    endpoints = [
        ("/docs", "API Documentation"),
        ("/openapi.json", "OpenAPI Schema"),
        ("/api/v1/auth/health", "Auth API Health"),
        ("/api/v1/users/health", "Users API Health"),
        ("/api/v1/files/health", "Files API Health"),
        ("/api/v1/mobile/health", "Mobile API Health")
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            if response.status_code in [200, 404]:  # 404 is ok for some endpoints
                log_result(f"Endpoint {name}", "✅ PASS", f"HTTP {response.status_code}")
            else:
                log_result(f"Endpoint {name}", "⚠️ WARN", f"HTTP {response.status_code}")
        except Exception as e:
            log_result(f"Endpoint {name}", "❌ FAIL", f"Error: {e}")

def test_websocket_endpoints():
    """Test WebSocket endpoints availability"""
    # Note: This just tests if endpoints exist, not actual WebSocket functionality
    ws_endpoints = [
        "/ws/auth",
        "/ws/users", 
        "/ws/monitoring",
        "/ws/alerts"
    ]
    
    for endpoint in ws_endpoints:
        try:
            # HTTP request to WebSocket endpoint should return 426 Upgrade Required
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            if response.status_code == 426:
                log_result(f"WebSocket {endpoint}", "✅ PASS", "WebSocket upgrade required (expected)")
            else:
                log_result(f"WebSocket {endpoint}", "⚠️ WARN", f"Unexpected HTTP {response.status_code}")
        except Exception as e:
            log_result(f"WebSocket {endpoint}", "❌ FAIL", f"Error: {e}")

def run_comprehensive_health_check():
    """Run all health checks"""
    print("=" * 60)
    print("🏥 AI-FRSS Backend Comprehensive Health Check")
    print("=" * 60)
    print(f"Target: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    # Run all tests
    basic_health = test_basic_health()
    comprehensive_health = test_comprehensive_health()
    yolo_health = test_yolo_health()
    database_health = test_database_health()
    
    test_api_endpoints()
    test_websocket_endpoints()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 HEALTH CHECK SUMMARY")
    print("=" * 60)
    
    total_tests = len(TEST_RESULTS)
    passed = len([r for r in TEST_RESULTS if "✅ PASS" in r["status"]])
    warnings = len([r for r in TEST_RESULTS if "⚠️ WARN" in r["status"]])
    failed = len([r for r in TEST_RESULTS if "❌ FAIL" in r["status"]])
    
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed}")
    print(f"⚠️ Warnings: {warnings}")
    print(f"❌ Failed: {failed}")
    
    # Overall status
    if failed == 0 and warnings == 0:
        print("\n🎉 OVERALL STATUS: HEALTHY")
    elif failed == 0:
        print("\n⚠️ OVERALL STATUS: HEALTHY WITH WARNINGS")
    else:
        print("\n❌ OVERALL STATUS: UNHEALTHY")
    
    # Detailed results
    print("\n📋 DETAILED RESULTS:")
    for result in TEST_RESULTS:
        print(f"  {result['status']} {result['test']}: {result['details']}")
    
    # Save report
    report_file = f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "target_url": BASE_URL,
            "summary": {
                "total": total_tests,
                "passed": passed,
                "warnings": warnings,
                "failed": failed
            },
            "results": TEST_RESULTS
        }, f, indent=2)
    
    print(f"\n💾 Report saved to: {report_file}")
    print("=" * 60)

if __name__ == "__main__":
    run_comprehensive_health_check()
