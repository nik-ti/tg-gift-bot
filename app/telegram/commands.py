from pyrogram import Client
from pyrogram.types import Message
from typing import Dict, Any
import json

from app.database import UserConfigManager, AuthManager
from app.core.user_config import UserConfig
from app.core.multi_user_manager import MultiUserManager
from app.utils.logger import info, error
from data.config import t

# Global managers
user_config_manager = UserConfigManager()
auth_manager = AuthManager()
multi_user_manager = MultiUserManager()

# Store user setup states
user_setup_states: Dict[int, Dict[str, Any]] = {}


async def handle_start(client: Client, message: Message):
    """Handle /start command."""
    user_id = message.from_user.id
    username = message.from_user.username
    
    if not await auth_manager.is_user_authorized(user_id):
        await message.reply(
            "❌ You are not authorized to use this bot.\n"
            "Please contact the administrator for access."
        )
        return
    
    welcome_text = (
        f"🎁 **Welcome to Multi-User Gifts Buyer Bot!**\n\n"
        f"Hello @{username}! You are authorized to use this bot.\n\n"
        f"**Available Commands:**\n"
        f"• `/setup` - Configure your gift buying settings\n"
        f"• `/settings` - View your current configuration\n"
        f"• `/start_bot` - Start your gift buying bot\n"
        f"• `/stop` - Stop your gift buying bot\n\n"
        f"Use `/setup` to get started with configuring your bot!"
    )
    
    await message.reply(welcome_text)


async def handle_setup(client: Client, message: Message):
    """Handle /setup command to start configuration process."""
    user_id = message.from_user.id
    
    if not await auth_manager.is_user_authorized(user_id):
        await message.reply("❌ You are not authorized to use this bot.")
        return
    
    # Initialize setup state
    user_setup_states[user_id] = {
        'step': 'api_id',
        'config': {}
    }
    
    setup_text = (
        "🔧 **Bot Setup Process**\n\n"
        "I'll guide you through setting up your gift buying bot.\n\n"
        "**Step 1/8: API ID**\n"
        "Please provide your Telegram API ID.\n"
        "You can get this from https://my.telegram.org/apps\n\n"
        "Send me your API ID:"
    )
    
    await message.reply(setup_text)


async def handle_setup_step(client: Client, message: Message):
    """Handle setup conversation steps."""
    user_id = message.from_user.id
    
    if user_id not in user_setup_states:
        return
    
    state = user_setup_states[user_id]
    step = state['step']
    config = state['config']
    
    try:
        if step == 'api_id':
            config['api_id'] = int(message.text)
            state['step'] = 'api_hash'
            await message.reply(
                "✅ API ID saved!\n\n"
                "**Step 2/8: API Hash**\n"
                "Now send me your API Hash from the same page:"
            )
        
        elif step == 'api_hash':
            config['api_hash'] = message.text.strip()
            state['step'] = 'phone_number'
            await message.reply(
                "✅ API Hash saved!\n\n"
                "**Step 3/8: Phone Number**\n"
                "Send me your phone number (with country code, e.g., +1234567890):"
            )
        
        elif step == 'phone_number':
            config['phone_number'] = message.text.strip()
            state['step'] = 'channel_id'
            await message.reply(
                "✅ Phone number saved!\n\n"
                "**Step 4/8: Notification Channel**\n"
                "Send me your notification channel ID or username.\n"
                "Examples: @mychannel, -1001234567890\n"
                "Send '-100' to disable notifications:"
            )
        
        elif step == 'channel_id':
            config['channel_id'] = message.text.strip()
            state['step'] = 'interval'
            await message.reply(
                "✅ Channel ID saved!\n\n"
                "**Step 5/8: Check Interval**\n"
                "How often should the bot check for new gifts? (in seconds)\n"
                "Recommended: 10-30 seconds:"
            )
        
        elif step == 'interval':
            config['interval'] = float(message.text)
            state['step'] = 'language'
            await message.reply(
                "✅ Interval saved!\n\n"
                "**Step 6/8: Language**\n"
                "Choose your preferred language:\n"
                "Send 'en' for English or 'ru' for Russian:"
            )
        
        elif step == 'language':
            lang = message.text.strip().lower()
            if lang not in ['en', 'ru']:
                await message.reply("❌ Please send 'en' or 'ru'")
                return
            config['language'] = lang
            state['step'] = 'gift_ranges'
            await message.reply(
                "✅ Language saved!\n\n"
                "**Step 7/8: Gift Ranges**\n"
                "This is the most important step. Define your gift buying ranges.\n\n"
                "**Format:** `min_price-max_price:supply_limit:quantity:recipients`\n"
                "**Example:** `1-1000:500000:1:@username,123456789`\n\n"
                "You can add multiple ranges separated by semicolons (;)\n"
                "Send your gift ranges configuration:"
            )
        
        elif step == 'gift_ranges':
            ranges_text = message.text.strip()
            parsed_ranges = parse_gift_ranges_from_text(ranges_text)
            if not parsed_ranges:
                await message.reply(
                    "❌ Invalid format. Please use the correct format:\n"
                    "`min_price-max_price:supply_limit:quantity:recipients`"
                )
                return
            
            config['gift_ranges'] = parsed_ranges
            state['step'] = 'final_options'
            await message.reply(
                "✅ Gift ranges saved!\n\n"
                "**Step 8/8: Final Options**\n"
                "Send your preferences in this format:\n"
                "`upgradable_only:true/false,prioritize_low_supply:true/false`\n\n"
                "Example: `upgradable_only:false,prioritize_low_supply:true`"
            )
        
        elif step == 'final_options':
            options_text = message.text.strip()
            options = parse_final_options(options_text)
            config.update(options)
            
            # Save configuration
            success = await user_config_manager.create_user_config(user_id, config)
            
            if success:
                await message.reply(
                    "🎉 **Configuration Complete!**\n\n"
                    "Your bot has been configured successfully!\n"
                    "Use `/start_bot` to start your gift buying bot.\n"
                    "Use `/settings` to view your configuration."
                )
            else:
                await message.reply(
                    "❌ **Error saving configuration.**\n"
                    "Please try the setup process again with `/setup`"
                )
            
            # Clear setup state
            del user_setup_states[user_id]
    
    except ValueError as e:
        await message.reply(f"❌ Invalid input: {str(e)}\nPlease try again.")
    except Exception as e:
        error(f"Setup error for user {user_id}: {str(e)}")
        await message.reply("❌ An error occurred. Please try again.")


