#!/usr/bin/env python3
"""
Backend API Testing for Employee Endpoints
Tests the new Employee management endpoints
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
    return "https://elektron-assistant.preview.emergentagent.com"

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

def main():
    """Run all Employee endpoint tests including new functionality"""
    print("👷 Employee Endpoint Testing - NEW FUNCTIONALITY")
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
    print("CZĘŚĆ 1: TEST EDYCJI WPISU GODZIN")
    print("="*60)
    
    # Step 1: Create Marek Testowy employee
    create_marek_result, marek_id = test_create_marek_testowy()
    results['create_marek_testowy'] = create_marek_result
    
    if not create_marek_result:
        print("\n❌ Cannot proceed without creating Marek Testowy.")
        return results
    
    # Step 2: Create work entry (5.0 hours = 200.0 zł)
    create_entry_result, entry_id = test_create_marek_work_entry(marek_id)
    results['create_marek_work_entry'] = create_entry_result
    
    if not create_entry_result:
        print("\n❌ Cannot proceed without creating work entry.")
        return results
    
    # Step 3: Edit work entry (7.5 hours = 300.0 zł)
    results['edit_work_entry'] = test_edit_work_entry(entry_id, marek_id)
    
    # Step 4: Verify edited entry
    results['verify_edited_entry'] = test_verify_edited_entry()
    
    print("\n" + "="*60)
    print("CZĘŚĆ 2: TEST CASCADE DELETE")
    print("="*60)
    
    # Step 5: Create second work entry
    create_second_result, second_entry_id = test_create_second_work_entry(marek_id)
    results['create_second_work_entry'] = create_second_result
    
    # Step 6: Count Marek's entries (should be 2)
    results['count_marek_entries'] = test_count_marek_entries()
    
    # Step 7: CASCADE DELETE employee
    results['cascade_delete_employee'] = test_cascade_delete_employee(marek_id)
    
    # Step 8: Verify CASCADE DELETE worked
    results['verify_cascade_delete'] = test_verify_cascade_delete()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY - NEW FUNCTIONALITY")
    print("="*60)
    
    print("\nCZĘŚĆ 1: EDYCJA WPISU GODZIN")
    part1_tests = ['create_marek_testowy', 'create_marek_work_entry', 'edit_work_entry', 'verify_edited_entry']
    for test_name in part1_tests:
        if test_name in results:
            status = "✅ PASS" if results[test_name] else "❌ FAIL"
            print(f"  {test_name}: {status}")
    
    print("\nCZĘŚĆ 2: CASCADE DELETE")
    part2_tests = ['create_second_work_entry', 'count_marek_entries', 'cascade_delete_employee', 'verify_cascade_delete']
    for test_name in part2_tests:
        if test_name in results:
            status = "✅ PASS" if results[test_name] else "❌ FAIL"
            print(f"  {test_name}: {status}")
    
    print(f"\nOVERALL:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All NEW FUNCTIONALITY tests PASSED!")
        print("\n✅ VERIFICATION COMPLETE:")
        print("- PUT /api/employee-work-entries/{entry_id} working ✅")
        print("- Automatic total_earnings recalculation working ✅")
        print("- DELETE /api/employees/{employee_id} CASCADE DELETE working ✅")
        print("- Employee and all work entries deleted correctly ✅")
    else:
        print("\n⚠️  Some NEW FUNCTIONALITY tests FAILED!")
        failed_tests = [name for name, result in results.items() if not result]
        print(f"Failed tests: {failed_tests}")
    
    return results

if __name__ == "__main__":
    main()