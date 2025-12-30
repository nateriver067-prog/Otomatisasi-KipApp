import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://kipapp.bps.go.id/api/v1"

USERNAME = os.getenv("KIP_USERNAME")
PASSWORD = os.getenv("KIP_PASSWORD")
NIP_LAMA = os.getenv("NIP_LAMA")

USER_AGENT = "Mozilla/5.0"
ONLY_LAST_MONTH = True