async def handle_my_settings(client: Client, message: Message):
    """Handle /settings command to show user configuration."""
    user_id = message.from_user.id
    
    if not await auth_manager.is_user_authorized(user_id):
        await message.reply("❌ You are not authorized to use this bot.")
        return
    
    config_data = await user_config_manager.get_user_config(user_id)
    
    if not config_data:
        await message.reply(
            "❌ No configuration found.\n"
            "Use `/setup` to configure your bot first."
        )
        return
    
    user_config = UserConfig(config_data)
    
    ranges_text = "\n".join([
        f"• {r['min_price']}-{r['max_price']} ⭐ (supply ≤ {r['supply_limit']}) x{r['quantity']} → {len(r['recipients'])} recipients"
        for r in user_config.gift_ranges
    ])
    
    settings_text = (
        f"⚙️ **Your Current Settings**\n\n"
        f"**Status:** {'🟢 Active' if user_config.is_active else '🔴 Inactive'}\n"
        f"**Language:** {user_config.language_display}\n"
        f"**Check Interval:** {user_config.interval}s\n"
        f"**Channel ID:** {user_config.channel_id or 'Disabled'}\n"
        f"**Only Upgradable:** {'Yes' if user_config.purchase_only_upgradable_gifts else 'No'}\n"
        f"**Prioritize Low Supply:** {'Yes' if user_config.prioritize_low_supply else 'No'}\n\n"
        f"**Gift Ranges:**\n{ranges_text}\n\n"
        f"Use `/setup` to reconfigure your settings."
    )
    
    await message.reply(settings_text)


async def handle_start_bot(client: Client, message: Message):
    """Handle /start_bot command."""
    user_id = message.from_user.id
    
    if not await auth_manager.is_user_authorized(user_id):
        await message.reply("❌ You are not authorized to use this bot.")
        return
    
    config_data = await user_config_manager.get_user_config(user_id)
    
    if not config_data:
        await message.reply(
            "❌ No configuration found.\n"
            "Use `/setup` to configure your bot first."
        )
        return
    
    success = await user_config_manager.set_user_active_status(user_id, True)
    
    if success:
        # Start the actual bot instance for this user
        await multi_user_manager.start_user_bot(user_id, config_data)
        
        await message.reply(
            "🟢 **Bot Started!**\n\n"
            "Your gift buying bot is now active and will start monitoring for new gifts.\n"
            "Use `/stop` to stop the bot."
        )
    else:
        await message.reply("❌ Failed to start bot. Please try again.")


