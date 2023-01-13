import logging.config
import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

logging.config.dictConfig(
    {
        "version": 1,
        "root": {
            "level": "DEBUG",
            "handlers": ["console"],
        },
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "asyncio": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "dm_stream_urls_server": {
                "level": "DEBUG",
                "handlers": ["console"],
                "propagate": False,
            },
        },
    },
)
