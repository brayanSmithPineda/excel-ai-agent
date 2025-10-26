#!/usr/bin/env python3
"""
Test script for backend JWT validation

This script tests the authentication flow:
1. Login to Supabase to get JWT token
2. Test authenticated request to chat endpoint
3. Test unauthenticated request (should fail)
"""

import requests
import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
BACKEND_URL = "https://127.0.0.1:8000"

def test_authentication():
    """Test the complete authentication flow"""
    
    print("Testing Supabase Authentication Flow")
    print("=" * 50)
    
    # Step 1: Initialize Supabase client
    print("1. Initializing Supabase client...")
    supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    
    # Step 2: Login to get JWT token
    print("2. Logging in to get JWT token...")
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": "test@example.com",
            "password": "TestPassword123!"
        })
        
        if auth_response.session:
            token = auth_response.session.access_token
            print(f"SUCCESS: Login successful! Token: {token[:20]}...")
        else:
            print("ERROR: Login failed - no session")
            return
            
    except Exception as e:
        print(f"ERROR: Login failed: {e}")
        print("TIP: Make sure you have created a test user in Supabase Dashboard")
        print("   Email: test@example.com")
        print("   Password: TestPassword123!")
        return
    
    # Step 3: Test authenticated request
    print("\n3. Testing authenticated request...")
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/chat/completion",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            json={
                "message": "Hello, this is a test with JWT authentication",
                "conversation_id": None,
                "enable_semantic_search": True,
                "enable_excel_search": True,
                "enable_hybrid_search": True
            },
            verify=False  # Skip SSL verification for localhost
        )
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS: Authenticated request successful!")
            print(f"   Response: {result.get('ai_response', '')[:100]}...")
            print(f"   Conversation ID: {result.get('conversation_id', 'N/A')}")
        else:
            print(f"ERROR: Authenticated request failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"ERROR: Authenticated request error: {e}")
    
    # Step 4: Test unauthenticated request (should fail)
    print("\n4. Testing unauthenticated request (should fail)...")
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/chat/completion",
            headers={"Content-Type": "application/json"},
            json={
                "message": "Hello, this should fail",
                "conversation_id": None
            },
            verify=False
        )
        
        if response.status_code == 401:
            print("SUCCESS: Unauthenticated request correctly rejected (401)")
        else:
            print(f"ERROR: Expected 401, got: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"ERROR: Unauthenticated request error: {e}")
    
    # Step 5: Test health endpoint (should work without auth)
    print("\n5. Testing health endpoint (should work without auth)...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", verify=False)
        
        if response.status_code == 200:
            print("SUCCESS: Health endpoint accessible without authentication")
        else:
            print(f"ERROR: Health endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"ERROR: Health endpoint error: {e}")
    
    print("\n" + "=" * 50)
    print("Authentication test completed!")

if __name__ == "__main__":
    test_authentication()
