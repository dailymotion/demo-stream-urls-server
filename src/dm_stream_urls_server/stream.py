import aiohttp

from dm_stream_urls_server.config import DAILYMOTION_API_VIDEO_URL


async def get_stream_urls(
    video_id: str,
    video_formats: str,
    client_ip: str,
    authorization: str,
) -> dict:
    """Return the stream URLs for a video

    URLs will only be valid for the provided client IP address.
    """

    async with aiohttp.ClientSession(raise_for_status=True) as session:
        async with session.get(
            url=f"{DAILYMOTION_API_VIDEO_URL}/{video_id}",
            params={
                "client_ip": client_ip,
                "fields": video_formats,
            },
            headers={
                "Authorization": f"Bearer {authorization}",
            },
            timeout=2,
        ) as response:
            response_json: dict = await response.json()

            return response_json
