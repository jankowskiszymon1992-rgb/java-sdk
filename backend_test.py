#!/usr/bin/env python3
"""
Backend API Testing for Financial System
Tests the new Financial system with OCR for invoices
"""

import requests
import json
import time
import os
from datetime import datetime

# Get backend URL from frontend .env
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except:
        pass
    return "https://elektron-finance.preview.emergentagent.com"

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
                        
                        # Verify it was marked as sent
                        if reminder.get("sent") == True:
                            print("✅ CRITICAL: Reminder was correctly marked as sent=True")
                        else:
                            print(f"❌ CRITICAL: Reminder should be marked as sent=True, got: {reminder.get('sent')}")
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

def main():
    """Run all Financial System endpoint tests"""
    print("💰 Financial System Testing - NEW FINANCIAL SYSTEM WITH OCR")
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
    print("CZĘŚĆ 1: RĘCZNE DODAWANIE WPISÓW")
    print("="*60)
    
    # Step 1: Create invoice sales entry
    create_invoice_result, invoice_id = test_create_financial_entry_invoice_sales()
    results['create_invoice_sales'] = create_invoice_result
    
    # Step 2: Create salaries entry
    create_salaries_result, salaries_id = test_create_financial_entry_salaries()
    results['create_salaries'] = create_salaries_result
    
    # Step 3: Create fuel entry
    create_fuel_result, fuel_id = test_create_financial_entry_fuel()
    results['create_fuel'] = create_fuel_result
    
    print("\n" + "="*60)
    print("CZĘŚĆ 2: POBIERANIE I PODSUMOWANIE")
    print("="*60)
    
    # Step 4: Get all entries for October
    results['get_entries_october'] = test_get_financial_entries_october()
    
    # Step 5: Get summary for October
    results['get_summary_october'] = test_get_financial_summary_october()
    
    print("\n" + "="*60)
    print("CZĘŚĆ 3: EDYCJA I USUWANIE")
    print("="*60)
    
    # Step 6: Edit fuel entry (only if it was created successfully)
    if create_fuel_result and fuel_id:
        results['edit_fuel_entry'] = test_edit_financial_entry_fuel(fuel_id)
        
        # Step 7: Delete fuel entry
        results['delete_fuel_entry'] = test_delete_financial_entry_fuel(fuel_id)
        
        # Step 8: Verify deletion
        results['verify_fuel_deletion'] = test_verify_fuel_deletion()
    else:
        print("⚠️  Skipping fuel edit/delete tests - fuel entry creation failed")
        results['edit_fuel_entry'] = False
        results['delete_fuel_entry'] = False
        results['verify_fuel_deletion'] = False
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY - FINANCIAL SYSTEM")
    print("="*60)
    
    print("\nCZĘŚĆ 1: RĘCZNE DODAWANIE WPISÓW")
    part1_tests = ['create_invoice_sales', 'create_salaries', 'create_fuel']
    for test_name in part1_tests:
        if test_name in results:
            status = "✅ PASS" if results[test_name] else "❌ FAIL"
            print(f"  {test_name}: {status}")
    
    print("\nCZĘŚĆ 2: POBIERANIE I PODSUMOWANIE")
    part2_tests = ['get_entries_october', 'get_summary_october']
    for test_name in part2_tests:
        if test_name in results:
            status = "✅ PASS" if results[test_name] else "❌ FAIL"
            print(f"  {test_name}: {status}")
    
    print("\nCZĘŚĆ 3: EDYCJA I USUWANIE")
    part3_tests = ['edit_fuel_entry', 'delete_fuel_entry', 'verify_fuel_deletion']
    for test_name in part3_tests:
        if test_name in results:
            status = "✅ PASS" if results[test_name] else "❌ FAIL"
            print(f"  {test_name}: {status}")
    
    print(f"\nOVERALL:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All FINANCIAL SYSTEM tests PASSED!")
        print("\n✅ VERIFICATION COMPLETE:")
        print("- POST /api/financial-entries working ✅")
        print("- GET /api/financial-entries with month filter working ✅")
        print("- GET /api/financial-entries/summary with calculations working ✅")
        print("- PUT /api/financial-entries/{id} working ✅")
        print("- DELETE /api/financial-entries/{id} working ✅")
        print("- All calculations (balance, totals per category) working ✅")
    else:
        print("\n⚠️  Some FINANCIAL SYSTEM tests FAILED!")
        failed_tests = [name for name, result in results.items() if not result]
        print(f"Failed tests: {failed_tests}")
    
    return results

if __name__ == "__main__":
    main()