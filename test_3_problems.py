#!/usr/bin/env python3
"""
Test 3 specific problems reported by user:
1. Error 'search_terms' in scraping Conrad/TME/RS
2. No access to GPT-5 chat history (AI Analyst)  
3. Check chat history in AI Assistant
"""

import requests
import json
import time
from datetime import datetime

# Backend URL
BASE_URL = "https://elektron-hub.preview.emergentagent.com"
API_URL = f"{BASE_URL}/api"

def test_problem_1_scraping_search_terms():
    """
    PROBLEM 1: Test scraping Conrad/TME/RS for 'search_terms' error
    POST /api/market-intelligence/scrape with {"suppliers": ["tme", "conrad"]}
    """
    print("\n" + "="*60)
    print("PROBLEM 1: Testing scraping Conrad/TME/RS for 'search_terms' error")
    print("="*60)
    
    url = f"{API_URL}/market-intelligence/scrape"
    
    test_data = {
        "suppliers": ["tme", "conrad"]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Sending POST request to: {url}")
        print(f"Request data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(url, json=test_data, headers=headers, timeout=30)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"✅ Response received: {json.dumps(response_data, indent=2)}")
            return True, "Scraping endpoint works - no search_terms error"
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                error_text = json.dumps(error_data, indent=2)
                print(f"Error details: {error_text}")
                
                # Check if error contains 'search_terms'
                if 'search_terms' in error_text.lower():
                    return False, f"CONFIRMED: 'search_terms' error found - {error_text}"
                else:
                    return False, f"Different error (not search_terms): {error_text}"
            except:
                error_text = response.text
                print(f"Error text: {error_text}")
                if 'search_terms' in error_text.lower():
                    return False, f"CONFIRMED: 'search_terms' error found - {error_text}"
                else:
                    return False, f"Different error (not search_terms): {error_text}"
            
    except requests.exceptions.Timeout:
        return False, "Request timed out (30s)"
    except requests.exceptions.ConnectionError:
        return False, "Connection error - backend may not be running"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def test_problem_2_ai_analyst_sessions():
    """
    PROBLEM 2.1: Test AI Analyst chat sessions
    GET /api/ai-analyst/chat/sessions?limit=50
    """
    print("\n" + "="*60)
    print("PROBLEM 2.1: Testing AI Analyst chat sessions")
    print("="*60)
    
    url = f"{API_URL}/ai-analyst/chat/sessions?limit=50"
    
    try:
        print(f"Sending GET request to: {url}")
        
        response = requests.get(url, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2)}")
            
            if isinstance(response_data, list):
                session_count = len(response_data)
                print(f"✅ Found {session_count} AI Analyst sessions")
                return True, f"Found {session_count} sessions", response_data
            else:
                print(f"✅ Response received: {response_data}")
                return True, "Sessions endpoint works", response_data
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error text: {response.text}")
            return False, f"Sessions endpoint failed with status {response.status_code}", None
            
    except Exception as e:
        return False, f"Error: {str(e)}", None

def test_problem_2_ai_analyst_history(session_id):
    """
    PROBLEM 2.2: Test AI Analyst chat history
    GET /api/ai-analyst/chat/history?session_id={session_id}&limit=50
    """
    print("\n" + "="*60)
    print("PROBLEM 2.2: Testing AI Analyst chat history")
    print("="*60)
    
    url = f"{API_URL}/ai-analyst/chat/history?session_id={session_id}&limit=50"
    
    try:
        print(f"Sending GET request to: {url}")
        
        response = requests.get(url, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2)}")
            
            if isinstance(response_data, list):
                history_count = len(response_data)
                print(f"✅ Found {history_count} messages in history")
                
                # Check for user_message and ai_response
                has_user_messages = any('user_message' in str(msg) for msg in response_data)
                has_ai_responses = any('ai_response' in str(msg) for msg in response_data)
                
                print(f"Has user_message: {has_user_messages}")
                print(f"Has ai_response: {has_ai_responses}")
                
                return True, f"Found {history_count} messages, user_msg: {has_user_messages}, ai_resp: {has_ai_responses}"
            else:
                print(f"✅ Response received: {response_data}")
                return True, "History endpoint works"
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error text: {response.text}")
            return False, f"History endpoint failed with status {response.status_code}"
            
    except Exception as e:
        return False, f"Error: {str(e)}"

