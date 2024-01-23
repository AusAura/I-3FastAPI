import redis

from src.conf.config import config
from src.utils.my_logger import logger


def get_cache():
    try:
        return redis.Redis(
            host=config.REDIS_DOMAIN,
            port=config.REDIS_PORT,
            db=0
        )
    except redis.ConnectionError as e:
        # TODO тут нам нужно упасть?/продолжить?/перезапустить?/сообщить?
        logger.error(e)
