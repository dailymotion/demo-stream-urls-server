import logging

import click

logger = logging.getLogger(__name__)


@click.command
def refresh_access_token_cache():
    """Refresh the access token cache"""

    # pylint: disable=import-outside-toplevel
    import asyncio

    from time import sleep

    from dm_stream_urls_server.cache import get_cache
    from dm_stream_urls_server.token import (
        refresh_dailymotion_api_access_token,
    )

    try:
        while True:
            cache = get_cache()

            if cache:
                asyncio.run(refresh_dailymotion_api_access_token(cache))

            sleep(60)
    except KeyboardInterrupt:  # CTRL+C (SIGINT) Here
        pass
    except Exception as e:  # pylint: disable=broad-except
        exception_type = type(e).__name__
        exception_message = str(e)

        logger.error(
            "Failed to refresh access token cache"
            "exception_type=%s, exception_message=%s",
            exception_type,
            exception_message,
        )


@click.command
def start_api():
    """Start the API"""

    # pylint: disable=import-outside-toplevel
    import uvicorn

    uvicorn.run(
        "dm_stream_urls_server.api:app",
        host="0.0.0.0",  # nosec
        access_log=True,
        log_level=logging.DEBUG,
        reload=False,
    )


@click.group()
def cli():
    """Dailymotion Stream URLs Server"""


if __name__ == "__main__":
    cli.add_command(refresh_access_token_cache)
    cli.add_command(start_api)

    cli()
