from typing import List, Union, Dict, Any, Optional
import json
from app.utils.localization import localization
from app.utils.logger import error


class UserConfig:
    """User-specific configuration class that replaces the global config."""
    
    def __init__(self, config_data: Dict[str, Any]):
        self.user_id = config_data.get('user_id')
        self.api_id = config_data.get('api_id', 0)
        self.api_hash = config_data.get('api_hash', '')
        self.phone_number = config_data.get('phone_number', '')
        self.channel_id = self._parse_channel_id(config_data.get('channel_id', ''))
        self.interval = config_data.get('interval', 15.0)
        self.language = config_data.get('language', 'en').lower()
        self.gift_ranges = self._parse_gift_ranges(config_data.get('gift_ranges', []))
        self.purchase_only_upgradable_gifts = config_data.get('purchase_only_upgradable_gifts', False)
        self.prioritize_low_supply = config_data.get('prioritize_low_supply', False)
        self.is_active = config_data.get('is_active', False)
        self.session_file_path = config_data.get('session_file_path', f"data/sessions/user_{self.user_id}")
        
        # Set localization for this user
        localization.set_locale(self.language)

    def _parse_channel_id(self, channel_value: str) -> Union[int, str, None]:
        """Parse channel ID from string value."""
        if not channel_value or channel_value == '-100':
            return None

        if channel_value.startswith('@'):
            return channel_value

        if channel_value.startswith('-') and channel_value[1:].isdigit():
            return int(channel_value)

        if channel_value.isdigit():
            return int(channel_value)

        return f"@{channel_value}"

    def _parse_gift_ranges(self, gift_ranges_data) -> List[Dict[str, Any]]:
        """Parse gift ranges from database format."""
        if isinstance(gift_ranges_data, str):
            try:
                gift_ranges_data = json.loads(gift_ranges_data)
            except json.JSONDecodeError:
                error(f"Invalid JSON in gift_ranges for user {self.user_id}")
                return []
        
        if not isinstance(gift_ranges_data, list):
            return []
        
        ranges = []
        for range_config in gift_ranges_data:
            if isinstance(range_config, dict) and all(
                key in range_config for key in ['min_price', 'max_price', 'supply_limit', 'quantity', 'recipients']
            ):
                # Ensure recipients are properly parsed
                recipients = range_config['recipients']
                if isinstance(recipients, str):
                    recipients = [r.strip() for r in recipients.split(',') if r.strip()]
                
                parsed_recipients = []
                for recipient in recipients:
                    parsed_recipient = self._parse_single_recipient(recipient)
                    if parsed_recipient is not None:
                        parsed_recipients.append(parsed_recipient)
                
                range_config['recipients'] = parsed_recipients
                ranges.append(range_config)
        
        return ranges

    def _parse_single_recipient(self, recipient: str) -> Union[int, str, None]:
        """Parse a single recipient from string format."""
        recipient = recipient.strip()
        
        if recipient.startswith('@'):
            return recipient[1:]
        elif recipient.isdigit():
            return int(recipient)
        else:
            return recipient

    def get_matching_range(self, price: int, total_amount: int) -> tuple[bool, int, List[Union[int, str]]]:
        """Get matching range for a gift based on price and supply."""
        matching_ranges = [
            (range_config['quantity'], range_config['recipients'])
            for range_config in self.gift_ranges
            if (range_config['min_price'] <= price <= range_config['max_price'] and
                total_amount <= range_config['supply_limit'])
        ]

        return (True, *matching_ranges[0]) if matching_ranges else (False, 0, [])

    @property
    def language_display(self) -> str:
        return localization.get_display_name(self.language)

    @property
    def language_code(self) -> str:
        return localization.get_language_code(self.language)

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for database storage."""
        return {
            'user_id': self.user_id,
            'api_id': self.api_id,
            'api_hash': self.api_hash,
            'phone_number': self.phone_number,
            'channel_id': str(self.channel_id) if self.channel_id else None,
            'interval': self.interval,
            'language': self.language,
            'gift_ranges': self.gift_ranges,
            'purchase_only_upgradable_gifts': self.purchase_only_upgradable_gifts,
            'prioritize_low_supply': self.prioritize_low_supply,
            'is_active': self.is_active,
            'session_file_path': self.session_file_path
        }