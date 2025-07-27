from typing import Optional, List, Dict, Any
from .client import get_supabase_client
from app.utils.logger import error, info


class AuthManager:
    def __init__(self):
        self.supabase = get_supabase_client()

    async def is_user_authorized(self, user_id: int) -> bool:
        """Check if a user is authorized to use the bot."""
        try:
            result = self.supabase.table('authorized_users').select('user_id').eq('user_id', user_id).execute()
            return len(result.data) > 0
        except Exception as ex:
            error(f"Error checking user authorization: {str(ex)}")
            return False

    async def add_authorized_user(self, user_id: int, username: Optional[str] = None, is_admin: bool = False) -> bool:
        """Add a user to the authorized users list."""
        try:
            data = {
                'user_id': user_id,
                'username': username,
                'is_admin': is_admin
            }
            self.supabase.table('authorized_users').insert(data).execute()
            info(f"Added authorized user: {user_id} (@{username})")
            return True
        except Exception as ex:
            error(f"Error adding authorized user: {str(ex)}")
            return False

    async def remove_authorized_user(self, user_id: int) -> bool:
        """Remove a user from the authorized users list."""
        try:
            self.supabase.table('authorized_users').delete().eq('user_id', user_id).execute()
            info(f"Removed authorized user: {user_id}")
            return True
        except Exception as ex:
            error(f"Error removing authorized user: {str(ex)}")
            return False

    async def get_authorized_users(self) -> List[Dict[str, Any]]:
        """Get all authorized users."""
        try:
            result = self.supabase.table('authorized_users').select('*').execute()
            return result.data
        except Exception as ex:
            error(f"Error fetching authorized users: {str(ex)}")
            return []

    async def is_user_admin(self, user_id: int) -> bool:
        """Check if a user has admin privileges."""
        try:
            result = self.supabase.table('authorized_users').select('is_admin').eq('user_id', user_id).execute()
            return len(result.data) > 0 and result.data[0].get('is_admin', False)
        except Exception as ex:
            error(f"Error checking admin status: {str(ex)}")
            return False