import erniebot
import os
from dotenv import load_dotenv

load_dotenv()
erniebot.api_type = "aistudio"
erniebot.access_token = os.getenv('ACCESS_TOKEN')

