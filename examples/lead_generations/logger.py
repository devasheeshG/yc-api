import logging
import logging.config
from contextvars import ContextVar
from functools import lru_cache

# Set this per-task to tag all log messages with the company name
current_company: ContextVar[str] = ContextVar("current_company", default="")


class _CompanyFilter(logging.Filter):
    def filter(self, record):
        record.company = current_company.get()
        return True


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
                    "format": "%(asctime)s | %(levelname)-8s | %(company)-20s | %(message)s",
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
                "root": {
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

    for handler in logging.getLogger().handlers:
        handler.addFilter(_CompanyFilter())

    return logger
