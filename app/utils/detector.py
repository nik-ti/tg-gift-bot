import asyncio
import json
import time
from typing import Any, Callable, Dict, List, Tuple
from pathlib import Path

from pyrogram import Client, types

from app.notifications import send_summary_message
from app.utils.logger import log_same_line, info
from data.config import t
from app.core.user_config import UserConfig


class GiftDetector:
    @staticmethod
    async def load_gift_history(user_id: int) -> Dict[int, dict]:
        """Load gift history for a specific user."""
        history_file = Path(f"data/history/user_{user_id}_history.json")
        try:
            with history_file.open("r", encoding='utf-8') as file:
                return {gift["id"]: gift for gift in json.load(file)}
        except FileNotFoundError:
            return {}

    @staticmethod
    async def save_gift_history(gifts: List[dict], user_id: int) -> None:
        """Save gift history for a specific user."""
        history_file = Path(f"data/history/user_{user_id}_history.json")
        history_file.parent.mkdir(parents=True, exist_ok=True)
        
        with history_file.open("w", encoding='utf-8') as file:
            json.dump(gifts, file, indent=4, default=types.Object.default, ensure_ascii=False)

    @staticmethod
    async def fetch_current_gifts(app: Client) -> Tuple[Dict[int, dict], List[int]]:
        gifts = [
            json.loads(json.dumps(gift, default=types.Object.default, ensure_ascii=False))
            for gift in await app.get_available_gifts()
        ]
        gifts_dict = {gift["id"]: gift for gift in gifts}
        return gifts_dict, list(gifts_dict.keys())

    @staticmethod
    def categorize_skipped_gifts(gift_data: Dict[str, Any], user_config: UserConfig) -> Dict[str, int]:
        skip_rules = {
            'sold_out_count': gift_data.get("is_sold_out", False),
            'non_limited_count': not gift_data.get("is_limited"),
            'non_upgradable_count': user_config.purchase_only_upgradable_gifts and "upgrade_price" not in gift_data
        }
        return {key: 1 if condition else 0 for key, condition in skip_rules.items()}

    @staticmethod
    def prioritize_gifts(gifts: Dict[int, dict], gift_ids: List[int], user_config: UserConfig) -> List[Tuple[int, dict]]:
        for gift_id, gift_data in gifts.items():
            gift_data["position"] = len(gift_ids) - gift_ids.index(gift_id)

        sorted_gifts = sorted(gifts.items(), key=lambda x: x[1]["position"])

        return sorted(sorted_gifts, key=lambda x: (
            x[1].get("total_amount", float('inf')) if x[1].get("is_limited", False) else float('inf'),
            x[1]["position"]
        )) if user_config.prioritize_low_supply else sorted_gifts


class GiftMonitor:
    @staticmethod
    async def run_detection_loop(app: Client, callback: Callable, user_config: UserConfig) -> None:
        """Run gift detection loop for a specific user."""
        animation_counter = 0
        user_id = user_config.user_id

        while True:
            animation_counter = (animation_counter + 1) % 4
            log_same_line(f'{t("console.gift_checking")}{"." * animation_counter}')
            time.sleep(0.2)

            app.is_connected or await app.start()

            old_gifts = await GiftDetector.load_gift_history(user_id)
            current_gifts, gift_ids = await GiftDetector.fetch_current_gifts(app)

            new_gifts = {
                gift_id: gift_data for gift_id, gift_data in current_gifts.items()
                if gift_id not in old_gifts
            }

            new_gifts and await GiftMonitor._process_new_gifts(app, new_gifts, gift_ids, callback, user_config)

            await GiftDetector.save_gift_history(list(current_gifts.values()), user_id)
            await asyncio.sleep(user_config.interval)

    @staticmethod
    async def _process_new_gifts(app: Client, new_gifts: Dict[int, dict], gift_ids: List[int], 
                                 callback: Callable, user_config: UserConfig) -> None:
        info(f'{t("console.new_gifts")} {len(new_gifts)}')

        skip_counts = {'sold_out_count': 0, 'non_limited_count': 0, 'non_upgradable_count': 0}

        for gift_data in new_gifts.values():
            gift_skips = GiftDetector.categorize_skipped_gifts(gift_data, user_config)
            for key, value in gift_skips.items():
                skip_counts[key] += value

        prioritized_gifts = GiftDetector.prioritize_gifts(new_gifts, gift_ids, user_config)

        for gift_id, gift_data in prioritized_gifts:
            gift_data['id'] = gift_id
            await callback(app, gift_data)

        await send_summary_message(app, **skip_counts)

        if any(skip_counts.values()):
            info(t("console.skip_summary",
                   sold_out=skip_counts['sold_out_count'],
                   non_limited=skip_counts['non_limited_count'],
                   non_upgradable=skip_counts['non_upgradable_count']))


gift_monitoring = GiftMonitor.run_detection_loop
