from app.config.settings import settings
from app.config.database import get_supabase_client
import asyncio #This is used to run the async code when you run the script by itself and not in the FastAPI app or server
from supabase import create_client, Client

async def get_jwt_token():
    supabase = get_supabase_client()
    try:
        password = input("Enter your password:")

        response = supabase.auth.sign_in_with_password(
            {
                "email": "pinedab606@gmail.com",
                "password": password
            }
        )

        if response.user and response.session:
            print("JWT token obtained successfully")
            print(f"\n🧪 Test command:")
            print(f'curl -H "Authorization: Bearer {response.session.access_token}" http://localhost:8000/test/jwt')
            return response.session.access_token
        else:
            print("Failed to get JWT token")

    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    token = asyncio.run(get_jwt_token())
    print(token)