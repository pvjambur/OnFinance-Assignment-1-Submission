import logging.config
import structlog
from .settings import settings

def configure_logging():
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "plain": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            },
            "json": {
                "format": "%(message)s",
                "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "plain",
                "level": settings.LOG_LEVEL,
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": "app.log",
                "formatter": "plain",
                "level": "DEBUG",
            },
        },
        "loggers": {
            "": {
                "handlers": ["console", "file"],
                "level": settings.LOG_LEVEL,
            },
            "httpcore": {"level": "WARNING"},
            "httpx": {"level": "WARNING"},
            "urllib3": {"level": "WARNING"},
        },
    })
