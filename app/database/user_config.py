from typing import Optional, Dict, Any, List, Union
import json
from .client import get_supabase_client
from app.utils.logger import error, info


class UserConfigManager:
    def __init__(self):
        self.supabase = get_supabase_client()

    async def get_user_config(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user configuration from database."""
        try:
            result = self.supabase.table('user_configs').select('*').eq('user_id', user_id).execute()
            return result.data[0] if result.data else None
        except Exception as ex:
            error(f"Error fetching user config for {user_id}: {str(ex)}")
            return None

    async def create_user_config(self, user_id: int, config_data: Dict[str, Any]) -> bool:
        """Create a new user configuration."""
        try:
            config_data['user_id'] = user_id
            config_data['session_file_path'] = f"data/sessions/user_{user_id}"
            
            # Convert gift_ranges to JSON if it's a list
            if 'gift_ranges' in config_data and isinstance(config_data['gift_ranges'], list):
                config_data['gift_ranges'] = json.dumps(config_data['gift_ranges'])
            
            self.supabase.table('user_configs').insert(config_data).execute()
            info(f"Created config for user {user_id}")
            return True
        except Exception as ex:
            error(f"Error creating user config: {str(ex)}")
            return False

    async def update_user_config(self, user_id: int, config_data: Dict[str, Any]) -> bool:
        """Update user configuration."""
        try:
            config_data['updated_at'] = 'now()'
            
            # Convert gift_ranges to JSON if it's a list
            if 'gift_ranges' in config_data and isinstance(config_data['gift_ranges'], list):
                config_data['gift_ranges'] = json.dumps(config_data['gift_ranges'])
            
            self.supabase.table('user_configs').update(config_data).eq('user_id', user_id).execute()
            info(f"Updated config for user {user_id}")
            return True
        except Exception as ex:
            error(f"Error updating user config: {str(ex)}")
            return False

    async def delete_user_config(self, user_id: int) -> bool:
        """Delete user configuration."""
        try:
            self.supabase.table('user_configs').delete().eq('user_id', user_id).execute()
            info(f"Deleted config for user {user_id}")
            return True
        except Exception as ex:
            error(f"Error deleting user config: {str(ex)}")
            return False

    async def get_active_users(self) -> List[Dict[str, Any]]:
        """Get all active user configurations."""
        try:
            result = self.supabase.table('user_configs').select('*').eq('is_active', True).execute()
            return result.data
        except Exception as ex:
            error(f"Error fetching active users: {str(ex)}")
            return []

    async def set_user_active_status(self, user_id: int, is_active: bool) -> bool:
        """Set user's active status."""
        try:
            self.supabase.table('user_configs').update({
                'is_active': is_active,
                'updated_at': 'now()'
            }).eq('user_id', user_id).execute()
            info(f"Set user {user_id} active status to {is_active}")
            return True
        except Exception as ex:
            error(f"Error setting user active status: {str(ex)}")
            return False