import logging.config
import structlog
from .settings import settings

def configure_logging():
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "plain": {
                "format": "%(message)s",
            },
            "json": {
                "format": "%(message)s",
                "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            },
        },
        "handlers": {
            "console": {
                "class": "rich.logging.RichHandler",
                "formatter": "plain",
                "level": settings.LOG_LEVEL,
                "rich_tracebacks": True,
                "show_time": False,
                "show_path": False
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": "app.log",
                "formatter": "plain",
                "level": "DEBUG",
                "encoding": "utf-8"
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
