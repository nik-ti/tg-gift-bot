# Telegram Gifts Buyer

<img src="https://github.com/user-attachments/assets/40f64ac9-ff84-4b31-85fd-b6ab01116bdb" alt="Program Preview" width="100%" />

**Multi-User Telegram Gifts Buyer Bot** - A scalable service that allows multiple users to configure and run their own automated gift purchasing bots through a simple Telegram interface.

> 🌐 [Русская версия](README-RU.md)

## ✨ Features

- **👥 Multi-User Support**: Multiple users can configure and run their own bots
- **💬 Telegram Interface**: Complete setup and management through Telegram commands
- **🔐 User Authorization**: Admin-controlled access with user management
- **🤖 Individual Bot Instances**: Each user gets their own monitoring and purchasing bot
- **⚙️ Per-User Configuration**: Individual settings for price ranges, recipients, and preferences
- **🎯 Smart Prioritization**: Prioritizes rare gifts (low supply) within price ranges
- **💰 Balance Management**: Makes partial purchases when balance is insufficient
- **📊 Real-time Notifications**: Purchase confirmations and processing summaries
- **🌍 Multi-Language**: English and Russian interface
- **☁️ Database Storage**: User configurations stored in Supabase

## 🚀 Installation

```bash
git clone https://github.com/bohd4nx/Gifts-Buyer.git
cd Gifts-Buyer
pip install -r requirements.txt
```

## 🗄️ Database Setup

This bot uses Supabase for storing user configurations. You need to:

1. Create a Supabase project at https://supabase.com
2. Copy `.env.example` to `.env` and fill in your Supabase credentials
3. Run the database migrations (tables will be created automatically)

Edit `config.ini` with your main bot settings and run:

```bash
python main.py
```

## 🐳 Docker Usage

You can run the bot via Docker. The process includes one-time Telegram authorization and background launch.

### 1. Build the Docker image

```bash
docker compose build
```

### 2. Run the container for Telegram login (one-time setup)

```bash
docker compose run --rm gift-buyer
```

Follow the prompts to complete Telegram authorization. Your session will be saved in the `./data/` directory.

> ℹ️ This step is only required once — until your session expires or you change accounts.

### 3. Start the bot in background mode

```bash
docker compose up -d
```

The bot will start using the saved session and configuration.

### 4. Stop the bot (when needed)

```bash
docker compose down
```

## ⚙️ Configuration

### Main Bot Settings (config.ini)

The `config.ini` now only contains settings for the main bot that handles Telegram commands:

```ini
[Telegram]
API_ID = your_main_bot_api_id          # From https://my.telegram.org/apps
API_HASH = your_main_bot_api_hash      # From https://my.telegram.org/apps  
PHONE_NUMBER = +1234567890             # Main bot phone number

[Bot]
LANGUAGE = EN                          # Main bot interface language (EN/RU)
```

### User Configuration via Telegram

Users configure their individual bots through Telegram commands:

## 📱 Telegram Commands

### For Users:
- `/start` - Welcome message and available commands
- `/setup` - Configure your gift buying bot (guided setup)
- `/settings` - View your current configuration
- `/start_bot` - Start your gift buying bot
- `/stop` - Stop your gift buying bot

### For Admins:
- `/admin_users` - List all authorized users
- `/admin_add user_id [username] [admin:true/false]` - Add authorized user
- `/admin_remove user_id` - Remove authorized user

## 🔧 Setup Process

1. **Admin Setup**: Add authorized users using admin commands
2. **User Setup**: Authorized users run `/setup` to configure their bot:
   - API ID and API Hash (from https://my.telegram.org/apps)
   - Phone number
   - Notification channel
   - Check interval
   - Language preference
   - Gift ranges (price ranges, supply limits, quantities, recipients)
   - Additional options (upgradable only, prioritize low supply)
3. **Start Bot**: Users run `/start_bot` to activate their gift buying bot

## 🎯 Gift Ranges Format

During setup, users define gift ranges in this format:
`min_price-max_price:supply_limit:quantity:recipients`

**Examples**:
- `1-1000:500000:1:@johndoe,123456789` - Cheap gifts, 1 copy each
- `1001-5000:100000:2:@channel,@user` - Mid-range, 2 copies each  
- `5001-50000:50000:5:987654321` - Expensive gifts, 5 copies

Multiple ranges separated by semicolons (`;`)

## 💰 Smart Balance Management

The bot calculates how many gifts it can afford before attempting purchase:

```
Example:
- Gift costs 1500⭐, want to buy 4 copies
- Current balance: 4500⭐
- Result: Buys 3 copies, reports missing 1500⭐ for the last one
```

## 📝 Tips

- **For Admins**: Carefully manage authorized users to prevent abuse
- **For Users**: Keep balance 2-3x higher than your most expensive range
- **Setup**: Test with small ranges first before scaling up
- **Monitoring**: Enable notifications to track bot activity
- **Hosting**: Run on VPS for 24/7 operation
- **Security**: Each user's session and data are isolated

---

<div align="center">
    <h4>🚀 Built with ❤️ by <a href="https://t.me/bohd4nx">Bohdan</a> • <a href="https://app.tonkeeper.com/transfer/UQBUAa7KCx1ifmoEy6lF7j-822Dm_cE1j9SR7UWteu3jzukV?amount=0&text=Thanks%20for%20Gifts-Buyer">Donate</a></h4>
</div>
