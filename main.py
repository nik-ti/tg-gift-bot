import asyncio
import traceback
import os

from pyrogram import Client

from app.core.banner import display_title, get_app_info, set_window_title
from app.core.multi_user_manager import MultiUserManager
from app.telegram.handlers import setup_handlers
from app.database import AuthManager
from app.utils.logger import info, error
from data.config import config, t, get_language_display

app_info = get_app_info()
multi_user_manager = MultiUserManager()
auth_manager = AuthManager()


class Application:
    @staticmethod
    async def run() -> None:
        set_window_title(app_info)
        display_title(app_info, get_language_display(config.LANGUAGE))

        # Create main bot client for handling Telegram commands
        main_bot = Client(
                name=config.SESSION,
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                phone_number=config.PHONE_NUMBER
        )
        
        # Setup Telegram command handlers
        setup_handlers(main_bot)
        
        async with main_bot:
            info("Main bot started - ready to accept commands")
            
            # Start all active user bots
            await multi_user_manager.start_all_active_users()
            
            # Keep the main bot running
            try:
                await asyncio.Event().wait()  # Run indefinitely
            except asyncio.CancelledError:
                info("Shutting down...")
                await multi_user_manager.stop_all_users()

    @staticmethod
    def main() -> None:
        # Check for required environment variables
        required_env_vars = ['SUPABASE_URL', 'SUPABASE_ANON_KEY']
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        
        if missing_vars:
            error(f"Missing required environment variables: {', '.join(missing_vars)}")
            error("Please set up Supabase connection first.")
            return
        
        try:
            asyncio.run(Application.run())
        except KeyboardInterrupt:
            info(t("console.terminated"))
        except Exception:
            error(t("console.unexpected_error"))
            traceback.print_exc()


Application.main() if __name__ == "__main__" else None
