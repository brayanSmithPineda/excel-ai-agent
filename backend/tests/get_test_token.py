from app.config.settings import settings
from app.config.database import get_supabase_client
import asyncio #This is used to run the async code when you run the script by itself and not in the FastAPI app or server
from supabase import create_client, Client

async def get_jwt_token():
    supabase = get_supabase_client()
    try:
        """
        response = supabase.auth.sign_in_with_password(
            {
                "email": " pinedab606@gmail.com",
                "password": "0semeolvidO+"
            }
        )
        """

        #Try to create a new user if it does not exists
        EMAIL = "testuser@gmail.com"
        PASSWORD = "mc%k>5?^Eshki48"
        try:
            signup_response = supabase.auth.sign_up({
                "email": EMAIL,
                "password": PASSWORD
            })
        except Exception as e:
            print(f"user might already exists: {e}")
        
        #Now try to log in
        try:
            response = supabase.auth.sign_in_with_password({
                "email": EMAIL,
                "password": PASSWORD
            })
            #print token
            print(f"response: {response}")
        except Exception as e:
            print(f"loging error: {e}")

    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    token = asyncio.run(get_jwt_token())
    print(token)