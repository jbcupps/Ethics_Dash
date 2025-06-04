#!/usr/bin/env python3
"""
Test script for Physical Verification Blockchain (PVB) system.

This script tests the basic functionality of the PVB system including:
- Health check
- Verifier registration
- Device registration
- Data submission
- Data verification
"""

import os
import sys
import json
import time
import hashlib
import requests
from datetime import datetime
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:5000"
PVB_API_BASE = f"{BASE_URL}/api/pvb"

def log_test(test_name: str, status: str, details: str = ""):
    """Log test results."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    status_symbol = "✓" if status == "PASS" else "✗"
    print(f"[{timestamp}] {status_symbol} {test_name}: {status}")
    if details:
        print(f"    {details}")

def test_health_check():
    """Test PVB health check endpoint."""
    try:
        response = requests.get(f"{PVB_API_BASE}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'healthy':
                log_test("Health Check", "PASS", "All systems healthy")
                return True
            else:
                log_test("Health Check", "FAIL", f"Status: {data.get('status')}")
                return False
        else:
            log_test("Health Check", "FAIL", f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_test("Health Check", "FAIL", str(e))
        return False

def test_verifier_registration():
    """Test verifier registration."""
    try:
        payload = {
            "name": "Test Verification Authority",
            "metadata": "Automated test verifier"
        }
        
        response = requests.post(
            f"{PVB_API_BASE}/verifiers",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 201:
            data = response.json()
            verifier_address = data.get('verifier_address')
            log_test("Verifier Registration", "PASS", f"Address: {verifier_address}")
            return verifier_address
        else:
            log_test("Verifier Registration", "FAIL", f"HTTP {response.status_code}: {response.text}")
            return None
    except Exception as e:
        log_test("Verifier Registration", "FAIL", str(e))
        return None

def test_device_registration(verifier_address: str):
    """Test device registration under a verifier."""
    try:
        payload = {
            "device_id": "test_camera_001",
            "device_public_key": "0x04a1b2c3d4e5f6789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            "metadata": "Test camera device for PVB testing"
        }
        
        response = requests.post(
            f"{PVB_API_BASE}/verifiers/{verifier_address}/devices",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 201:
            data = response.json()
            device_id = data.get('device_id')
            log_test("Device Registration", "PASS", f"Device: {device_id}")
            return device_id
        else:
            log_test("Device Registration", "FAIL", f"HTTP {response.status_code}: {response.text}")
            return None
    except Exception as e:
        log_test("Device Registration", "FAIL", str(e))
        return None

def test_data_submission(device_id: str):
    """Test data submission to PVB."""
    try:
        # Generate test data
        test_data = b"This is test media data for PVB verification"
        data_hash = hashlib.sha256(test_data).hexdigest()
        
        payload = {
            "device_id": device_id,
            "data_hash": data_hash,
            "signature": "test_signature_placeholder",  # In real implementation, this would be a proper ECDSA signature
            "data_uri": f"ipfs://QmTest{data_hash[:16]}",
            "metadata": "Test data submission for PVB verification"
        }
        
        response = requests.post(
            f"{PVB_API_BASE}/data",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 201:
            data = response.json()
            tx_hash = data.get('transaction_hash')
            log_test("Data Submission", "PASS", f"TX: {tx_hash}")
            return data_hash
        else:
            log_test("Data Submission", "FAIL", f"HTTP {response.status_code}: {response.text}")
            return None
    except Exception as e:
        log_test("Data Submission", "FAIL", str(e))
        return None

def test_data_verification(data_hash: str):
    """Test data verification."""
    try:
        response = requests.get(
            f"{PVB_API_BASE}/data/{data_hash}/verify",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            is_verified = data.get('is_verified')
            if is_verified:
                log_test("Data Verification", "PASS", f"Hash: {data_hash[:16]}...")
                return True
            else:
                log_test("Data Verification", "FAIL", "Data not verified")
                return False
        elif response.status_code == 404:
            log_test("Data Verification", "FAIL", "Data not found")
            return False
        else:
            log_test("Data Verification", "FAIL", f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        log_test("Data Verification", "FAIL", str(e))
        return False

def test_device_info(device_id: str):
    """Test device information retrieval."""
    try:
        response = requests.get(
            f"{PVB_API_BASE}/devices/{device_id}",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            is_active = data.get('is_active')
            log_test("Device Info", "PASS", f"Active: {is_active}")
            return True
        elif response.status_code == 404:
            log_test("Device Info", "FAIL", "Device not found")
            return False
        else:
            log_test("Device Info", "FAIL", f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        log_test("Device Info", "FAIL", str(e))
        return False

def wait_for_service(max_retries: int = 30, retry_interval: int = 2):
    """Wait for the PVB service to become available."""
    print(f"Waiting for PVB service at {BASE_URL}...")
    
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(f"{BASE_URL}/api/health", timeout=5)
            if response.status_code == 200:
                print(f"✓ Service available after {attempt} attempts")
                return True
        except Exception:
            pass
        
        if attempt < max_retries:
            print(f"  Attempt {attempt}/{max_retries} failed, retrying in {retry_interval}s...")
            time.sleep(retry_interval)
    
    print(f"✗ Service not available after {max_retries} attempts")
    return False

def main():
    """Run all PVB tests."""
    print("=" * 60)
    print("Physical Verification Blockchain (PVB) Test Suite")
    print("=" * 60)
    
    # Wait for service to be available
    if not wait_for_service():
        print("ERROR: PVB service is not available")
        sys.exit(1)
    
    print("\nRunning PVB tests...")
    print("-" * 40)
    
    # Test sequence
    tests_passed = 0
    total_tests = 0
    
    # 1. Health Check
    total_tests += 1
    if test_health_check():
        tests_passed += 1
    else:
        print("ERROR: Health check failed. Cannot proceed with other tests.")
        sys.exit(1)
    
    # 2. Verifier Registration
    total_tests += 1
    verifier_address = test_verifier_registration()
    if verifier_address:
        tests_passed += 1
    else:
        print("ERROR: Verifier registration failed. Cannot proceed with device tests.")
        sys.exit(1)
    
    # 3. Device Registration
    total_tests += 1
    device_id = test_device_registration(verifier_address)
    if device_id:
        tests_passed += 1
    else:
        print("ERROR: Device registration failed. Cannot proceed with data tests.")
        sys.exit(1)
    
    # 4. Device Info
    total_tests += 1
    if test_device_info(device_id):
        tests_passed += 1
    
    # 5. Data Submission
    total_tests += 1
    data_hash = test_data_submission(device_id)
    if data_hash:
        tests_passed += 1
        
        # 6. Data Verification
        total_tests += 1
        if test_data_verification(data_hash):
            tests_passed += 1
    
    # Results
    print("-" * 40)
    print(f"Tests completed: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("✓ All tests passed! PVB system is working correctly.")
        sys.exit(0)
    else:
        print("✗ Some tests failed. Check the logs above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main() 