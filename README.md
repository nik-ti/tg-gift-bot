# Telegram Gifts Buyer

<img src="https://github.com/user-attachments/assets/40f64ac9-ff84-4b31-85fd-b6ab01116bdb" alt="Program Preview" width="100%" />

**Multi-User Telegram Gifts Buyer Bot** - A scalable service that allows multiple users to configure and run their own automated gift purchasing bots through a simple Telegram interface.

> 🌐 [Русская версия](README-RU.md)

## ✨ Features

- **🤖 Telegram Bot Interface**: Users interact with a proper Telegram bot (created via @BotFather)
- **👥 Multi-User Support**: Multiple users can configure and run their own gift-buying bots
- **💬 Complete Telegram Interface**: Setup and management through bot commands
- **🔐 User Authorization**: Admin-controlled access with user management
- **🔄 Individual Bot Instances**: Each user gets their own monitoring and purchasing bot
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

## 🤖 Create Your Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow the instructions
3. Choose a name and username for your bot
4. Copy the bot token that BotFather provides

## 🗄️ Database Setup

This bot uses Supabase for storing user configurations. You need to:

1. Create a Supabase project at https://supabase.com
2. Copy `.env.example` to `.env` and fill in your Supabase credentials
3. Run the database migrations (tables will be created automatically)

## ⚙️ Configuration

Edit `config.ini` with your bot settings:

```ini
[Telegram]
BOT_TOKEN = your_bot_token_from_botfather

[Bot]
LANGUAGE = EN  # Interface language (EN/RU)
```

Then run:

```bash
python main.py
```

## 🐳 Docker Usage

You can run the bot via Docker:

### 1. Build the Docker image

```bash
docker compose build
```

### 2. Set up your configuration

- Copy `.env.example` to `.env` and add your Supabase credentials
- Update `config.ini` with your bot token

### 3. Start the bot

```bash
docker compose up -d
```

### 4. Stop the bot (when needed)

```bash
docker compose down
```

## 📱 Telegram Commands

Users interact with your bot through these commands:

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

1. **Create and Start Your Bot**: 
   - Create bot with @BotFather
   - Configure `config.ini` and start the service
   
2. **Admin Setup**: Add authorized users using admin commands

3. **User Setup**: Authorized users run `/setup` to configure their bot:
   - API ID and API Hash (from https://my.telegram.org/apps)
   - Phone number
   - Notification channel
   - Check interval
   - Language preference
   - Gift ranges (price ranges, supply limits, quantities, recipients)
   - Additional options (upgradable only, prioritize low supply)
   
4. **Start Bot**: Users run `/start_bot` to activate their gift buying bot

## 🎯 Gift Ranges Format

During setup, users define gift ranges in this format:
`min_price-max_price:supply_limit:quantity:recipients`

**Examples**:
- `1-1000:500000:1:@johndoe,123456789` - Cheap gifts, 1 copy each
- `1001-5000:100000:2:@channel,@user` - Mid-range, 2 copies each  
- `5001-50000:50000:5:987654321` - Expensive gifts, 5 copies

Multiple ranges separated by semicolons (`;`)

## 🏗️ Architecture

The bot uses a hybrid architecture:

- **Bot API Client**: Handles user interactions via Telegram Bot API
- **User Clients**: Individual Pyrogram user clients for gift purchasing
- **Database**: Supabase for storing user configurations and authorization
- **Multi-User Manager**: Orchestrates multiple user bot instances

## 💰 Smart Balance Management

The bot calculates how many gifts it can afford before attempting purchase:

```
Example:
- Gift costs 1500⭐, want to buy 4 copies
- Current balance: 4500⭐
- Result: Buys 3 copies, reports missing 1500⭐ for the last one
```

## 📝 Tips

- **Bot Setup**: Create a professional bot name and description via @BotFather
- **Admin Management**: Carefully control authorized users to prevent abuse
- **For Users**: Keep balance 2-3x higher than your most expensive range
- **Setup**: Test with small ranges first before scaling up
- **Monitoring**: Enable notifications to track bot activity
- **Hosting**: Run on VPS for 24/7 operation
- **Security**: Each user's session and data are isolated
- **Scaling**: The architecture supports hundreds of concurrent users

---

<div align="center">
    <h4>🚀 Built with ❤️ by <a href="https://t.me/bohd4nx">Bohdan</a> • <a href="https://app.tonkeeper.com/transfer/UQBUAa7KCx1ifmoEy6lF7j-822Dm_cE1j9SR7UWteu3jzukV?amount=0&text=Thanks%20for%20Gifts-Buyer">Donate</a></h4>
</div>
