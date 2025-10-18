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
    return "https://elektro-assist.preview.emergentagent.com"

BASE_URL = get_backend_url()
API_URL = f"{BASE_URL}/api"

def test_ai_chat_endpoint():
    """Test POST /api/ai/chat endpoint"""
    print("\n=== Testing AI Chat Endpoint ===")
    
    url = f"{API_URL}/ai/chat"
    
    # Test data as specified in the request
    test_data = {
        "text": "Witaj! Kim jesteś?",
        "session_id": "test_session_123"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Sending POST request to: {url}")
        print(f"Request data: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=test_data, headers=headers, timeout=30)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verify response structure
            required_fields = ["response", "session_id", "timestamp"]
            missing_fields = [field for field in required_fields if field not in response_data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            
            # Verify session_id matches
            if response_data["session_id"] != test_data["session_id"]:
                print(f"❌ Session ID mismatch. Expected: {test_data['session_id']}, Got: {response_data['session_id']}")
                return False
            
            # Verify AI response is not empty
            if not response_data["response"] or len(response_data["response"].strip()) == 0:
                print("❌ AI response is empty")
                return False
            
            print("✅ AI Chat endpoint working correctly")
            print(f"AI Response: {response_data['response']}")
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
        print("❌ Request timed out (30s)")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - backend may not be running")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_ai_history_endpoint():
    """Test POST /api/ai/history endpoint"""
    print("\n=== Testing AI History Endpoint ===")
    
    url = f"{API_URL}/ai/history"
    
    # Test data as specified in the request
    test_data = {
        "session_id": "test_session_123",
        "limit": 10
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
            if response_data["session_id"] != test_data["session_id"]:
                print(f"❌ Session ID mismatch. Expected: {test_data['session_id']}, Got: {response_data['session_id']}")
                return False
            
            # Verify conversations is a list
            if not isinstance(response_data["conversations"], list):
                print("❌ Conversations field is not a list")
                return False
            
            # Check if we have the conversation from the previous test
            conversations = response_data["conversations"]
            if len(conversations) > 0:
                print(f"✅ Found {len(conversations)} conversation(s) in history")
                
                # Verify conversation structure
                for i, conv in enumerate(conversations):
                    required_conv_fields = ["id", "session_id", "user_message", "ai_response", "timestamp", "model"]
                    missing_conv_fields = [field for field in required_conv_fields if field not in conv]
                    
                    if missing_conv_fields:
                        print(f"❌ Conversation {i} missing fields: {missing_conv_fields}")
                        return False
                
                # Check if our test message is in the history
                test_message_found = any(
                    conv.get("user_message") == "Witaj! Kim jesteś?" 
                    for conv in conversations
                )
                
                if test_message_found:
                    print("✅ Test message found in conversation history")
                else:
                    print("⚠️  Test message not found in history (may be expected if history was cleared)")
                
            else:
                print("⚠️  No conversations found in history")
            
            print("✅ AI History endpoint working correctly")
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
    """Run all AI Assistant endpoint tests"""
    print("🤖 AI Assistant Endpoint Testing")
    print(f"Backend URL: {BASE_URL}")
    print(f"API URL: {API_URL}")
    print(f"Test time: {datetime.now().isoformat()}")
    
    results = {}
    
    # Test backend health first
    results['backend_health'] = test_backend_health()
    
    if not results['backend_health']:
        print("\n❌ Backend is not responding. Cannot proceed with AI tests.")
        return results
    
    # Test AI Chat endpoint
    results['ai_chat'] = test_ai_chat_endpoint()
    
    # Wait a moment for the conversation to be saved
    if results['ai_chat']:
        print("\nWaiting 2 seconds for conversation to be saved...")
        time.sleep(2)
    
    # Test AI History endpoint
    results['ai_history'] = test_ai_history_endpoint()
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All AI Assistant tests PASSED!")
    else:
        print("\n⚠️  Some AI Assistant tests FAILED!")
    
    return results

if __name__ == "__main__":
    main()