def test_problem_2_create_ai_analyst_conversation():
    """
    PROBLEM 2.3: Create test AI Analyst conversation
    POST /api/ai-analyst/chat
    """
    print("\n" + "="*60)
    print("PROBLEM 2.3: Creating test AI Analyst conversation")
    print("="*60)
    
    url = f"{API_URL}/ai-analyst/chat"
    
    test_data = {
        "text": "Jakie są najnowsze ceny przewodów?",
        "session_id": "test-history-analyst"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Sending POST request to: {url}")
        print(f"Request data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(url, json=test_data, headers=headers, timeout=30)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"✅ Response received: {json.dumps(response_data, indent=2)}")
            return True, "AI Analyst chat works"
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error text: {response.text}")
            return False, f"AI Analyst chat failed with status {response.status_code}"
            
    except Exception as e:
        return False, f"Error: {str(e)}"

def test_problem_3_ai_assistant_sessions():
    """
    PROBLEM 3.1: Test AI Assistant sessions
    GET /api/ai/sessions?limit=50
    """
    print("\n" + "="*60)
    print("PROBLEM 3.1: Testing AI Assistant sessions")
    print("="*60)
    
    url = f"{API_URL}/ai/sessions?limit=50"
    
    try:
        print(f"Sending GET request to: {url}")
        
        response = requests.get(url, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2)}")
            
            if isinstance(response_data, list):
                session_count = len(response_data)
                print(f"✅ Found {session_count} AI Assistant sessions")
                return True, f"Found {session_count} sessions", response_data
            else:
                print(f"✅ Response received: {response_data}")
                return True, "Sessions endpoint works", response_data
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error text: {response.text}")
            return False, f"Sessions endpoint failed with status {response.status_code}", None
            
    except Exception as e:
        return False, f"Error: {str(e)}", None

def test_problem_3_ai_assistant_history(session_id):
    """
    PROBLEM 3.2: Test AI Assistant history
    POST /api/ai/history
    """
    print("\n" + "="*60)
    print("PROBLEM 3.2: Testing AI Assistant history")
    print("="*60)
    
    url = f"{API_URL}/ai/history"
    
    test_data = {
        "session_id": session_id
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Sending POST request to: {url}")
        print(f"Request data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(url, json=test_data, headers=headers, timeout=15)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2)}")
            
            # Check for expected structure
            if 'conversations' in response_data:
                conversations = response_data['conversations']
                count = response_data.get('count', len(conversations))
                print(f"✅ Found {count} conversations in history")
                return True, f"Found {count} conversations"
            else:
                print(f"✅ Response received: {response_data}")
                return True, "History endpoint works"
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error text: {response.text}")
            return False, f"History endpoint failed with status {response.status_code}"
            
    except Exception as e:
        return False, f"Error: {str(e)}"

def test_problem_3_create_ai_assistant_conversation():
    """
    PROBLEM 3.3: Create test AI Assistant conversation
    POST /api/ai/chat
    """
    print("\n" + "="*60)
    print("PROBLEM 3.3: Creating test AI Assistant conversation")
    print("="*60)
    
    url = f"{API_URL}/ai/chat"
    
    test_data = {
        "text": "Witaj! Kim jesteś?",
        "session_id": "test-history-assistant"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Sending POST request to: {url}")
        print(f"Request data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(url, json=test_data, headers=headers, timeout=30)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"✅ Response received: {json.dumps(response_data, indent=2)}")
            return True, "AI Assistant chat works"
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error text: {response.text}")
            return False, f"AI Assistant chat failed with status {response.status_code}"
            
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    """Run all 3 problem tests"""
    print("TESTING 3 PROBLEMS REPORTED BY USER")
    print("Backend URL:", BASE_URL)
    
    results = {}
    
    # PROBLEM 1: Scraping search_terms error
    print("\n" + "🔍 TESTING PROBLEM 1: Scraping Conrad/TME/RS 'search_terms' error")
    success, message = test_problem_1_scraping_search_terms()
    results['problem_1'] = {'success': success, 'message': message}
    
    # PROBLEM 2: AI Analyst chat history
    print("\n" + "🤖 TESTING PROBLEM 2: AI Analyst chat history")
    
    # 2.1: Check sessions
    success, message, sessions = test_problem_2_ai_analyst_sessions()
    results['problem_2_sessions'] = {'success': success, 'message': message}
    
    if success and sessions and isinstance(sessions, list) and len(sessions) > 0:
        # 2.2: Check history for existing session
        session_id = sessions[0].get('session_id') or sessions[0].get('id') or 'test-session'
        success, message = test_problem_2_ai_analyst_history(session_id)
        results['problem_2_history'] = {'success': success, 'message': message}
    else:
        # 2.3: Create new conversation and check sessions again
        success, message = test_problem_2_create_ai_analyst_conversation()
        results['problem_2_create'] = {'success': success, 'message': message}
        
        if success:
            # Check sessions again
            success, message, sessions = test_problem_2_ai_analyst_sessions()
            results['problem_2_sessions_after'] = {'success': success, 'message': message}
    
    # PROBLEM 3: AI Assistant chat history
    print("\n" + "💬 TESTING PROBLEM 3: AI Assistant chat history")
    
    # 3.1: Check sessions
    success, message, sessions = test_problem_3_ai_assistant_sessions()
    results['problem_3_sessions'] = {'success': success, 'message': message}
    
    if success and sessions and isinstance(sessions, list) and len(sessions) > 0:
        # 3.2: Check history for existing session
        session_id = sessions[0].get('session_id') or sessions[0].get('id') or 'test-session'
        success, message = test_problem_3_ai_assistant_history(session_id)
        results['problem_3_history'] = {'success': success, 'message': message}
    else:
        # 3.3: Create new conversation and check sessions again
        success, message = test_problem_3_create_ai_assistant_conversation()
        results['problem_3_create'] = {'success': success, 'message': message}
        
        if success:
            # Check sessions again
            success, message, sessions = test_problem_3_ai_assistant_sessions()
            results['problem_3_sessions_after'] = {'success': success, 'message': message}
    
    # SUMMARY
    print("\n" + "="*80)
    print("SUMMARY OF 3 PROBLEMS TESTING")
    print("="*80)
    
    for problem, result in results.items():
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{problem}: {status} - {result['message']}")
    
    return results

if __name__ == "__main__":
    main()