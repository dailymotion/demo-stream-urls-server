import os

DAILYMOTION_API_BASE_URL = "https://partner.api.dailymotion.com"

DAILYMOTION_API_OAUTH_TOKEN_URL = f"{DAILYMOTION_API_BASE_URL}/oauth/v1/token"
DAILYMOTION_API_VIDEO_URL = f"{DAILYMOTION_API_BASE_URL}/rest/video"

DAILYMOTION_API_CREDENTIALS_FILE = ".secrets/dailymotion_api_credentials.json"

CACHE_HOST = os.getenv("CACHE_HOST", "localhost")
