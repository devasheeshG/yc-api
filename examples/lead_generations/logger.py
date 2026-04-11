import logging
import logging.config
from functools import lru_cache

@lru_cache
def get_logger() -> logging.Logger:
    """Get a logger instance."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s | %(levelname)-8s | %(message)s",
                    "datefmt": "%H:%M:%S",
                },
            },
            "handlers": {
                "stdout": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "default",
                },
            },
            "loggers": {
                "lead_gen": {
                    "handlers": ["stdout"],
                    "level": "INFO",
                    "propagate": False,
                },
                # Suppress noisy HTTP client logs
                "httpx": {"level": "WARNING"},
                "httpcore": {"level": "WARNING"},
            },
        }
    )

    return logger