async def handle_stop_bot(client: Client, message: Message):
    """Handle /stop command."""
    user_id = message.from_user.id
    
    if not await auth_manager.is_user_authorized(user_id):
        await message.reply("❌ You are not authorized to use this bot.")
        return
    
    success = await user_config_manager.set_user_active_status(user_id, False)
    
    if success:
        # Stop the actual bot instance for this user
        await multi_user_manager.stop_user_bot(user_id)
        
        await message.reply(
            "🔴 **Bot Stopped!**\n\n"
            "Your gift buying bot has been deactivated.\n"
            "Use `/start_bot` to start it again."
        )
    else:
        await message.reply("❌ Failed to stop bot. Please try again.")


async def handle_admin_users(client: Client, message: Message):
    """Handle /admin_users command (admin only)."""
    user_id = message.from_user.id
    
    if not await auth_manager.is_user_admin(user_id):
        await message.reply("❌ Admin access required.")
        return
    
    users = await auth_manager.get_authorized_users()
    
    if not users:
        await message.reply("No authorized users found.")
        return
    
    users_text = "\n".join([
        f"• {user['user_id']} (@{user.get('username', 'N/A')}) {'👑' if user.get('is_admin') else ''}"
        for user in users
    ])
    
    await message.reply(f"**Authorized Users:**\n{users_text}")


async def handle_admin_add_user(client: Client, message: Message):
    """Handle /admin_add command (admin only)."""
    user_id = message.from_user.id
    
    if not await auth_manager.is_user_admin(user_id):
        await message.reply("❌ Admin access required.")
        return
    
    args = message.text.split()[1:]
    if len(args) < 1:
        await message.reply("Usage: `/admin_add user_id [username] [admin:true/false]`")
        return
    
    try:
        target_user_id = int(args[0])
        username = args[1] if len(args) > 1 else None
        is_admin = len(args) > 2 and args[2].lower() == 'admin:true'
        
        success = await auth_manager.add_authorized_user(target_user_id, username, is_admin)
        
        if success:
            await message.reply(f"✅ Added user {target_user_id} to authorized users.")
        else:
            await message.reply("❌ Failed to add user.")
    
    except ValueError:
        await message.reply("❌ Invalid user ID.")


async def handle_admin_remove_user(client: Client, message: Message):
    """Handle /admin_remove command (admin only)."""
    user_id = message.from_user.id
    
    if not await auth_manager.is_user_admin(user_id):
        await message.reply("❌ Admin access required.")
        return
    
    args = message.text.split()[1:]
    if len(args) < 1:
        await message.reply("Usage: `/admin_remove user_id`")
        return
    
    try:
        target_user_id = int(args[0])
        success = await auth_manager.remove_authorized_user(target_user_id)
        
        if success:
            await message.reply(f"✅ Removed user {target_user_id} from authorized users.")
        else:
            await message.reply("❌ Failed to remove user.")
    
    except ValueError:
        await message.reply("❌ Invalid user ID.")


def parse_gift_ranges_from_text(ranges_text: str) -> list:
    """Parse gift ranges from user input text."""
    ranges = []
    
    for range_item in ranges_text.split(';'):
        range_item = range_item.strip()
        if not range_item:
            continue
        
        try:
            parts = range_item.split(':')
            if len(parts) != 4:
                continue
            
            price_range, supply_limit, quantity, recipients = parts
            min_price, max_price = map(int, price_range.split('-'))
            supply_limit = int(supply_limit)
            quantity = int(quantity)
            recipients_list = [r.strip() for r in recipients.split(',') if r.strip()]
            
            ranges.append({
                'min_price': min_price,
                'max_price': max_price,
                'supply_limit': supply_limit,
                'quantity': quantity,
                'recipients': recipients_list
            })
        
        except (ValueError, IndexError):
            continue
    
    return ranges


def parse_final_options(options_text: str) -> dict:
    """Parse final options from user input."""
    options = {
        'purchase_only_upgradable_gifts': False,
        'prioritize_low_supply': False
    }
    
    try:
        for option in options_text.split(','):
            key, value = option.split(':')
            key = key.strip()
            value = value.strip().lower() == 'true'
            
            if key == 'upgradable_only':
                options['purchase_only_upgradable_gifts'] = value
            elif key == 'prioritize_low_supply':
                options['prioritize_low_supply'] = value
    
    except (ValueError, IndexError):
        pass
    
    return options