from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
from typing import Optional
from .settings import settings

class SupabaseManager:
    """
    Manages supabase client connections for the FastAPI app.
    provides both user-level and admin-level clients.
    """
    def __init__(self):
        self._client: Optional[Client] = None
        self._admin_client: Optional[Client] = None

    @property #This is a property decorator, it is used to define a property method, a property method is a method that is accessed like an attribute
    #for example, we can access the client as a attribute, like supabase.client, instead of calling a method like supabase.client()
    def client(self) -> Client:
        """
        Get the user-level supabase client. Respects RLS policies. Uses anon key
        This client uses the anon key (anonymous user), which means the auth.uid() is going to be Null,
        So the RLS policies are going to be violated, which we can fix by using the admin client or by using the access token of the session.
        with supabase.auth.set_session(access_token, refresh_token = None) this tells who the user is, so the RLS policies are not violated.
        and the auth.uid() is not going to be Null but the user_id.
        """
        if self._client is None:
            self._client = create_client(
                supabase_url=settings.supabase_url,
                supabase_key=settings.supabase_anon_key.get_secret_value(),
                options=ClientOptions(
                    auto_refresh_token=True,
                    persist_session=True,
                    #debug mode is used to print the requests and responses to the console
                    postgrest_client_timeout=60,
                    schema="public"
                )
            )
        return self._client

    @property
    def admin_client(self) -> Client:
        """Get the admin-level supabase client. Uses service role key. No RLS policies"""
        if self._admin_client is None:
            self._admin_client = create_client(
                supabase_url=settings.supabase_url,
                supabase_key=settings.supabase_service_role_key.get_secret_value(),
                options=ClientOptions(
                    auto_refresh_token=False,
                    postgrest_client_timeout=60,
                    schema="public"
                )
            )
        return self._admin_client
    
    async def health_check(self) -> dict:
        """
        Check if supabase connection is working
        Return connection status and version info
        """
        try:
            #response = self.client.table("information_schema.tables")\
                #.select("table_name")\
                #.limit(1)\
                #.execute()
            response = self.client.from_("users").select("count", count="exact").limit(0).execute()
            
            return {
                "status": "healthy",
                "supabase_url": settings.supabase_url,
                "project_id": settings.supabase_project_id,
                "connection": "ok"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "supabase_url": settings.supabase_url,
            }
        
    def close(self):
        """
        Clean up client connections.
        Should be called when the app shuts down.
        """
        self._client = None
        self._admin_client = None

#Create global
supabase_manager = SupabaseManager()

#Convenience function to get the supabase client
def get_supabase_client() -> Client:
    """
    Get the supabase client for the current request.
    Uses the user-level client by default.
    """
    return supabase_manager.client

def get_supabase_admin_client() -> Client:
    """
    Get the supabase admin client.
    """
    return supabase_manager.admin_client

async def get_supabase_health() -> dict:
    """
    Get the health check of the supabase connection.
    """
    return await supabase_manager.health_check()