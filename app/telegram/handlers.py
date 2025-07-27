from pyrogram import Client, filters
from pyrogram.types import Message
from .commands import (
    handle_start, handle_setup, handle_my_settings, handle_stop_bot,
    handle_start_bot, handle_admin_users, handle_admin_add_user,
    handle_admin_remove_user, handle_setup_step
)


def setup_handlers(app: Client):
    """Setup all Telegram message handlers."""
    
    # Basic commands
    app.add_handler(filters.command("start") & filters.private, handle_start)
    app.add_handler(filters.command("setup") & filters.private, handle_setup)
    app.add_handler(filters.command("settings") & filters.private, handle_my_settings)
    app.add_handler(filters.command("stop") & filters.private, handle_stop_bot)
    app.add_handler(filters.command("start_bot") & filters.private, handle_start_bot)
    
    # Admin commands
    app.add_handler(filters.command("admin_users") & filters.private, handle_admin_users)
    app.add_handler(filters.command("admin_add") & filters.private, handle_admin_add_user)
    app.add_handler(filters.command("admin_remove") & filters.private, handle_admin_remove_user)
    
    # Setup conversation handler
    app.add_handler(filters.text & filters.private, handle_setup_step)