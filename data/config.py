import configparser
import os
from pathlib import Path
from typing import Optional

from app.utils.localization import localization


class Config:
    def __init__(self):
        self.parser = configparser.ConfigParser()
        self.config_file = Path("config.ini")
        self._load_config()

    def _load_config(self) -> None:
        if not self.config_file.exists():
            self._create_default_config()

        self.parser.read(self.config_file, encoding='utf-8')

        # Telegram Bot Configuration
        self.BOT_TOKEN = self.parser.get('Telegram', 'BOT_TOKEN', fallback='')
        self.API_ID = self.parser.getint('Telegram', 'API_ID', fallback=0)
        self.API_HASH = self.parser.get('Telegram', 'API_HASH', fallback='')

        # Bot Configuration
        self.LANGUAGE = self.parser.get('Bot', 'LANGUAGE', fallback='EN').upper()

        # Set localization
        localization.set_locale(self.LANGUAGE.lower())

        # Validate required configuration
        self._validate_config()

    def _create_default_config(self) -> None:
        self.parser.add_section('Telegram')
        self.parser.set('Telegram', 'BOT_TOKEN', 'your_bot_token_from_botfather')
        self.parser.set('Telegram', 'API_ID', '0')
        self.parser.set('Telegram', 'API_HASH', 'your_api_hash_from_my_telegram_org')

        self.parser.add_section('Bot')
        self.parser.set('Bot', 'LANGUAGE', 'EN')

        with open(self.config_file, 'w', encoding='utf-8') as file:
            self.parser.write(file)

    def _validate_config(self) -> None:
        missing_configs = []

        if not self.BOT_TOKEN or self.BOT_TOKEN == 'your_bot_token_from_botfather':
            missing_configs.append("BOT_TOKEN - Get this from @BotFather")

        if not self.API_ID or self.API_ID == 0:
            missing_configs.append("API_ID - Get this from https://my.telegram.org/apps")

        if not self.API_HASH or self.API_HASH == 'your_api_hash_from_my_telegram_org':
            missing_configs.append("API_HASH - Get this from https://my.telegram.org/apps")

        if missing_configs:
            error_message = localization.translate('errors.missing_config').format('\n'.join(f"• {config}" for config in missing_configs))
            raise ValueError(error_message)

    @property
    def language_display(self) -> str:
        return localization.get_display_name(self.LANGUAGE.lower())


# Global config instance
config = Config()

# Translation function
def t(key: str, **kwargs) -> str:
    return localization.translate(key, **kwargs)

def get_language_display(language_code: str) -> str:
    return localization.get_display_name(language_code.lower())