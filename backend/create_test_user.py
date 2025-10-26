#!/usr/bin/env python3
"""
Create test user in Supabase for authentication testing

This script creates a test user in Supabase using the service role key.
Run this script to set up a test user for authentication testing.
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def create_test_user():
    """Create a test user in Supabase"""
    
    print("Creating test user in Supabase")
    print("=" * 50)
    
    # Get Supabase configuration
    supabase_url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not service_role_key:
        print("❌ Missing Supabase configuration")
        print("Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in your .env file")
        return
    
    # Initialize Supabase client with service role
    supabase = create_client(supabase_url, service_role_key)
    
    # Test user credentials
    test_email = "testuser@gmail.com"
    test_password = "mc%k>5?^Eshki48"
    
    try:
        # Create test user
        result = supabase.auth.admin.create_user({
            "email": test_email,
            "password": test_password,
            "email_confirm": True  # Auto-confirm email
        })
        
        if result.user:
            print(f"SUCCESS: Test user created successfully!")
            print(f"   Email: {test_email}")
            print(f"   Password: {test_password}")
            print(f"   User ID: {result.user.id}")
            print(f"   Email confirmed: {result.user.email_confirmed_at is not None}")
        else:
            print("ERROR: Failed to create test user")
            
    except Exception as e:
        if "already registered" in str(e).lower():
            print(f"SUCCESS: Test user already exists!")
            print(f"   Email: {test_email}")
            print(f"   Password: {test_password}")
        else:
            print(f"ERROR: Error creating test user: {e}")
            print("TIP: Make sure your service role key has admin permissions")

if __name__ == "__main__":
    create_test_user()
