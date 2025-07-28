import configparser
import sys
from pathlib import Path
from typing import Optional, List

from app.utils.localization import localization
from app.utils.logger import error


class Config:
    """Main bot configuration - now only for the Bot API bot interface."""
    
    def __init__(self):
        self.parser = configparser.ConfigParser()
        self._load_config()
        self._setup_properties()
        self._validate()
        localization.set_locale(self.LANGUAGE)

    def _load_config(self) -> None:
        config_file = Path('config.ini')
        config_file.exists() or self._exit_with_error("Configuration file 'config.ini' not found!")
        self.parser.read(config_file, encoding='utf-8')

    def _setup_properties(self) -> None:
        self.BOT_TOKEN = self.parser.get('Telegram', 'BOT_TOKEN', fallback='')
        self.LANGUAGE = self.parser.get('Bot', 'LANGUAGE', fallback='EN').lower()

    def _validate(self) -> None:
        validation_rules = {
            "Telegram > BOT_TOKEN": lambda: not self.BOT_TOKEN,
        }

        invalid_fields = [field for field, check in validation_rules.items() if check()]
        invalid_fields and self._exit_with_validation_error(invalid_fields)

    @staticmethod
    def _exit_with_error(message: str) -> None:
        error(message)
        sys.exit(1)

    def _exit_with_validation_error(self, invalid_fields: List[str]) -> None:
        error_msg = localization.translate("errors.missing_config").format(
            '\n'.join(f'- {field}' for field in invalid_fields))
        self._exit_with_error(error_msg)

    @property
    def language_display(self) -> str:
        return localization.get_display_name(self.LANGUAGE)

    @property
    def language_code(self) -> str:
        return localization.get_language_code(self.LANGUAGE)


config = Config()
t = localization.translate
get_language_display = localization.get_display_name
get_language_code = localization.get_language_code
