import asyncio
from typing import Dict, Optional
from pyrogram import Client
from pathlib import Path

from app.database import UserConfigManager
from app.core.user_config import UserConfig
from app.core.callbacks import process_gift
from app.utils.detector import gift_monitoring
from app.notifications import send_start_message
from app.utils.logger import info, error, warn


class MultiUserManager:
    """Manages multiple user bot instances."""
    
    def __init__(self):
        self.user_config_manager = UserConfigManager()
        self.active_clients: Dict[int, Client] = {}
        self.active_tasks: Dict[int, asyncio.Task] = {}
        self.user_configs: Dict[int, UserConfig] = {}

    async def start_all_active_users(self):
        """Start bot instances for all active users."""
        active_users = await self.user_config_manager.get_active_users()
        
        info(f"Starting bots for {len(active_users)} active users")
        
        for user_data in active_users:
            user_id = user_data['user_id']
            try:
                await self.start_user_bot(user_id, user_data)
            except Exception as ex:
                error(f"Failed to start bot for user {user_id}: {str(ex)}")

    async def start_user_bot(self, user_id: int, user_data: Optional[Dict] = None):
        """Start bot instance for a specific user."""
        if user_id in self.active_clients:
            warn(f"Bot for user {user_id} is already running")
            return

        if not user_data:
            user_data = await self.user_config_manager.get_user_config(user_id)
            if not user_data:
                error(f"No configuration found for user {user_id}")
                return

        user_config = UserConfig(user_data)
        
        # Validate required fields
        if not all([user_config.api_id, user_config.api_hash, user_config.phone_number]):
            error(f"Incomplete configuration for user {user_id}")
            return

        # Ensure session directory exists
        session_dir = Path(user_config.session_file_path).parent
        session_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Create Pyrogram client
            client = Client(
                name=user_config.session_file_path,
                api_id=user_config.api_id,
                api_hash=user_config.api_hash,
                phone_number=user_config.phone_number
            )

            # Start client
            await client.start()
            
            # Store client and config
            self.active_clients[user_id] = client
            self.user_configs[user_id] = user_config
            
            # Send start notification
            await send_start_message(client)
            
            # Start gift monitoring task
            task = asyncio.create_task(
                self._run_user_monitoring(client, user_config)
            )
            self.active_tasks[user_id] = task
            
            info(f"Started bot for user {user_id}")
            
        except Exception as ex:
            error(f"Failed to start client for user {user_id}: {str(ex)}")
            await self.stop_user_bot(user_id)

    async def stop_user_bot(self, user_id: int):
        """Stop bot instance for a specific user."""
        # Cancel monitoring task
        if user_id in self.active_tasks:
            task = self.active_tasks[user_id]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            del self.active_tasks[user_id]

        # Stop and remove client
        if user_id in self.active_clients:
            client = self.active_clients[user_id]
            try:
                await client.stop()
            except Exception as ex:
                error(f"Error stopping client for user {user_id}: {str(ex)}")
            del self.active_clients[user_id]

        # Remove config
        if user_id in self.user_configs:
            del self.user_configs[user_id]

        info(f"Stopped bot for user {user_id}")

    async def restart_user_bot(self, user_id: int):
        """Restart bot instance for a specific user."""
        await self.stop_user_bot(user_id)
        await asyncio.sleep(1)  # Brief pause
        await self.start_user_bot(user_id)

    async def _run_user_monitoring(self, client: Client, user_config: UserConfig):
        """Run gift monitoring for a specific user."""
        try:
            # Create a wrapper function that passes the user config
            async def process_gift_with_config(app: Client, gift_data: Dict):
                return await process_gift(app, gift_data, user_config)
            
            await gift_monitoring(client, process_gift_with_config, user_config)
        except asyncio.CancelledError:
            info(f"Monitoring cancelled for user {user_config.user_id}")
        except Exception as ex:
            error(f"Monitoring error for user {user_config.user_id}: {str(ex)}")

    async def stop_all_users(self):
        """Stop all active user bots."""
        user_ids = list(self.active_clients.keys())
        for user_id in user_ids:
            await self.stop_user_bot(user_id)

    def get_active_user_count(self) -> int:
        """Get number of active users."""
        return len(self.active_clients)

    def is_user_active(self, user_id: int) -> bool:
        """Check if a user's bot is currently active."""
        return user_id in self.active_clients