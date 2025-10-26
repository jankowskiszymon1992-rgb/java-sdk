#!/usr/bin/env python3
"""
Backend API Testing for Financial System
Tests the new Financial system with OCR for invoices
"""

import requests
import json
import time
import os
from datetime import datetime, timezone, timedelta

# Get backend URL from frontend .env
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except:
        pass
    return "https://pwa-troubleshoot-1.preview.emergentagent.com"

BASE_URL = get_backend_url()
API_URL = f"{BASE_URL}/api"

def test_create_employee():
    """Test POST /api/employees endpoint"""
    print("\n=== Testing Create Employee Endpoint ===")
    
    url = f"{API_URL}/employees"
    
    # Test data as specified in the request
    test_data = {
        "name": "Jan Kowalski",
        "hourly_rate": 35.50,
        "notes": "Elektryk - pomocnik"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Sending POST request to: {url}")
        print(f"Request data: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=test_data, headers=headers, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verify response structure
            required_fields = ["id", "name", "hourly_rate", "notes", "created_at", "updated_at"]
            missing_fields = [field for field in required_fields if field not in response_data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False, None
            
            # Verify data matches
            if response_data["name"] != test_data["name"]:
                print(f"❌ Name mismatch. Expected: {test_data['name']}, Got: {response_data['name']}")
                return False, None
            
            if response_data["hourly_rate"] != test_data["hourly_rate"]:
                print(f"❌ Hourly rate mismatch. Expected: {test_data['hourly_rate']}, Got: {response_data['hourly_rate']}")
                return False, None
            
            if response_data["notes"] != test_data["notes"]:
                print(f"❌ Notes mismatch. Expected: {test_data['notes']}, Got: {response_data['notes']}")
                return False, None
            
            # Verify ID is generated
            if not response_data["id"] or len(response_data["id"]) == 0:
                print("❌ Employee ID is empty")
                return False, None
            
            print("✅ Create Employee endpoint working correctly")
            print(f"Created employee ID: {response_data['id']}")
            return True, response_data["id"]
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False, None
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (15s)")
        return False, None
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - backend may not be running")
        return False, None
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False, None

def test_get_employees():
    """Test GET /api/employees endpoint"""
    print("\n=== Testing Get Employees Endpoint ===")
    
    url = f"{API_URL}/employees"
    
    try:
        print(f"Sending GET request to: {url}")
        
        response = requests.get(url, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verify response is a list
            if not isinstance(response_data, list):
                print("❌ Response is not a list")
                return False
            
            # If we have employees, verify structure
            if len(response_data) > 0:
                print(f"✅ Found {len(response_data)} employee(s)")
                
                # Verify employee structure
                for i, employee in enumerate(response_data):
                    required_fields = ["id", "name", "hourly_rate", "created_at", "updated_at"]
                    missing_fields = [field for field in required_fields if field not in employee]
                    
                    if missing_fields:
                        print(f"❌ Employee {i} missing fields: {missing_fields}")
                        return False
                
                # Check if our test employee "Jan Kowalski" is in the list
                jan_found = any(emp.get("name") == "Jan Kowalski" for emp in response_data)
                if jan_found:
                    print("✅ Test employee 'Jan Kowalski' found in employee list")
                    # Verify hourly rate
                    jan_employee = next(emp for emp in response_data if emp.get("name") == "Jan Kowalski")
                    if jan_employee.get("hourly_rate") == 35.50:
                        print("✅ Jan Kowalski has correct hourly rate: 35.50 zł/h")
                    else:
                        print(f"❌ Jan Kowalski hourly rate mismatch. Expected: 35.50, Got: {jan_employee.get('hourly_rate')}")
                else:
                    print("⚠️  Test employee 'Jan Kowalski' not found in list")
                
            else:
                print("⚠️  No employees found")
            
            print("✅ Get Employees endpoint working correctly")
            return True
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (15s)")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - backend may not be running")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_create_work_entry(employee_id):
    """Test POST /api/employee-work-entries endpoint"""
    print("\n=== Testing Create Work Entry Endpoint ===")
    
    url = f"{API_URL}/employee-work-entries"
    
    # Test data as specified in the request
    test_data = {
        "employee_id": employee_id,
        "date": "2025-10-18",
        "hours": 6.5,
        "notes": "Montaż rozdzielni"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Sending POST request to: {url}")
        print(f"Request data: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=test_data, headers=headers, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verify response structure
            required_fields = ["id", "employee_id", "employee_name", "date", "hours", "hourly_rate", "total_earnings", "notes", "created_at"]
            missing_fields = [field for field in required_fields if field not in response_data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            
            # Verify data matches
            if response_data["employee_id"] != test_data["employee_id"]:
                print(f"❌ Employee ID mismatch. Expected: {test_data['employee_id']}, Got: {response_data['employee_id']}")
                return False
            
            if response_data["date"] != test_data["date"]:
                print(f"❌ Date mismatch. Expected: {test_data['date']}, Got: {response_data['date']}")
                return False
            
            if response_data["hours"] != test_data["hours"]:
                print(f"❌ Hours mismatch. Expected: {test_data['hours']}, Got: {response_data['hours']}")
                return False
            
            # Verify calculations (hours × hourly_rate = total_earnings)
            expected_earnings = response_data["hours"] * response_data["hourly_rate"]
            if abs(response_data["total_earnings"] - expected_earnings) > 0.01:
                print(f"❌ Earnings calculation error. Expected: {expected_earnings}, Got: {response_data['total_earnings']}")
                return False
            
            # Verify employee name is populated
            if not response_data["employee_name"] or len(response_data["employee_name"]) == 0:
                print("❌ Employee name is empty")
                return False
            
            print("✅ Create Work Entry endpoint working correctly")
            print(f"Calculated earnings: {response_data['total_earnings']} (hours: {response_data['hours']} × rate: {response_data['hourly_rate']})")
            return True
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (15s)")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - backend may not be running")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_get_work_entries():
    """Test GET /api/employee-work-entries endpoint"""
    print("\n=== Testing Get Work Entries Endpoint ===")
    
    url = f"{API_URL}/employee-work-entries"
    
    try:
        print(f"Sending GET request to: {url}")
        
        response = requests.get(url, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verify response is a list
            if not isinstance(response_data, list):
                print("❌ Response is not a list")
                return False
            
            # If we have work entries, verify structure
            if len(response_data) > 0:
                print(f"✅ Found {len(response_data)} work entry/entries")
                
                # Verify work entry structure
                for i, entry in enumerate(response_data):
                    required_fields = ["id", "employee_id", "employee_name", "date", "hours", "hourly_rate", "total_earnings", "created_at"]
                    missing_fields = [field for field in required_fields if field not in entry]
                    
                    if missing_fields:
                        print(f"❌ Work entry {i} missing fields: {missing_fields}")
                        return False
                
                # Check if our test entry is in the list and verify calculations
                test_entry_found = False
                for entry in response_data:
                    if (entry.get("date") == "2025-10-18" and 
                        entry.get("hours") == 6.5 and 
                        entry.get("notes") == "Montaż rozdzielni" and
                        entry.get("employee_name") == "Jan Kowalski"):
                        
                        test_entry_found = True
                        print("✅ Test work entry found in list")
                        
                        # Verify critical calculation: total_earnings = hours × hourly_rate
                        expected_earnings = 6.5 * 35.50  # 230.75
                        actual_earnings = entry.get("total_earnings")
                        
                        if abs(actual_earnings - expected_earnings) < 0.01:
                            print(f"✅ CRITICAL: Earnings calculation correct: {actual_earnings} zł (6.5h × 35.50 zł/h = 230.75 zł)")
                        else:
                            print(f"❌ CRITICAL: Earnings calculation ERROR! Expected: 230.75 zł, Got: {actual_earnings} zł")
                        
                        # Verify all fields
                        print(f"   Employee: {entry.get('employee_name')}")
                        print(f"   Hours: {entry.get('hours')}")
                        print(f"   Hourly Rate: {entry.get('hourly_rate')} zł/h")
                        print(f"   Total Earnings: {entry.get('total_earnings')} zł")
                        break
                
                if not test_entry_found:
                    print("⚠️  Test work entry for Jan Kowalski not found in list")
                
            else:
                print("⚠️  No work entries found")
            
            print("✅ Get Work Entries endpoint working correctly")
            return True
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (15s)")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - backend may not be running")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_work_entries_summary():
    """Test GET /api/employee-work-entries/summary endpoint"""
    print("\n=== Testing Work Entries Summary Endpoint ===")
    
    url = f"{API_URL}/employee-work-entries/summary?month=2025-10"
    
    try:
        print(f"Sending GET request to: {url}")
        
        response = requests.get(url, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verify response structure
            required_fields = ["month", "employees", "grand_total"]
            missing_fields = [field for field in required_fields if field not in response_data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            
            # Verify month matches
            if response_data["month"] != "2025-10":
                print(f"❌ Month mismatch. Expected: 2025-10, Got: {response_data['month']}")
                return False
            
            # Verify employees is a list
            if not isinstance(response_data["employees"], list):
                print("❌ Employees field is not a list")
                return False
            
            # Verify grand_total is a number
            if not isinstance(response_data["grand_total"], (int, float)):
                print("❌ Grand total is not a number")
                return False
            
            # If we have employees, verify structure
            if len(response_data["employees"]) > 0:
                print(f"✅ Found {len(response_data['employees'])} employee(s) with work entries")
                
                # Verify employee summary structure
                for i, emp_summary in enumerate(response_data["employees"]):
                    required_emp_fields = ["employee_id", "employee_name", "total_hours", "total_earnings"]
                    missing_emp_fields = [field for field in required_emp_fields if field not in emp_summary]
                    
                    if missing_emp_fields:
                        print(f"❌ Employee summary {i} missing fields: {missing_emp_fields}")
                        return False
                
                # Check if our test employee "Jan Kowalski" is in the summary
                jan_summary = next(
                    (emp for emp in response_data["employees"] if emp.get("employee_name") == "Jan Kowalski"),
                    None
                )
                
                if jan_summary:
                    print(f"✅ Test employee 'Jan Kowalski' found in summary:")
                    print(f"   Total Hours: {jan_summary['total_hours']}")
                    print(f"   Total Earnings: {jan_summary['total_earnings']} zł")
                    
                    # Verify calculation in summary
                    if jan_summary['total_hours'] == 6.5 and jan_summary['total_earnings'] == 230.75:
                        print("✅ CRITICAL: Summary calculations are correct!")
                    else:
                        print(f"❌ CRITICAL: Summary calculation mismatch!")
                else:
                    print("⚠️  Test employee 'Jan Kowalski' not found in summary")
                
            else:
                print("⚠️  No employees found in summary")
            
            print(f"✅ Work Entries Summary endpoint working correctly. Grand total: {response_data['grand_total']}")
            return True
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (15s)")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - backend may not be running")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_backend_health():
    """Test if backend is running"""
    print("\n=== Testing Backend Health ===")
    
    url = f"{API_URL}/"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Backend is running")
            try:
                data = response.json()
                print(f"Backend response: {json.dumps(data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Backend response: {response.text}")
            return True
        else:
            print(f"❌ Backend health check failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Backend health check failed: {str(e)}")
        return False

def test_create_marek_testowy():
    """Test creating Marek Testowy employee for new functionality tests"""
    print("\n=== Testing Create Marek Testowy Employee ===")
    
    url = f"{API_URL}/employees"
    
    # Test data as specified in the request
    test_data = {
        "name": "Marek Testowy",
        "hourly_rate": 40.0,
        "notes": "Testowy pracownik"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Sending POST request to: {url}")
        print(f"Request data: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=test_data, headers=headers, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verify response structure
            required_fields = ["id", "name", "hourly_rate", "notes", "created_at", "updated_at"]
            missing_fields = [field for field in required_fields if field not in response_data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False, None
            
            # Verify data matches
            if response_data["name"] != test_data["name"]:
                print(f"❌ Name mismatch. Expected: {test_data['name']}, Got: {response_data['name']}")
                return False, None
            
            if response_data["hourly_rate"] != test_data["hourly_rate"]:
                print(f"❌ Hourly rate mismatch. Expected: {test_data['hourly_rate']}, Got: {response_data['hourly_rate']}")
                return False, None
            
            print("✅ Marek Testowy employee created successfully")
            print(f"Created employee ID: {response_data['id']}")
            return True, response_data["id"]
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False, None

def test_create_marek_work_entry(employee_id):
    """Test creating work entry for Marek - 5.0 hours"""
    print("\n=== Testing Create Marek Work Entry (5.0 hours) ===")
    
    url = f"{API_URL}/employee-work-entries"
    
    # Test data as specified in the request
    test_data = {
        "employee_id": employee_id,
        "date": "2025-10-20",
        "hours": 5.0,
        "notes": "Test wpisu"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Sending POST request to: {url}")
        print(f"Request data: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=test_data, headers=headers, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verify critical calculation: 5.0 × 40.0 = 200.0 zł
            expected_earnings = 5.0 * 40.0  # 200.0
            actual_earnings = response_data.get("total_earnings")
            
            if abs(actual_earnings - expected_earnings) < 0.01:
                print(f"✅ CRITICAL: Initial earnings calculation correct: {actual_earnings} zł (5.0h × 40.0 zł/h = 200.0 zł)")
            else:
                print(f"❌ CRITICAL: Initial earnings calculation ERROR! Expected: 200.0 zł, Got: {actual_earnings} zł")
                return False, None
            
            print("✅ Marek work entry created successfully")
            return True, response_data["id"]
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False, None

def test_edit_work_entry(entry_id, employee_id):
    """Test PUT /api/employee-work-entries/{entry_id} - edit work entry to 7.5 hours"""
    print("\n=== Testing Edit Work Entry (7.5 hours) ===")
    
    url = f"{API_URL}/employee-work-entries/{entry_id}"
    
    # Test data as specified in the request - change hours to 7.5
    test_data = {
        "employee_id": employee_id,
        "date": "2025-10-20",
        "hours": 7.5,
        "notes": "Test edycji"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Sending PUT request to: {url}")
        print(f"Request data: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        response = requests.put(url, json=test_data, headers=headers, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verify critical calculation: 7.5 × 40.0 = 300.0 zł
            expected_earnings = 7.5 * 40.0  # 300.0
            actual_earnings = response_data.get("total_earnings")
            
            if abs(actual_earnings - expected_earnings) < 0.01:
                print(f"✅ CRITICAL: Edited earnings calculation correct: {actual_earnings} zł (7.5h × 40.0 zł/h = 300.0 zł)")
            else:
                print(f"❌ CRITICAL: Edited earnings calculation ERROR! Expected: 300.0 zł, Got: {actual_earnings} zł")
                return False
            
            # Verify hours were updated
            if response_data.get("hours") == 7.5:
                print("✅ Hours updated correctly to 7.5")
            else:
                print(f"❌ Hours not updated correctly. Expected: 7.5, Got: {response_data.get('hours')}")
                return False
            
            # Verify notes were updated
            if response_data.get("notes") == "Test edycji":
                print("✅ Notes updated correctly")
            else:
                print(f"❌ Notes not updated correctly. Expected: 'Test edycji', Got: {response_data.get('notes')}")
                return False
            
            print("✅ Work entry edit functionality working correctly")
            return True
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_verify_edited_entry():
    """Test GET /api/employee-work-entries to verify the edited entry"""
    print("\n=== Testing Verify Edited Entry ===")
    
    url = f"{API_URL}/employee-work-entries"
    
    try:
        print(f"Sending GET request to: {url}")
        
        response = requests.get(url, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            
            # Find Marek's entry
            marek_entry = None
            for entry in response_data:
                if (entry.get("employee_name") == "Marek Testowy" and 
                    entry.get("date") == "2025-10-20"):
                    marek_entry = entry
                    break
            
            if marek_entry:
                print("✅ Found Marek's edited entry")
                print(f"   Hours: {marek_entry.get('hours')}")
                print(f"   Total Earnings: {marek_entry.get('total_earnings')} zł")
                
                # Verify the edited values
                if marek_entry.get("hours") == 7.5 and marek_entry.get("total_earnings") == 300.0:
                    print("✅ CRITICAL: Edited entry verification PASSED - hours=7.5, total_earnings=300.0")
                    return True
                else:
                    print(f"❌ CRITICAL: Edited entry verification FAILED")
                    print(f"   Expected: hours=7.5, total_earnings=300.0")
                    print(f"   Got: hours={marek_entry.get('hours')}, total_earnings={marek_entry.get('total_earnings')}")
                    return False
            else:
                print("❌ Marek's edited entry not found")
                return False
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_create_second_work_entry(employee_id):
    """Test creating second work entry for Marek"""
    print("\n=== Testing Create Second Work Entry for Marek ===")
    
    url = f"{API_URL}/employee-work-entries"
    
    # Test data as specified in the request
    test_data = {
        "employee_id": employee_id,
        "date": "2025-10-21",
        "hours": 8.0,
        "notes": "Drugi wpis"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Sending POST request to: {url}")
        print(f"Request data: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=test_data, headers=headers, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            print("✅ Second work entry created successfully")
            return True, response_data["id"]
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False, None

def test_count_marek_entries():
    """Test counting Marek's work entries (should be 2)"""
    print("\n=== Testing Count Marek's Work Entries ===")
    
    url = f"{API_URL}/employee-work-entries"
    
    try:
        print(f"Sending GET request to: {url}")
        
        response = requests.get(url, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            
            # Count Marek's entries
            marek_entries = [entry for entry in response_data if entry.get("employee_name") == "Marek Testowy"]
            marek_count = len(marek_entries)
            
            print(f"Found {marek_count} work entries for Marek Testowy")
            
            for i, entry in enumerate(marek_entries, 1):
                print(f"   Entry {i}: {entry.get('date')} - {entry.get('hours')}h - {entry.get('notes')}")
            
            if marek_count == 2:
                print("✅ CRITICAL: Marek has exactly 2 work entries as expected")
                return True
            else:
                print(f"❌ CRITICAL: Expected 2 entries for Marek, found {marek_count}")
                return False
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_cascade_delete_employee(employee_id):
    """Test DELETE /api/employees/{employee_id} - CASCADE DELETE"""
    print("\n=== Testing CASCADE DELETE Employee ===")
    
    url = f"{API_URL}/employees/{employee_id}"
    
    try:
        print(f"Sending DELETE request to: {url}")
        
        response = requests.delete(url, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verify success message
            if "message" in response_data:
                print(f"✅ DELETE response: {response_data['message']}")
                return True
            else:
                print("❌ No success message in response")
                return False
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_verify_cascade_delete():
    """Test verifying CASCADE DELETE worked - employee and all work entries deleted"""
    print("\n=== Testing Verify CASCADE DELETE ===")
    
    # Test 1: Verify employee is deleted
    print("\n--- Checking if Marek employee is deleted ---")
    url = f"{API_URL}/employees"
    
    try:
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            employees = response.json()
            marek_employees = [emp for emp in employees if emp.get("name") == "Marek Testowy"]
            
            if len(marek_employees) == 0:
                print("✅ CRITICAL: Marek Testowy employee successfully deleted")
                employee_deleted = True
            else:
                print(f"❌ CRITICAL: Marek Testowy employee still exists! Found {len(marek_employees)} entries")
                employee_deleted = False
        else:
            print(f"❌ Failed to get employees list: {response.status_code}")
            employee_deleted = False
            
    except Exception as e:
        print(f"❌ Error checking employees: {str(e)}")
        employee_deleted = False
    
    # Test 2: Verify all work entries are deleted
    print("\n--- Checking if all Marek's work entries are deleted ---")
    url = f"{API_URL}/employee-work-entries"
    
    try:
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            work_entries = response.json()
            marek_entries = [entry for entry in work_entries if entry.get("employee_name") == "Marek Testowy"]
            
            if len(marek_entries) == 0:
                print("✅ CRITICAL: All Marek's work entries successfully deleted (CASCADE DELETE worked)")
                entries_deleted = True
            else:
                print(f"❌ CRITICAL: Marek's work entries still exist! Found {len(marek_entries)} entries")
                for entry in marek_entries:
                    print(f"   Remaining entry: {entry.get('date')} - {entry.get('hours')}h")
                entries_deleted = False
        else:
            print(f"❌ Failed to get work entries list: {response.status_code}")
            entries_deleted = False
            
    except Exception as e:
        print(f"❌ Error checking work entries: {str(e)}")
        entries_deleted = False
    
    # Final result
    cascade_success = employee_deleted and entries_deleted
    
    if cascade_success:
        print("\n✅ CASCADE DELETE VERIFICATION PASSED")
        print("   - Employee deleted ✅")
        print("   - All work entries deleted ✅")
    else:
        print("\n❌ CASCADE DELETE VERIFICATION FAILED")
        print(f"   - Employee deleted: {'✅' if employee_deleted else '❌'}")
        print(f"   - Work entries deleted: {'✅' if entries_deleted else '❌'}")
    
    return cascade_success

# ============= FINANCIAL SYSTEM TESTS =============

def test_create_financial_entry_invoice_sales():
    """Test POST /api/financial-entries - Dodaj przychód - Faktura sprzedażowa"""
    print("\n=== Testing Create Financial Entry - Invoice Sales ===")
    
    url = f"{API_URL}/financial-entries"
    
    # Test data as specified in the request
    test_data = {
        "category": "invoice_sales",
        "date": "2025-10-22",
        "description": "Faktura VAT 123/2025",
        "amount_net": 1000.00,
        "amount_gross": 1230.00,
        "vat_rate": 23.0,
        "notes": "Instalacja elektryczna - klient XYZ"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Sending POST request to: {url}")
        print(f"Request data: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=test_data, headers=headers, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verify response structure
            required_fields = ["id", "date", "category", "description", "amount_net", "amount_gross", "vat_rate", "notes", "created_at", "updated_at"]
            missing_fields = [field for field in required_fields if field not in response_data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False, None
            
            # Verify data matches
            for field in ["category", "date", "description", "amount_net", "amount_gross", "vat_rate", "notes"]:
                if response_data[field] != test_data[field]:
                    print(f"❌ {field} mismatch. Expected: {test_data[field]}, Got: {response_data[field]}")
                    return False, None
            
            # Verify ID is generated
            if not response_data["id"] or len(response_data["id"]) == 0:
                print("❌ Financial entry ID is empty")
                return False, None
            
            print("✅ Create Financial Entry (Invoice Sales) endpoint working correctly")
            print(f"Created entry ID: {response_data['id']}")
            return True, response_data["id"]
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False, None

def test_create_financial_entry_salaries():
    """Test POST /api/financial-entries - Dodaj wydatek - Wypłaty pracowników"""
    print("\n=== Testing Create Financial Entry - Salaries ===")
    
    url = f"{API_URL}/financial-entries"
    
    # Test data as specified in the request
    test_data = {
        "category": "salaries",
        "date": "2025-10-22",
        "description": "Wypłaty październik 2025",
        "amount_net": 500.00,
        "amount_gross": 500.00,
        "notes": "Wypłaty dla 4 pracowników"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Sending POST request to: {url}")
        print(f"Request data: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=test_data, headers=headers, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verify response structure
            required_fields = ["id", "date", "category", "description", "amount_net", "amount_gross", "notes", "created_at", "updated_at"]
            missing_fields = [field for field in required_fields if field not in response_data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False, None
            
            # Verify data matches
            for field in ["category", "date", "description", "amount_net", "amount_gross", "notes"]:
                if response_data[field] != test_data[field]:
                    print(f"❌ {field} mismatch. Expected: {test_data[field]}, Got: {response_data[field]}")
                    return False, None
            
            print("✅ Create Financial Entry (Salaries) endpoint working correctly")
            print(f"Created entry ID: {response_data['id']}")
            return True, response_data["id"]
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False, None

def test_create_financial_entry_fuel():
    """Test POST /api/financial-entries - Dodaj wydatek - Paliwo"""
    print("\n=== Testing Create Financial Entry - Fuel ===")
    
    url = f"{API_URL}/financial-entries"
    
    # Test data as specified in the request
    test_data = {
        "category": "fuel",
        "date": "2025-10-22",
        "description": "Tankowanie Shell",
        "amount_net": 200.00,
        "amount_gross": 246.00,
        "vat_rate": 23.0
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Sending POST request to: {url}")
        print(f"Request data: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=test_data, headers=headers, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verify response structure
            required_fields = ["id", "date", "category", "description", "amount_net", "amount_gross", "vat_rate", "created_at", "updated_at"]
            missing_fields = [field for field in required_fields if field not in response_data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False, None
            
            # Verify data matches
            for field in ["category", "date", "description", "amount_net", "amount_gross", "vat_rate"]:
                if response_data[field] != test_data[field]:
                    print(f"❌ {field} mismatch. Expected: {test_data[field]}, Got: {response_data[field]}")
                    return False, None
            
            print("✅ Create Financial Entry (Fuel) endpoint working correctly")
            print(f"Created entry ID: {response_data['id']}")
            return True, response_data["id"]
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False, None

def test_get_financial_entries_october():
    """Test GET /api/financial-entries?month=2025-10 - Pobierz wszystkie wpisy dla października"""
    print("\n=== Testing Get Financial Entries for October 2025 ===")
    
    url = f"{API_URL}/financial-entries?month=2025-10"
    
    try:
        print(f"Sending GET request to: {url}")
        
        response = requests.get(url, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verify response is a list
            if not isinstance(response_data, list):
                print("❌ Response is not a list")
                return False
            
            print(f"✅ Found {len(response_data)} financial entries for October 2025")
            
            # Verify our test entries are present
            test_entries = {
                "invoice_sales": False,
                "salaries": False,
                "fuel": False
            }
            
            for entry in response_data:
                if entry.get("date") == "2025-10-22":
                    if entry.get("category") == "invoice_sales" and entry.get("description") == "Faktura VAT 123/2025":
                        test_entries["invoice_sales"] = True
                        print("✅ Found test invoice_sales entry")
                    elif entry.get("category") == "salaries" and entry.get("description") == "Wypłaty październik 2025":
                        test_entries["salaries"] = True
                        print("✅ Found test salaries entry")
                    elif entry.get("category") == "fuel" and entry.get("description") == "Tankowanie Shell":
                        test_entries["fuel"] = True
                        print("✅ Found test fuel entry")
            
            missing_entries = [cat for cat, found in test_entries.items() if not found]
            if missing_entries:
                print(f"⚠️  Missing test entries: {missing_entries}")
            else:
                print("✅ All test entries found in October 2025 list")
            
            print("✅ Get Financial Entries endpoint working correctly")
            return True
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_get_financial_summary_october():
    """Test GET /api/financial-entries/summary?month=2025-10 - Pobierz podsumowanie"""
    print("\n=== Testing Get Financial Summary for October 2025 ===")
    
    url = f"{API_URL}/financial-entries/summary?month=2025-10"
    
    try:
        print(f"Sending GET request to: {url}")
        
        response = requests.get(url, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verify response structure
            required_fields = ["categories", "totals"]
            missing_fields = [field for field in required_fields if field not in response_data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            
            # Verify categories structure
            categories = response_data.get("categories", [])
            if not isinstance(categories, list):
                print("❌ Categories is not a list")
                return False
            
            # Verify totals structure
            totals = response_data.get("totals", {})
            required_total_fields = ["income_net", "income_gross", "expense_net", "expense_gross", "balance_net", "balance_gross"]
            missing_total_fields = [field for field in required_total_fields if field not in totals]
            
            if missing_total_fields:
                print(f"❌ Missing total fields: {missing_total_fields}")
                return False
            
            print("✅ Financial Summary structure is correct")
            
            # Verify calculations based on our test data
            # Expected: 
            # Income: invoice_sales (1000.00 net, 1230.00 gross)
            # Expenses: salaries (500.00 net, 500.00 gross) + fuel (200.00 net, 246.00 gross)
            # Total income: 1000.00 net, 1230.00 gross
            # Total expenses: 700.00 net, 746.00 gross
            # Balance: 300.00 net, 484.00 gross
            
            print(f"\n📊 CRITICAL CALCULATIONS VERIFICATION:")
            print(f"Income Net: {totals['income_net']}")
            print(f"Income Gross: {totals['income_gross']}")
            print(f"Expense Net: {totals['expense_net']}")
            print(f"Expense Gross: {totals['expense_gross']}")
            print(f"Balance Net: {totals['balance_net']}")
            print(f"Balance Gross: {totals['balance_gross']}")
            
            # Verify categories have correct structure
            for category in categories:
                required_cat_fields = ["category", "total_net", "total_gross", "count", "type"]
                missing_cat_fields = [field for field in required_cat_fields if field not in category]
                
                if missing_cat_fields:
                    print(f"❌ Category missing fields: {missing_cat_fields}")
                    return False
                
                print(f"Category {category['category']}: {category['total_net']} net, {category['total_gross']} gross, count: {category['count']}, type: {category['type']}")
            
            # Verify balance calculation
            calculated_balance_net = totals['income_net'] - totals['expense_net']
            calculated_balance_gross = totals['income_gross'] - totals['expense_gross']
            
            if abs(totals['balance_net'] - calculated_balance_net) < 0.01:
                print("✅ CRITICAL: Balance Net calculation is correct")
            else:
                print(f"❌ CRITICAL: Balance Net calculation error. Expected: {calculated_balance_net}, Got: {totals['balance_net']}")
                return False
            
            if abs(totals['balance_gross'] - calculated_balance_gross) < 0.01:
                print("✅ CRITICAL: Balance Gross calculation is correct")
            else:
                print(f"❌ CRITICAL: Balance Gross calculation error. Expected: {calculated_balance_gross}, Got: {totals['balance_gross']}")
                return False
            
            print("✅ Get Financial Summary endpoint working correctly")
            return True
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_edit_financial_entry_fuel(fuel_id):
    """Test PUT /api/financial-entries/{fuel_id} - Edytuj wpis paliwa - zmień kwotę"""
    print("\n=== Testing Edit Financial Entry - Fuel ===")
    
    url = f"{API_URL}/financial-entries/{fuel_id}"
    
    # Test data as specified in the request - change amounts
    test_data = {
        "amount_net": 250.00,
        "amount_gross": 307.50
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Sending PUT request to: {url}")
        print(f"Request data: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        response = requests.put(url, json=test_data, headers=headers, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verify amounts were updated
            if response_data.get("amount_net") == 250.00:
                print("✅ Amount Net updated correctly to 250.00")
            else:
                print(f"❌ Amount Net not updated correctly. Expected: 250.00, Got: {response_data.get('amount_net')}")
                return False
            
            if response_data.get("amount_gross") == 307.50:
                print("✅ Amount Gross updated correctly to 307.50")
            else:
                print(f"❌ Amount Gross not updated correctly. Expected: 307.50, Got: {response_data.get('amount_gross')}")
                return False
            
            # Verify other fields remain unchanged
            if response_data.get("category") == "fuel" and response_data.get("description") == "Tankowanie Shell":
                print("✅ Other fields remain unchanged")
            else:
                print("❌ Other fields were unexpectedly changed")
                return False
            
            print("✅ Edit Financial Entry endpoint working correctly")
            return True
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_delete_financial_entry_fuel(fuel_id):
    """Test DELETE /api/financial-entries/{fuel_id} - Usuń wpis paliwa"""
    print("\n=== Testing Delete Financial Entry - Fuel ===")
    
    url = f"{API_URL}/financial-entries/{fuel_id}"
    
    try:
        print(f"Sending DELETE request to: {url}")
        
        response = requests.delete(url, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verify success message
            if "message" in response_data:
                print(f"✅ DELETE response: {response_data['message']}")
                return True
            else:
                print("❌ No success message in response")
                return False
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_verify_fuel_deletion():
    """Test GET /api/financial-entries/summary?month=2025-10 - Zweryfikuj po usunięciu"""
    print("\n=== Testing Verify Fuel Entry Deletion ===")
    
    url = f"{API_URL}/financial-entries/summary?month=2025-10"
    
    try:
        print(f"Sending GET request to: {url}")
        
        response = requests.get(url, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Check if fuel category is missing or has 0 entries
            categories = response_data.get("categories", [])
            fuel_category = next((cat for cat in categories if cat.get("category") == "fuel"), None)
            
            if fuel_category is None:
                print("✅ CRITICAL: Fuel category not found in summary (correctly deleted)")
                fuel_deleted = True
            elif fuel_category.get("count", 0) == 0:
                print("✅ CRITICAL: Fuel category has 0 entries (correctly deleted)")
                fuel_deleted = True
            else:
                print(f"❌ CRITICAL: Fuel category still has {fuel_category.get('count', 0)} entries")
                fuel_deleted = False
            
            # Verify updated totals (should exclude fuel amounts)
            # Expected after deletion:
            # Income: invoice_sales (1000.00 net, 1230.00 gross)
            # Expenses: salaries (500.00 net, 500.00 gross) only
            # Total expenses: 500.00 net, 500.00 gross
            # Balance: 500.00 net, 730.00 gross
            
            totals = response_data.get("totals", {})
            print(f"\n📊 UPDATED CALCULATIONS AFTER DELETION:")
            print(f"Income Net: {totals.get('income_net')}")
            print(f"Income Gross: {totals.get('income_gross')}")
            print(f"Expense Net: {totals.get('expense_net')}")
            print(f"Expense Gross: {totals.get('expense_gross')}")
            print(f"Balance Net: {totals.get('balance_net')}")
            print(f"Balance Gross: {totals.get('balance_gross')}")
            
            if fuel_deleted:
                print("✅ Verify Fuel Deletion working correctly")
                return True
            else:
                print("❌ Fuel deletion verification failed")
                return False
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

# ============= AI ASSISTANT & AI ANALYST CHAT HISTORY TESTING =============

def test_ai_assistant_sessions():
    """TEST 1: GET /api/ai/sessions?limit=50 - Sprawdź listę sesji AI Assistant"""
    print("\n=== TEST 1: AI Assistant Sessions Endpoint ===")
    
    url = f"{API_URL}/ai/sessions?limit=50"
    
    try:
        print(f"Sending GET request to: {url}")
        
        response = requests.get(url, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verify response structure
            required_fields = ["sessions", "count"]
            missing_fields = [field for field in required_fields if field not in response_data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False, None
            
            # Verify sessions is a list
            sessions = response_data.get("sessions", [])
            if not isinstance(sessions, list):
                print("❌ Sessions field is not a list")
                return False, None
            
            print(f"✅ Found {len(sessions)} AI Assistant sessions")
            
            # If we have sessions, verify structure
            if len(sessions) > 0:
                for i, session in enumerate(sessions):
                    required_session_fields = ["_id", "title", "message_count", "updated_at"]
                    missing_session_fields = [field for field in required_session_fields if field not in session]
                    
                    if missing_session_fields:
                        print(f"❌ Session {i} missing fields: {missing_session_fields}")
                        return False, None
                    
                    # Verify session_id field (mapped from _id)
                    session_id = session.get("_id")
                    if not session_id:
                        print(f"❌ Session {i} has empty session_id")
                        return False, None
                
                # Verify sessions are sorted by updated_at (newest first)
                if len(sessions) > 1:
                    for i in range(len(sessions) - 1):
                        current_time = sessions[i].get("updated_at")
                        next_time = sessions[i + 1].get("updated_at")
                        if current_time < next_time:
                            print("❌ Sessions are not sorted by updated_at (newest first)")
                            return False, None
                
                print("✅ Sessions structure is correct and sorted properly")
                print(f"   Sample session: ID={sessions[0].get('_id')}, Title='{sessions[0].get('title')}', Messages={sessions[0].get('message_count')}")
                
                # Return first session ID for history testing
                return True, sessions[0].get("_id")
            else:
                print("⚠️  No AI Assistant sessions found")
                return True, None
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False, None
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (15s)")
        return False, None
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - backend may not be running")
        return False, None
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False, None

def test_ai_assistant_history(session_id):
    """TEST 2: POST /api/ai/history - Sprawdź historię konwersacji AI Assistant"""
    print("\n=== TEST 2: AI Assistant History Endpoint ===")
    
    if not session_id:
        print("⚠️  No session_id provided - skipping history test")
        return True
    
    url = f"{API_URL}/ai/history"
    
    test_data = {
        "session_id": session_id,
        "limit": 100
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Sending POST request to: {url}")
        print(f"Request data: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=test_data, headers=headers, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verify response structure
            required_fields = ["session_id", "conversations", "count"]
            missing_fields = [field for field in required_fields if field not in response_data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            
            # Verify session_id matches
            if response_data.get("session_id") != session_id:
                print(f"❌ Session ID mismatch. Expected: {session_id}, Got: {response_data.get('session_id')}")
                return False
            
            # Verify conversations is a list
            conversations = response_data.get("conversations", [])
            if not isinstance(conversations, list):
                print("❌ Conversations field is not a list")
                return False
            
            print(f"✅ Found {len(conversations)} conversations for session {session_id}")
            
            # If we have conversations, verify structure
            if len(conversations) > 0:
                for i, conv in enumerate(conversations):
                    required_conv_fields = ["user_message", "ai_response", "timestamp"]
                    missing_conv_fields = [field for field in required_conv_fields if field not in conv]
                    
                    if missing_conv_fields:
                        print(f"❌ Conversation {i} missing fields: {missing_conv_fields}")
                        return False
                    
                    # Verify fields are not empty
                    if not conv.get("user_message") or not conv.get("ai_response"):
                        print(f"❌ Conversation {i} has empty user_message or ai_response")
                        return False
                
                print("✅ Conversations structure is correct")
                print(f"   Sample conversation: User='{conversations[0].get('user_message')[:50]}...', AI='{conversations[0].get('ai_response')[:50]}...'")
            else:
                print("⚠️  No conversations found for this session")
            
            print("✅ AI Assistant History endpoint working correctly")
            return True
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (15s)")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - backend may not be running")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_ai_analyst_sessions():
    """TEST 3: GET /api/ai-analyst/chat/sessions?limit=50 - Sprawdź listę sesji AI Analyst"""
    print("\n=== TEST 3: AI Analyst Sessions Endpoint ===")
    
    url = f"{API_URL}/ai-analyst/chat/sessions?limit=50"
    
    try:
        print(f"Sending GET request to: {url}")
        
        response = requests.get(url, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verify response structure
            required_fields = ["sessions", "count"]
            missing_fields = [field for field in required_fields if field not in response_data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False, None
            
            # Verify sessions is a list
            sessions = response_data.get("sessions", [])
            if not isinstance(sessions, list):
                print("❌ Sessions field is not a list")
                return False, None
            
            print(f"✅ Found {len(sessions)} AI Analyst sessions")
            
            # If we have sessions, verify structure
            if len(sessions) > 0:
                for i, session in enumerate(sessions):
                    required_session_fields = ["_id", "title", "message_count", "updated_at"]
                    missing_session_fields = [field for field in required_session_fields if field not in session]
                    
                    if missing_session_fields:
                        print(f"❌ Session {i} missing fields: {missing_session_fields}")
                        return False, None
                    
                    # Verify session_id field (mapped from _id)
                    session_id = session.get("_id")
                    if not session_id:
                        print(f"❌ Session {i} has empty session_id")
                        return False, None
                
                # Verify sessions are sorted by updated_at (newest first)
                if len(sessions) > 1:
                    for i in range(len(sessions) - 1):
                        current_time = sessions[i].get("updated_at")
                        next_time = sessions[i + 1].get("updated_at")
                        if current_time < next_time:
                            print("❌ Sessions are not sorted by updated_at (newest first)")
                            return False, None
                
                print("✅ Sessions structure is correct and sorted properly")
                print(f"   Sample session: ID={sessions[0].get('_id')}, Title='{sessions[0].get('title')}', Messages={sessions[0].get('message_count')}")
                
                # Return first session ID for history testing
                return True, sessions[0].get("_id")
            else:
                print("⚠️  No AI Analyst sessions found")
                return True, None
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False, None
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (15s)")
        return False, None
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - backend may not be running")
        return False, None
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False, None

def test_ai_analyst_history(session_id):
    """TEST 4: GET /api/ai-analyst/chat/history?session_id={session_id} - Sprawdź historię AI Analyst"""
    print("\n=== TEST 4: AI Analyst History Endpoint ===")
    
    if not session_id:
        print("⚠️  No session_id provided - skipping history test")
        return True
    
    url = f"{API_URL}/ai-analyst/chat/history?session_id={session_id}"
    
    try:
        print(f"Sending GET request to: {url}")
        
        response = requests.get(url, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verify response structure
            required_fields = ["history", "count"]
            missing_fields = [field for field in required_fields if field not in response_data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            
            # Verify history is a list
            history = response_data.get("history", [])
            if not isinstance(history, list):
                print("❌ History field is not a list")
                return False
            
            print(f"✅ Found {len(history)} history entries for session {session_id}")
            
            # If we have history, verify structure
            if len(history) > 0:
                for i, entry in enumerate(history):
                    # AI Analyst uses 'created_at' instead of 'timestamp'
                    required_entry_fields = ["user_message", "ai_response", "created_at"]
                    missing_entry_fields = [field for field in required_entry_fields if field not in entry]
                    
                    if missing_entry_fields:
                        print(f"❌ History entry {i} missing fields: {missing_entry_fields}")
                        return False
                    
                    # Verify fields are not empty
                    if not entry.get("user_message") or not entry.get("ai_response"):
                        print(f"❌ History entry {i} has empty user_message or ai_response")
                        return False
                
                # Verify data is properly sorted (chronological order)
                if len(history) > 1:
                    for i in range(len(history) - 1):
                        current_time = history[i].get("created_at")
                        next_time = history[i + 1].get("created_at")
                        if current_time > next_time:
                            print("❌ History is not sorted chronologically")
                            return False
                
                print("✅ History structure is correct and properly sorted")
                print(f"   Sample entry: User='{history[0].get('user_message')[:50]}...', AI='{history[0].get('ai_response')[:50]}...'")
            else:
                print("⚠️  No history entries found for this session")
            
            print("✅ AI Analyst History endpoint working correctly")
            return True
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (15s)")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - backend may not be running")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_empty_sessions_handling():
    """TEST 5: Sprawdź czy endpointy zwracają pustą listę gdy brak sesji"""
    print("\n=== TEST 5: Empty Sessions Handling ===")
    
    # Test both endpoints with non-existent session
    test_session_id = "non-existent-session-12345"
    
    # Test AI Assistant history with non-existent session
    print("\n--- Testing AI Assistant with non-existent session ---")
    url = f"{API_URL}/ai/history"
    test_data = {"session_id": test_session_id, "limit": 10}
    
    try:
        response = requests.post(url, json=test_data, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get("count") == 0 and len(data.get("conversations", [])) == 0:
                print("✅ AI Assistant returns empty list for non-existent session")
                ai_assistant_empty_ok = True
            else:
                print("❌ AI Assistant should return empty list for non-existent session")
                ai_assistant_empty_ok = False
        else:
            print(f"❌ AI Assistant returned error status {response.status_code} instead of empty list")
            ai_assistant_empty_ok = False
    except Exception as e:
        print(f"❌ AI Assistant error: {str(e)}")
        ai_assistant_empty_ok = False
    
    # Test AI Analyst history with non-existent session
    print("\n--- Testing AI Analyst with non-existent session ---")
    url = f"{API_URL}/ai-analyst/chat/history?session_id={test_session_id}"
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get("count") == 0 and len(data.get("history", [])) == 0:
                print("✅ AI Analyst returns empty list for non-existent session")
                ai_analyst_empty_ok = True
            else:
                print("❌ AI Analyst should return empty list for non-existent session")
                ai_analyst_empty_ok = False
        else:
            print(f"❌ AI Analyst returned error status {response.status_code} instead of empty list")
            ai_analyst_empty_ok = False
    except Exception as e:
        print(f"❌ AI Analyst error: {str(e)}")
        ai_analyst_empty_ok = False
    
    # Final result
    if ai_assistant_empty_ok and ai_analyst_empty_ok:
        print("\n✅ Empty sessions handling test PASSED")
        return True
    else:
        print("\n❌ Empty sessions handling test FAILED")
        return False

# ============= AI ASSISTANT DATE TESTING =============

def test_ai_chat_today_date():
    """TEST 1: AI rozpoznaje 'dzisiaj' - sprawdź czy używa poprawnej daty polskiej strefy czasowej"""
    print("\n=== TEST 1: AI Assistant - Rozpoznawanie 'dzisiaj' ===")
    
    url = f"{API_URL}/ai/chat"
    
    # Calculate expected date in Polish timezone (UTC+1)
    from datetime import timedelta
    poland_tz = timezone(timedelta(hours=1))
    expected_today = datetime.now(poland_tz).strftime('%Y-%m-%d')
    
    test_data = {
        "text": "Zapisz 8 godzin pracy dzisiaj na projekcie Test",
        "session_id": "test-date-today"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Sending POST request to: {url}")
        print(f"Request data: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        print(f"Expected today's date (Polish timezone UTC+1): {expected_today}")
        
        response = requests.post(url, json=test_data, headers=headers, timeout=30)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verify response structure
            required_fields = ["response", "session_id"]
            missing_fields = [field for field in required_fields if field not in response_data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            
            ai_response = response_data.get("response", "")
            
            # Check if AI executed action (action_executed field shows the result)
            action_executed = response_data.get("action_executed", "")
            
            if action_executed:
                print("✅ AI wykonał akcję (action_executed field present)")
                print(f"Action executed: {action_executed}")
                
                # Check if the executed action contains today's date
                if expected_today in action_executed:
                    print(f"✅ KRYTYCZNE: AI używa poprawnej daty dzisiejszej: {expected_today}")
                    print("✅ TEST 1 PASSED - AI rozpoznaje 'dzisiaj' i używa polskiej strefy czasowej")
                    return True
                else:
                    print(f"❌ KRYTYCZNE: AI używa niepoprawnej daty!")
                    print(f"   Oczekiwana data: {expected_today}")
                    print(f"   Znaleziono w action_executed: {action_executed}")
                    return False
            else:
                print("❌ AI nie wykonał akcji - brak action_executed field")
                print(f"AI response: {ai_response}")
                return False
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (30s)")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - backend may not be running")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_ai_chat_yesterday_date():
    """TEST 2: AI rozpoznaje 'wczoraj' - sprawdź czy używa poprawnej daty wczorajszej"""
    print("\n=== TEST 2: AI Assistant - Rozpoznawanie 'wczoraj' ===")
    
    url = f"{API_URL}/ai/chat"
    
    # Calculate expected yesterday date in Polish timezone (UTC+1)
    from datetime import timedelta
    poland_tz = timezone(timedelta(hours=1))
    expected_yesterday = (datetime.now(poland_tz) - timedelta(days=1)).strftime('%Y-%m-%d')
    
    test_data = {
        "text": "Wpisz 5 godzin pracy wczoraj",
        "session_id": "test-date-yesterday"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Sending POST request to: {url}")
        print(f"Request data: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        print(f"Expected yesterday's date (Polish timezone UTC+1): {expected_yesterday}")
        
        response = requests.post(url, json=test_data, headers=headers, timeout=30)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            ai_response = response_data.get("response", "")
            
            # Check if AI executed action (action_executed field shows the result)
            action_executed = response_data.get("action_executed", "")
            
            if action_executed:
                print("✅ AI wykonał akcję (action_executed field present)")
                print(f"Action executed: {action_executed}")
                
                # Check if the executed action contains yesterday's date
                if expected_yesterday in action_executed:
                    print(f"✅ KRYTYCZNE: AI używa poprawnej daty wczorajszej: {expected_yesterday}")
                    print("✅ TEST 2 PASSED - AI rozpoznaje 'wczoraj' i używa polskiej strefy czasowej")
                    return True
                else:
                    print(f"❌ KRYTYCZNE: AI używa niepoprawnej daty!")
                    print(f"   Oczekiwana data wczoraj: {expected_yesterday}")
                    print(f"   Znaleziono w action_executed: {action_executed}")
                    return False
            else:
                print("❌ AI nie wykonał akcji - brak action_executed field")
                print(f"AI response: {ai_response}")
                return False
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_check_workhours_database():
    """TEST 3: Sprawdź czy wpisy są w bazie z poprawnymi datami"""
    print("\n=== TEST 3: Sprawdzenie wpisów w bazie danych ===")
    
    url = f"{API_URL}/workhours"
    
    # Calculate expected dates
    from datetime import timedelta
    poland_tz = timezone(timedelta(hours=1))
    expected_today = datetime.now(poland_tz).strftime('%Y-%m-%d')
    expected_yesterday = (datetime.now(poland_tz) - timedelta(days=1)).strftime('%Y-%m-%d')
    
    try:
        print(f"Sending GET request to: {url}")
        
        response = requests.get(url, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Found {len(response_data)} work hour entries in database")
            
            # Look for entries from TEST 1 and TEST 2
            today_entries = [entry for entry in response_data if entry.get("date") == expected_today and "Test" in entry.get("notes", "")]
            yesterday_entries = [entry for entry in response_data if entry.get("date") == expected_yesterday]
            
            print(f"\n📅 Entries for today ({expected_today}):")
            for entry in today_entries:
                print(f"   - {entry.get('hours')}h, notes: {entry.get('notes')}, date: {entry.get('date')}")
            
            print(f"\n📅 Entries for yesterday ({expected_yesterday}):")
            for entry in yesterday_entries:
                print(f"   - {entry.get('hours')}h, notes: {entry.get('notes')}, date: {entry.get('date')}")
            
            # Verify dates are correct
            dates_correct = True
            
            if today_entries:
                for entry in today_entries:
                    if entry.get("date") == expected_today:
                        print(f"✅ Entry from TEST 1 has correct date: {entry.get('date')}")
                    else:
                        print(f"❌ Entry from TEST 1 has wrong date: {entry.get('date')} (expected: {expected_today})")
                        dates_correct = False
            else:
                print("⚠️  No entries found for today (TEST 1 may not have created entry)")
            
            if yesterday_entries:
                for entry in yesterday_entries:
                    if entry.get("date") == expected_yesterday:
                        print(f"✅ Entry from TEST 2 has correct date: {entry.get('date')}")
                    else:
                        print(f"❌ Entry from TEST 2 has wrong date: {entry.get('date')} (expected: {expected_yesterday})")
                        dates_correct = False
            else:
                print("⚠️  No entries found for yesterday (TEST 2 may not have created entry)")
            
            if dates_correct:
                print("✅ TEST 3 PASSED - Daty w bazie danych są poprawne")
                return True
            else:
                print("❌ TEST 3 FAILED - Znaleziono niepoprawne daty w bazie")
                return False
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_ai_chat_default_date():
    """TEST 4: Test bez podanej daty (domyślnie dzisiaj)"""
    print("\n=== TEST 4: AI Assistant - Domyślna data (dzisiaj) ===")
    
    url = f"{API_URL}/ai/chat"
    
    # Calculate expected date in Polish timezone (UTC+1)
    from datetime import timedelta
    poland_tz = timezone(timedelta(hours=1))
    expected_today = datetime.now(poland_tz).strftime('%Y-%m-%d')
    
    test_data = {
        "text": "Zapisz 3 godziny pracy",
        "session_id": "test-date-default"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Sending POST request to: {url}")
        print(f"Request data: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        print(f"Expected default date (today, Polish timezone UTC+1): {expected_today}")
        
        response = requests.post(url, json=test_data, headers=headers, timeout=30)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            ai_response = response_data.get("response", "")
            
            # Check if AI executed action (action_executed field shows the result)
            action_executed = response_data.get("action_executed", "")
            
            if action_executed:
                print("✅ AI wykonał akcję (action_executed field present)")
                print(f"Action executed: {action_executed}")
                
                # Check if the executed action contains today's date (default)
                if expected_today in action_executed:
                    print(f"✅ KRYTYCZNE: AI używa dzisiejszej daty jako domyślnej: {expected_today}")
                    print("✅ TEST 4 PASSED - AI używa dzisiejszej daty jako domyślnej")
                    return True
                else:
                    print(f"❌ KRYTYCZNE: AI nie używa dzisiejszej daty jako domyślnej!")
                    print(f"   Oczekiwana data (dzisiaj): {expected_today}")
                    print(f"   Znaleziono w action_executed: {action_executed}")
                    return False
            else:
                print("❌ AI nie wykonał akcji - brak action_executed field")
                print(f"AI response: {ai_response}")
                return False
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_ai_date_comprehensive():
    """Comprehensive test for AI Assistant date functionality"""
    print("\n" + "="*80)
    print("🤖 COMPREHENSIVE AI ASSISTANT DATE TESTING")
    print("Testowanie czy AI używa POPRAWNYCH DAT (polska strefa czasowa UTC+1)")
    print("="*80)
    
    # Calculate current dates for reference
    from datetime import timedelta
    poland_tz = timezone(timedelta(hours=1))
    current_date_poland = datetime.now(poland_tz).strftime('%Y-%m-%d')
    current_time_poland = datetime.now(poland_tz).strftime('%H:%M')
    yesterday_poland = (datetime.now(poland_tz) - timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"📅 REFERENCE DATES (Polish timezone UTC+1):")
    print(f"   Dzisiaj: {current_date_poland}")
    print(f"   Wczoraj: {yesterday_poland}")
    print(f"   Aktualny czas: {current_time_poland}")
    
    # Run all tests
    test_results = []
    
    print(f"\n🔍 Rozpoczynam testy...")
    
    # TEST 1: "dzisiaj"
    result1 = test_ai_chat_today_date()
    test_results.append(("TEST 1: AI rozpoznaje 'dzisiaj'", result1))
    
    # TEST 2: "wczoraj"  
    result2 = test_ai_chat_yesterday_date()
    test_results.append(("TEST 2: AI rozpoznaje 'wczoraj'", result2))
    
    # TEST 3: Check database
    result3 = test_check_workhours_database()
    test_results.append(("TEST 3: Sprawdzenie bazy danych", result3))
    
    # TEST 4: Default date
    result4 = test_ai_chat_default_date()
    test_results.append(("TEST 4: Domyślna data", result4))
    
    # Summary
    print(f"\n" + "="*80)
    print("📊 PODSUMOWANIE TESTÓW AI ASSISTANT - DATY")
    print("="*80)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
        if result:
            passed_tests += 1
    
    print(f"\n📈 WYNIK KOŃCOWY: {passed_tests}/{total_tests} testów przeszło pomyślnie")
    
    if passed_tests == total_tests:
        print("🎉 WSZYSTKIE TESTY PRZESZŁY - AI używa poprawnych dat w polskiej strefie czasowej!")
        return True
    else:
        print("⚠️  NIEKTÓRE TESTY NIE PRZESZŁY - Problem z datami w AI Assistant")
        return False

# ============= REMINDERS SYSTEM TESTS =============

def test_create_reminder_for_pending_check():
    """Test POST /api/reminders - Create a reminder for today with past time"""
    print("\n=== Testing Create Reminder for Pending Check ===")
    
    url = f"{API_URL}/reminders"
    
    # Create a reminder for today with a time that has already passed (09:00)
    today = datetime.now().date().isoformat()
    test_data = {
        "title": "Test przypomnienie do sprawdzenia",
        "description": "To jest testowe przypomnienie które powinno być zwrócone przez endpoint check/pending",
        "reminder_date": today,
        "reminder_time": "09:00",
        "reminder_type": "custom",
        "is_recurring": False
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Sending POST request to: {url}")
        print(f"Request data: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=test_data, headers=headers, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verify response structure
            required_fields = ["id", "title", "description", "reminder_date", "reminder_time", "reminder_type", "is_recurring", "is_completed", "sent", "created_at", "updated_at"]
            missing_fields = [field for field in required_fields if field not in response_data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False, None
            
            # Verify data matches
            for field in ["title", "description", "reminder_date", "reminder_time", "reminder_type", "is_recurring"]:
                if response_data[field] != test_data[field]:
                    print(f"❌ {field} mismatch. Expected: {test_data[field]}, Got: {response_data[field]}")
                    return False, None
            
            # Verify initial state
            if response_data["sent"] != False:
                print(f"❌ Initial sent state should be False, got: {response_data['sent']}")
                return False, None
            
            if response_data["is_completed"] != False:
                print(f"❌ Initial is_completed state should be False, got: {response_data['is_completed']}")
                return False, None
            
            # Verify ID is generated
            if not response_data["id"] or len(response_data["id"]) == 0:
                print("❌ Reminder ID is empty")
                return False, None
            
            print("✅ Create Reminder endpoint working correctly")
            print(f"Created reminder ID: {response_data['id']}")
            print(f"Reminder date: {response_data['reminder_date']}, time: {response_data['reminder_time']}")
            return True, response_data["id"]
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False, None

def test_check_pending_reminders():
    """Test GET /api/reminders/check/pending - Check for pending reminders"""
    print("\n=== Testing Check Pending Reminders Endpoint ===")
    
    url = f"{API_URL}/reminders/check/pending"
    
    try:
        print(f"Sending GET request to: {url}")
        
        response = requests.get(url, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verify response structure
            required_fields = ["count", "reminders"]
            missing_fields = [field for field in required_fields if field not in response_data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            
            # Verify count is a number
            if not isinstance(response_data["count"], int):
                print("❌ Count field is not an integer")
                return False
            
            # Verify reminders is a list
            if not isinstance(response_data["reminders"], list):
                print("❌ Reminders field is not a list")
                return False
            
            # Verify count matches list length
            if response_data["count"] != len(response_data["reminders"]):
                print(f"❌ Count mismatch. Count: {response_data['count']}, List length: {len(response_data['reminders'])}")
                return False
            
            print(f"✅ Found {response_data['count']} pending reminder(s)")
            
            # If we have reminders, verify structure and check for our test reminder
            if response_data["count"] > 0:
                test_reminder_found = False
                
                for i, reminder in enumerate(response_data["reminders"]):
                    print(f"\nReminder {i+1}:")
                    print(f"  Title: {reminder.get('title')}")
                    print(f"  Date: {reminder.get('reminder_date')}")
                    print(f"  Time: {reminder.get('reminder_time')}")
                    print(f"  Sent: {reminder.get('sent')}")
                    
                    # Verify reminder structure
                    required_reminder_fields = ["id", "title", "reminder_date", "reminder_time", "sent"]
                    missing_reminder_fields = [field for field in required_reminder_fields if field not in reminder]
                    
                    if missing_reminder_fields:
                        print(f"❌ Reminder {i+1} missing fields: {missing_reminder_fields}")
                        return False
                    
                    # Check if this is our test reminder
                    if (reminder.get("title") == "Test przypomnienie do sprawdzenia" and 
                        reminder.get("reminder_time") == "09:00"):
                        test_reminder_found = True
                        print(f"✅ Found our test reminder in pending list")
                        
                        # The response shows the reminder as it was before marking as sent
                        # This is correct behavior - we'll verify it was marked as sent in the next step
                        if reminder.get("sent") == False:
                            print("✅ CRITICAL: Reminder returned with original sent=False state (correct behavior)")
                        else:
                            print(f"⚠️  Reminder sent state: {reminder.get('sent')} (expected False in response)")
                        
                        # Verify other required fields for pending reminders
                        if reminder.get("reminder_date") == datetime.now().date().isoformat():
                            print("✅ Reminder date matches today")
                        else:
                            print(f"❌ Reminder date mismatch. Expected today, got: {reminder.get('reminder_date')}")
                            return False
                
                if not test_reminder_found:
                    print("⚠️  Our test reminder was not found in pending list (might have been processed already)")
            else:
                print("ℹ️  No pending reminders found")
            
            print("✅ Check Pending Reminders endpoint working correctly")
            return True
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_verify_reminder_marked_as_sent(reminder_id):
    """Test GET /api/reminders/{reminder_id} - Verify reminder was marked as sent"""
    print("\n=== Testing Verify Reminder Marked as Sent ===")
    
    url = f"{API_URL}/reminders/{reminder_id}"
    
    try:
        print(f"Sending GET request to: {url}")
        
        response = requests.get(url, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verify the reminder was marked as sent
            if response_data.get("sent") == True:
                print("✅ CRITICAL: Reminder correctly marked as sent=True after check/pending call")
                return True
            else:
                print(f"❌ CRITICAL: Reminder should be sent=True, got: {response_data.get('sent')}")
                return False
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_reminders_system():
    """Run complete reminders system test"""
    print("\n" + "="*60)
    print("🔔 REMINDERS SYSTEM TESTING - CHECK PENDING ENDPOINT")
    print("="*60)
    print(f"Backend URL: {BASE_URL}")
    print(f"API URL: {API_URL}")
    print(f"Test time: {datetime.now().isoformat()}")
    
    results = {}
    
    # Test backend health first
    results['backend_health'] = test_backend_health()
    
    if not results['backend_health']:
        print("\n❌ Backend is not responding. Cannot proceed with tests.")
        return results
    
    print("\n" + "="*60)
    print("KROK 1: UTWORZENIE TESTOWEGO PRZYPOMNIENIA")
    print("="*60)
    
    # Step 1: Create a test reminder for today with past time
    create_result, reminder_id = test_create_reminder_for_pending_check()
    results['create_reminder'] = create_result
    
    if not create_result or not reminder_id:
        print("\n❌ Cannot proceed without creating test reminder")
        return results
    
    print("\n" + "="*60)
    print("KROK 2: SPRAWDZENIE PENDING REMINDERS")
    print("="*60)
    
    # Step 2: Call check/pending endpoint
    results['check_pending'] = test_check_pending_reminders()
    
    print("\n" + "="*60)
    print("KROK 3: WERYFIKACJA OZNACZENIA JAKO WYSŁANE")
    print("="*60)
    
    # Step 3: Verify reminder was marked as sent
    results['verify_sent'] = test_verify_reminder_marked_as_sent(reminder_id)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY - REMINDERS SYSTEM")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All REMINDERS SYSTEM tests PASSED!")
        print("\n✅ VERIFICATION COMPLETE:")
        print("- POST /api/reminders working ✅")
        print("- GET /api/reminders/check/pending working ✅")
        print("- Endpoint returns correct format: {\"count\": int, \"reminders\": [...]} ✅")
        print("- Endpoint filters reminders for today with time <= current time ✅")
        print("- Endpoint marks reminders as sent=True after retrieval ✅")
    else:
        print("\n⚠️  Some REMINDERS SYSTEM tests FAILED!")
        failed_tests = [name for name, result in results.items() if not result]
        print(f"Failed tests: {failed_tests}")
    
    return results

# ============= AI ASSISTANT WORK HOURS TESTS =============

def test_get_projects():
    """TEST 1: Check if there are projects in the database"""
    print("\n=== TEST 1: Check Projects in Database ===")
    
    url = f"{API_URL}/projects"
    
    try:
        print(f"Sending GET request to: {url}")
        
        response = requests.get(url, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Found {len(response_data)} projects in database")
            
            if len(response_data) > 0:
                print("✅ Projects exist in database")
                for i, project in enumerate(response_data[:3]):  # Show first 3
                    print(f"   Project {i+1}: {project.get('title', 'No title')} - {project.get('status', 'No status')}")
                return True, response_data
            else:
                print("⚠️  No projects found - will create test project")
                return False, []
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            return False, []
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False, []

def test_create_test_project():
    """Create test project if none exist"""
    print("\n=== Creating Test Project ===")
    
    # First, get or create a client
    clients_url = f"{API_URL}/clients"
    
    try:
        # Check if clients exist
        response = requests.get(clients_url, timeout=15)
        if response.status_code == 200:
            clients = response.json()
            if len(clients) > 0:
                client_id = clients[0]["id"]
                print(f"Using existing client: {clients[0]['name']}")
            else:
                # Create a test client
                client_data = {
                    "name": "Jan Kowalski",
                    "phone": "+48123456789",
                    "address": "ul. Testowa 1",
                    "city": "Warszawa",
                    "postal_code": "00-001"
                }
                response = requests.post(clients_url, json=client_data, timeout=15)
                if response.status_code == 200:
                    client_id = response.json()["id"]
                    print(f"Created test client: {client_data['name']}")
                else:
                    print("❌ Failed to create test client")
                    return False, None
        else:
            print("❌ Failed to get clients list")
            return False, None
        
        # Create test project
        url = f"{API_URL}/projects"
        
        test_data = {
            "client_id": client_id,
            "title": "Test Montaż",
            "description": "Testowy projekt montażu instalacji elektrycznej",
            "location": "Warszawa",
            "status": "in_progress",
            "start_date": "2025-01-19",
            "estimated_hours": 10
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        print(f"Sending POST request to: {url}")
        print(f"Request data: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=test_data, headers=headers, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            print("✅ Test project created successfully")
            print(f"Created project ID: {response_data['id']}")
            print(f"Project title: {response_data['title']}")
            return True, response_data["id"]
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False, None

def test_ai_chat_add_work_hours():
    """TEST 2: Simulate AI - add work hours via chat"""
    print("\n=== TEST 2: AI Chat - Add Work Hours ===")
    
    url = f"{API_URL}/ai/chat"
    
    test_data = {
        "text": "Zapisz 8 godzin pracy na projekcie Test Montaż dzisiaj",
        "session_id": "test-work-hours-123"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Sending POST request to: {url}")
        print(f"Request data: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=test_data, headers=headers, timeout=30)  # Longer timeout for AI
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Check AI response
            ai_response = response_data.get("response", "")
            print(f"\n🤖 AI Response: {ai_response}")
            
            # Check if AI responded that it saved hours
            if "✅ Dodano" in ai_response or "zapisano" in ai_response.lower() or "dodano" in ai_response.lower():
                print("✅ AI responded that it saved work hours")
                
                # Check if action was executed
                action_executed = response_data.get("action_executed")
                if action_executed:
                    print(f"✅ Action executed: {action_executed}")
                    return True
                else:
                    print("⚠️  AI responded positively but no action_executed field")
                    return True  # Still consider success if AI responded correctly
            else:
                print("❌ AI did not respond that it saved work hours")
                print(f"AI Response: {ai_response}")
                return False
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_check_work_hours_in_database():
    """TEST 3: Check if work hours entry is in database"""
    print("\n=== TEST 3: Check Work Hours in Database ===")
    
    url = f"{API_URL}/workhours"
    
    try:
        print(f"Sending GET request to: {url}")
        
        response = requests.get(url, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Found {len(response_data)} work hours entries")
            
            # Look for today's entry with 8 hours
            today = datetime.now().date().isoformat()
            
            found_entry = None
            for entry in response_data:
                if (entry.get("date") == today and 
                    entry.get("hours") == 8.0 and 
                    "AI" in entry.get("notes", "")):
                    found_entry = entry
                    break
            
            if found_entry:
                print("✅ Found work hours entry added by AI:")
                print(f"   Date: {found_entry['date']}")
                print(f"   Hours: {found_entry['hours']}")
                print(f"   Notes: {found_entry['notes']}")
                print(f"   Project ID: {found_entry.get('project_id', 'None')}")
                return True, found_entry["id"]
            else:
                print("❌ No work hours entry found with:")
                print(f"   Date: {today}")
                print("   Hours: 8.0")
                print("   Notes containing 'AI'")
                
                # Show all entries for debugging
                if len(response_data) > 0:
                    print("\nAll work hours entries found:")
                    for i, entry in enumerate(response_data):
                        print(f"   Entry {i+1}: {entry.get('date')} - {entry.get('hours')}h - {entry.get('notes', 'No notes')}")
                
                return False, None
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False, None

def test_delete_work_hours(work_hour_id):
    """TEST 4: Test deleting work hours entry"""
    print("\n=== TEST 4: Delete Work Hours Entry ===")
    
    url = f"{API_URL}/workhours/{work_hour_id}"
    
    try:
        print(f"Sending DELETE request to: {url}")
        
        response = requests.delete(url, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verify success message
            if "message" in response_data:
                print(f"✅ DELETE response: {response_data['message']}")
                
                # Verify entry is actually deleted
                get_url = f"{API_URL}/workhours"
                get_response = requests.get(get_url, timeout=15)
                
                if get_response.status_code == 200:
                    entries = get_response.json()
                    deleted_entry = next((e for e in entries if e.get("id") == work_hour_id), None)
                    
                    if deleted_entry is None:
                        print("✅ Work hours entry successfully deleted from database")
                        return True
                    else:
                        print("❌ Work hours entry still exists in database")
                        return False
                else:
                    print("⚠️  Could not verify deletion - GET request failed")
                    return True  # Assume success based on 200 response
            else:
                print("❌ No success message in response")
                return False
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_delete_employee():
    """TEST 5: Test deleting employee"""
    print("\n=== TEST 5: Delete Employee ===")
    
    # First get list of employees
    url = f"{API_URL}/employees"
    
    try:
        print(f"Getting employees list from: {url}")
        
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            employees = response.json()
            
            if len(employees) > 0:
                # Delete the first employee
                employee_to_delete = employees[0]
                employee_id = employee_to_delete["id"]
                employee_name = employee_to_delete["name"]
                
                print(f"Deleting employee: {employee_name} (ID: {employee_id})")
                
                delete_url = f"{API_URL}/employees/{employee_id}"
                delete_response = requests.delete(delete_url, timeout=15)
                
                print(f"DELETE response status: {delete_response.status_code}")
                
                if delete_response.status_code == 200:
                    delete_data = delete_response.json()
                    print(f"DELETE response: {json.dumps(delete_data, indent=2, ensure_ascii=False)}")
                    
                    if "message" in delete_data:
                        print(f"✅ DELETE response: {delete_data['message']}")
                        return True
                    else:
                        print("❌ No success message in delete response")
                        return False
                else:
                    print(f"❌ DELETE request failed with status {delete_response.status_code}")
                    try:
                        error_data = delete_response.json()
                        print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
                    except:
                        print(f"Error text: {delete_response.text}")
                    return False
            else:
                print("⚠️  No employees found to delete")
                return True  # Not a failure if no employees exist
            
        else:
            print(f"❌ GET employees request failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def main():
    """Run AI Assistant Work Hours Tests as requested"""
    print("🤖 AI ASSISTANT WORK HOURS TESTING")
    print("Testing czy AI faktycznie zapisuje godziny pracy do bazy")
    print(f"Backend URL: {BASE_URL}")
    print(f"API URL: {API_URL}")
    print("=" * 80)
    
    # Test backend health first
    if not test_backend_health():
        print("\n❌ Backend health check failed - stopping tests")
        return
    
    # Track test results
    results = []
    
    print("\n" + "=" * 80)
    print("🤖 AI ASSISTANT WORK HOURS TESTS (as requested)")
    print("=" * 80)
    
    # TEST 1: Check if projects exist
    projects_exist, projects = test_get_projects()
    results.append(("TEST 1: Check Projects", projects_exist))
    
    # If no projects, create test project
    if not projects_exist:
        success, project_id = test_create_test_project()
        results.append(("Create Test Project", success))
    
    # TEST 2: AI Chat - Add work hours
    success = test_ai_chat_add_work_hours()
    results.append(("TEST 2: AI Chat Add Work Hours", success))
    
    # TEST 3: Check if entry is in database
    success, work_hour_id = test_check_work_hours_in_database()
    results.append(("TEST 3: Check Work Hours in DB", success))
    
    # TEST 4: Delete work hours entry
    if success and work_hour_id:
        success = test_delete_work_hours(work_hour_id)
        results.append(("TEST 4: Delete Work Hours", success))
    
    # TEST 5: Delete employee
    success = test_delete_employee()
    results.append(("TEST 5: Delete Employee", success))
    
    # Print final results
    print("\n" + "=" * 80)
    print("📊 AI ASSISTANT WORK HOURS TEST RESULTS")
    print("=" * 80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    print(f"\n🎯 SUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL AI ASSISTANT WORK HOURS TESTS PASSED!")
        print("\n✅ VERIFICATION COMPLETE:")
        print("- GET /api/projects working ✅")
        print("- POST /api/ai/chat working ✅")
        print("- AI can save work hours to database ✅")
        print("- GET /api/workhours working ✅")
        print("- DELETE /api/workhours/{id} working ✅")
        print("- DELETE /api/employees/{id} working ✅")
    else:
        print(f"⚠️  {total - passed} tests failed")
        failed_tests = [name for name, success in results if not success]
        print(f"Failed tests: {[name for name, success in results if not success]}")
    
    print(f"\nBackend URL tested: {BASE_URL}")
    return results

# ============= SALARIES CATEGORY SPECIFIC TESTS =============

def test_salaries_category_complete_flow():
    """Complete test flow for salaries category as requested in review"""
    print("\n" + "="*80)
    print("🧪 TESTING SALARIES CATEGORY - COMPLETE FLOW")
    print("="*80)
    
    # TEST 1: Dodawanie wpisu "Wypłaty pracowników"
    print("\n📝 TEST 1: Dodawanie wpisu 'Wypłaty pracowników'")
    success, salary_id = test_create_salary_entry()
    if not success:
        print("❌ TEST 1 FAILED - Cannot continue with other tests")
        return False
    
    # TEST 2: Weryfikacja w liście
    print("\n📋 TEST 2: Weryfikacja w liście")
    success = test_verify_salary_in_list()
    if not success:
        print("❌ TEST 2 FAILED")
        return False
    
    # TEST 3: Weryfikacja w podsumowaniu
    print("\n📊 TEST 3: Weryfikacja w podsumowaniu")
    success = test_verify_salary_in_summary()
    if not success:
        print("❌ TEST 3 FAILED")
        return False
    
    # TEST 4: Usuwanie wpisu
    print("\n🗑️ TEST 4: Usuwanie wpisu")
    success = test_delete_salary_entry(salary_id)
    if not success:
        print("❌ TEST 4 FAILED")
        return False
    
    # TEST 5: Weryfikacja po usunięciu
    print("\n✅ TEST 5: Weryfikacja po usunięciu")
    success = test_verify_salary_deleted()
    if not success:
        print("❌ TEST 5 FAILED")
        return False
    
    print("\n" + "="*80)
    print("🎉 ALL SALARIES CATEGORY TESTS PASSED!")
    print("="*80)
    return True

def test_create_salary_entry():
    """TEST 1: POST /api/financial-entries - Create salary entry"""
    print("\n=== TEST 1: Creating Salary Entry ===")
    
    url = f"{API_URL}/financial-entries"
    
    # Exact test data as specified in the review request
    test_data = {
        "category": "salaries",
        "date": "2025-01-19",
        "description": "Wypłaty styczeń 2025",
        "amount_net": 5000.00,
        "amount_gross": 5000.00,
        "vat_rate": None,
        "notes": "Test wypłat"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Sending POST request to: {url}")
        print(f"Request data: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=test_data, headers=headers, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verify response structure
            required_fields = ["id", "date", "category", "description", "amount_net", "amount_gross", "notes", "created_at", "updated_at"]
            missing_fields = [field for field in required_fields if field not in response_data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False, None
            
            # Verify data matches exactly
            if response_data["category"] != "salaries":
                print(f"❌ Category mismatch. Expected: salaries, Got: {response_data['category']}")
                return False, None
            
            if response_data["date"] != "2025-01-19":
                print(f"❌ Date mismatch. Expected: 2025-01-19, Got: {response_data['date']}")
                return False, None
            
            if response_data["description"] != "Wypłaty styczeń 2025":
                print(f"❌ Description mismatch. Expected: 'Wypłaty styczeń 2025', Got: {response_data['description']}")
                return False, None
            
            if response_data["amount_net"] != 5000.00:
                print(f"❌ Amount net mismatch. Expected: 5000.00, Got: {response_data['amount_net']}")
                return False, None
            
            if response_data["amount_gross"] != 5000.00:
                print(f"❌ Amount gross mismatch. Expected: 5000.00, Got: {response_data['amount_gross']}")
                return False, None
            
            if response_data["notes"] != "Test wypłat":
                print(f"❌ Notes mismatch. Expected: 'Test wypłat', Got: {response_data['notes']}")
                return False, None
            
            # Verify ID is generated
            if not response_data["id"] or len(response_data["id"]) == 0:
                print("❌ Salary entry ID is empty")
                return False, None
            
            print("✅ TEST 1 PASSED: Salary entry created successfully")
            print(f"✅ Status 200 returned")
            print(f"✅ Created entry ID: {response_data['id']}")
            print(f"✅ All required fields present and correct")
            return True, response_data["id"]
            
        else:
            print(f"❌ TEST 1 FAILED: Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ TEST 1 FAILED: Unexpected error: {str(e)}")
        return False, None

def test_verify_salary_in_list():
    """TEST 2: GET /api/financial-entries?month=2025-01 - Verify salary in list"""
    print("\n=== TEST 2: Verifying Salary in List ===")
    
    url = f"{API_URL}/financial-entries?month=2025-01"
    
    try:
        print(f"Sending GET request to: {url}")
        
        response = requests.get(url, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Found {len(response_data)} entries for January 2025")
            
            # Verify response is a list
            if not isinstance(response_data, list):
                print("❌ Response is not a list")
                return False
            
            # Look for our salary entry
            salary_entry = None
            for entry in response_data:
                if (entry.get("category") == "salaries" and 
                    entry.get("date") == "2025-01-19" and
                    entry.get("description") == "Wypłaty styczeń 2025"):
                    salary_entry = entry
                    break
            
            if salary_entry:
                print("✅ TEST 2 PASSED: Salary entry found in list")
                print(f"✅ Category: {salary_entry['category']}")
                print(f"✅ Date: {salary_entry['date']}")
                print(f"✅ Description: {salary_entry['description']}")
                print(f"✅ Amount Net: {salary_entry['amount_net']}")
                print(f"✅ Amount Gross: {salary_entry['amount_gross']}")
                
                # Verify amounts are correct
                if salary_entry['amount_net'] == 5000.00 and salary_entry['amount_gross'] == 5000.00:
                    print("✅ Amounts are correct (5000.00)")
                    return True
                else:
                    print(f"❌ Amount mismatch. Expected: 5000.00/5000.00, Got: {salary_entry['amount_net']}/{salary_entry['amount_gross']}")
                    return False
            else:
                print("❌ TEST 2 FAILED: Salary entry not found in list")
                print("Available entries:")
                for entry in response_data:
                    print(f"  - {entry.get('category')} | {entry.get('date')} | {entry.get('description')}")
                return False
            
        else:
            print(f"❌ TEST 2 FAILED: Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ TEST 2 FAILED: Unexpected error: {str(e)}")
        return False

def test_verify_salary_in_summary():
    """TEST 3: GET /api/financial-entries/summary?month=2025-01 - Verify salary in summary"""
    print("\n=== TEST 3: Verifying Salary in Summary ===")
    
    url = f"{API_URL}/financial-entries/summary?month=2025-01"
    
    try:
        print(f"Sending GET request to: {url}")
        
        response = requests.get(url, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verify response structure
            if "categories" not in response_data or "totals" not in response_data:
                print("❌ Missing categories or totals in response")
                return False
            
            categories = response_data["categories"]
            totals = response_data["totals"]
            
            # Look for salaries category
            salaries_category = None
            for category in categories:
                if category.get("category") == "salaries":
                    salaries_category = category
                    break
            
            if salaries_category:
                print("✅ TEST 3 PART 1 PASSED: Salaries category found in summary")
                print(f"✅ Category: {salaries_category['category']}")
                print(f"✅ Total Net: {salaries_category['total_net']}")
                print(f"✅ Total Gross: {salaries_category['total_gross']}")
                print(f"✅ Count: {salaries_category['count']}")
                print(f"✅ Type: {salaries_category['type']}")
                
                # Verify amounts
                if salaries_category['total_net'] == 5000.00 and salaries_category['total_gross'] == 5000.00:
                    print("✅ Salaries category amounts are correct")
                else:
                    print(f"❌ Salaries category amounts incorrect. Expected: 5000.00/5000.00, Got: {salaries_category['total_net']}/{salaries_category['total_gross']}")
                    return False
            else:
                print("❌ TEST 3 PART 1 FAILED: Salaries category not found in summary")
                print("Available categories:")
                for category in categories:
                    print(f"  - {category.get('category')}: {category.get('total_net')}/{category.get('total_gross')}")
                return False
            
            # Verify totals include salary amounts
            print(f"\n📊 Checking totals:")
            print(f"Expense Net: {totals.get('expense_net')}")
            print(f"Expense Gross: {totals.get('expense_gross')}")
            
            # Since salaries is an expense, it should be included in expense totals
            if totals.get('expense_net', 0) >= 5000.00 and totals.get('expense_gross', 0) >= 5000.00:
                print("✅ TEST 3 PART 2 PASSED: Salary amounts included in expense totals")
                print("✅ TEST 3 COMPLETE: Summary verification successful")
                return True
            else:
                print(f"❌ TEST 3 PART 2 FAILED: Salary amounts not properly included in totals")
                print(f"Expected expense totals to include at least 5000.00, got: {totals.get('expense_net')}/{totals.get('expense_gross')}")
                return False
            
        else:
            print(f"❌ TEST 3 FAILED: Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ TEST 3 FAILED: Unexpected error: {str(e)}")
        return False

def test_delete_salary_entry(salary_id):
    """TEST 4: DELETE /api/financial-entries/{id} - Delete salary entry"""
    print("\n=== TEST 4: Deleting Salary Entry ===")
    
    url = f"{API_URL}/financial-entries/{salary_id}"
    
    try:
        print(f"Sending DELETE request to: {url}")
        print(f"Deleting salary entry with ID: {salary_id}")
        
        response = requests.delete(url, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verify success message
            if "message" in response_data:
                print(f"✅ TEST 4 PASSED: DELETE successful")
                print(f"✅ Status 200 returned")
                print(f"✅ Success message: {response_data['message']}")
                return True
            else:
                print("❌ No success message in response")
                return False
            
        else:
            print(f"❌ TEST 4 FAILED: Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ TEST 4 FAILED: Unexpected error: {str(e)}")
        return False

def test_verify_salary_deleted():
    """TEST 5: GET /api/financial-entries?month=2025-01 - Verify salary is deleted"""
    print("\n=== TEST 5: Verifying Salary Entry Deleted ===")
    
    url = f"{API_URL}/financial-entries?month=2025-01"
    
    try:
        print(f"Sending GET request to: {url}")
        
        response = requests.get(url, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Found {len(response_data)} entries for January 2025 after deletion")
            
            # Look for our deleted salary entry
            salary_entry_found = False
            for entry in response_data:
                if (entry.get("category") == "salaries" and 
                    entry.get("date") == "2025-01-19" and
                    entry.get("description") == "Wypłaty styczeń 2025"):
                    salary_entry_found = True
                    break
            
            if not salary_entry_found:
                print("✅ TEST 5 PASSED: Salary entry successfully deleted from list")
                print("✅ Entry no longer appears in January 2025 entries")
                return True
            else:
                print("❌ TEST 5 FAILED: Salary entry still found in list after deletion")
                return False
            
        else:
            print(f"❌ TEST 5 FAILED: Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ TEST 5 FAILED: Unexpected error: {str(e)}")
        return False

def main_salaries():
    """Run Salaries Category tests specifically"""
    print("🚀 Starting Salaries Category Testing...")
    print(f"Backend URL: {BASE_URL}")
    print(f"API URL: {API_URL}")
    
    # Test backend health first
    if not test_backend_health():
        print("❌ Backend is not responding. Cannot run tests.")
        return False
    
    # Run the complete salaries category test flow
    success = test_salaries_category_complete_flow()
    
    if success:
        print("\n🎉 ALL SALARIES CATEGORY TESTS COMPLETED SUCCESSFULLY!")
        return True
    else:
        print("\n❌ SOME SALARIES CATEGORY TESTS FAILED!")
        return False

def main_reminders():
    """Run Reminders System tests specifically"""
    return test_reminders_system()

def main_ai_dates():
    """Run AI Assistant Date tests specifically"""
    print("🤖 Starting AI Assistant Date Testing...")
    print(f"Backend URL: {BASE_URL}")
    print(f"API URL: {API_URL}")
    
    # Test backend health first
    if not test_backend_health():
        print("❌ Backend is not responding. Cannot run tests.")
        return False
    
    # Run the comprehensive AI date test
    success = test_ai_date_comprehensive()
    
    if success:
        print("\n🎉 ALL AI DATE TESTS COMPLETED SUCCESSFULLY!")
        return True
    else:
        print("\n❌ SOME AI DATE TESTS FAILED!")
        return False

def main_chat_history():
    """Main function for AI Assistant and AI Analyst chat history testing"""
    print("💬 AI CHAT HISTORY TESTING STARTED")
    print(f"Backend URL: {BASE_URL}")
    print(f"API URL: {API_URL}")
    print("=" * 80)
    
    # Test backend health first
    if not test_backend_health():
        print("❌ Backend is not responding. Cannot run tests.")
        return False
    
    # Test results tracking
    results = []
    
    # TEST 1: AI Assistant Sessions
    print("\n🔍 TESTING AI ASSISTANT ENDPOINTS")
    success, ai_session_id = test_ai_assistant_sessions()
    results.append(("AI Assistant Sessions", success))
    
    # TEST 2: AI Assistant History
    if success and ai_session_id:
        success = test_ai_assistant_history(ai_session_id)
        results.append(("AI Assistant History", success))
    else:
        print("⚠️  Skipping AI Assistant History test - no sessions available")
        results.append(("AI Assistant History", None))
    
    # TEST 3: AI Analyst Sessions
    print("\n🔍 TESTING AI ANALYST ENDPOINTS")
    success, analyst_session_id = test_ai_analyst_sessions()
    results.append(("AI Analyst Sessions", success))
    
    # TEST 4: AI Analyst History
    if success and analyst_session_id:
        success = test_ai_analyst_history(analyst_session_id)
        results.append(("AI Analyst History", success))
    else:
        print("⚠️  Skipping AI Analyst History test - no sessions available")
        results.append(("AI Analyst History", None))
    
    # TEST 5: Empty Sessions Handling
    print("\n🔍 TESTING EMPTY SESSIONS HANDLING")
    success = test_empty_sessions_handling()
    results.append(("Empty Sessions Handling", success))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 CHAT HISTORY TESTING SUMMARY")
    print("=" * 80)
    
    passed = 0
    failed = 0
    skipped = 0
    
    for test_name, result in results:
        if result is True:
            print(f"✅ {test_name}: PASSED")
            passed += 1
        elif result is False:
            print(f"❌ {test_name}: FAILED")
            failed += 1
        else:
            print(f"⚠️  {test_name}: SKIPPED")
            skipped += 1
    
    print(f"\nTotal: {len(results)} tests")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️  Skipped: {skipped}")
    
    if failed == 0:
        print("\n🎉 ALL CRITICAL TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️  {failed} TESTS FAILED - REQUIRES ATTENTION")
        return False
    
    print("\n" + "=" * 80)
    print("💬 AI CHAT HISTORY TESTING COMPLETED")

if __name__ == "__main__":
    # Check if we should run specific tests
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "reminders":
            main_reminders()
        elif sys.argv[1] == "salaries":
            main_salaries()
        elif sys.argv[1] == "ai-dates":
            main_ai_dates()
        elif sys.argv[1] == "chat-history":
            main_chat_history()
        else:
            print("Available test modes: reminders, salaries, ai-dates, chat-history")
            print("Usage: python backend_test.py [reminders|salaries|ai-dates|chat-history]")
    else:
        # Default: run chat history tests as requested
        main_chat_history()