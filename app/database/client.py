import os
from supabase import create_client, Client
from typing import Optional

_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """Get or create Supabase client instance."""
    global _supabase_client
    
    if _supabase_client is None:
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY environment variables must be set")
        
        _supabase_client = create_client(supabase_url, supabase_key)
    
    return _supabase_client