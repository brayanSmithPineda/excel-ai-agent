#!/usr/bin/env python3
"""
Get the user ID for the test user
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def get_test_user_id():
    """Get the user ID for the test user"""
    print("Getting test user ID...")
    
    # Get Supabase configuration
    supabase_url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not service_role_key:
        print("ERROR: Supabase URL or Service Role Key not found in environment variables.")
        return
    
    # Initialize Supabase client with service role
    supabase = create_client(supabase_url, service_role_key)
    
    # Test user email
    test_email = "testuser@gmail.com"
    
    try:
        # Get user by email
        result = supabase.auth.admin.list_users()
        
        for user in result:
            if user.email == test_email:
                print(f"SUCCESS: Found test user!")
                print(f"   Email: {user.email}")
                print(f"   User ID: {user.id}")
                return user.id
        
        print("ERROR: Test user not found")
        
    except Exception as e:
        print(f"ERROR: Error getting user: {e}")

if __name__ == "__main__":
    get_test_user_id()
