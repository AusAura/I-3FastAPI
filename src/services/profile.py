from datetime import datetime

from src.utils.my_logger import logger


async def calculate_usage_days(created_at: datetime) -> int:
    logger.info(f"calculate_usage_days {type(created_at)}")
    now = datetime.now()
    delta = now.day - created_at.day
    return delta
