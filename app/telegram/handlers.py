from pyrogram import Client, filters, handlers
from pyrogram.types import Message
from .commands import (
    handle_start, handle_setup, handle_my_settings, handle_stop_bot,
    handle_start_bot, handle_admin_users, handle_admin_add_user,
    handle_admin_remove_user, handle_setup_step
)


def setup_handlers(app: Client):
    """Setup all Telegram message handlers."""
    
    # Basic commands
    app.add_handler(handlers.MessageHandler(handle_start, filters.command("start") & filters.private))
    app.add_handler(handlers.MessageHandler(handle_setup, filters.command("setup") & filters.private))
    app.add_handler(handlers.MessageHandler(handle_my_settings, filters.command("settings") & filters.private))
    app.add_handler(handlers.MessageHandler(handle_stop_bot, filters.command("stop") & filters.private))
    app.add_handler(handlers.MessageHandler(handle_start_bot, filters.command("start_bot") & filters.private))
    
    # Admin commands
    app.add_handler(handlers.MessageHandler(handle_admin_users, filters.command("admin_users") & filters.private))
    app.add_handler(handlers.MessageHandler(handle_admin_add_user, filters.command("admin_add") & filters.private))
    app.add_handler(handlers.MessageHandler(handle_admin_remove_user, filters.command("admin_remove") & filters.private))
    
    # Setup conversation handler
    app.add_handler(handlers.MessageHandler(handle_setup_step, filters.text & filters.private))