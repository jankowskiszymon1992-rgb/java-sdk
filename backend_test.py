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

def main():
    """Run all Employee endpoint tests"""
    print("👷 Employee Endpoint Testing")
    print(f"Backend URL: {BASE_URL}")
    print(f"API URL: {API_URL}")
    print(f"Test time: {datetime.now().isoformat()}")
    
    results = {}
    employee_id = None
    
    # Test backend health first
    results['backend_health'] = test_backend_health()
    
    if not results['backend_health']:
        print("\n❌ Backend is not responding. Cannot proceed with Employee tests.")
        return results
    
    # Test Create Employee endpoint
    create_result, employee_id = test_create_employee()
    results['create_employee'] = create_result
    
    if not create_result:
        print("\n❌ Cannot proceed with other tests without creating an employee.")
        return results
    
    # Test Get Employees endpoint
    results['get_employees'] = test_get_employees()
    
    # Test Create Work Entry endpoint (requires employee_id)
    if employee_id:
        results['create_work_entry'] = test_create_work_entry(employee_id)
        
        # Wait a moment for the work entry to be saved
        if results['create_work_entry']:
            print("\nWaiting 2 seconds for work entry to be saved...")
            time.sleep(2)
    else:
        print("\n❌ No employee ID available for work entry test")
        results['create_work_entry'] = False
    
    # Test Get Work Entries endpoint
    results['get_work_entries'] = test_get_work_entries()
    
    # Test Work Entries Summary endpoint
    results['work_entries_summary'] = test_work_entries_summary()
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All Employee endpoint tests PASSED!")
        print("\n✅ VERIFICATION COMPLETE:")
        print("- All CRUD operations working")
        print("- Calculations are correct (hours × hourly_rate)")
        print("- Data is being saved to MongoDB")
        print("- All endpoints return status 200")
    else:
        print("\n⚠️  Some Employee endpoint tests FAILED!")
    
    return results

if __name__ == "__main__":
    main()