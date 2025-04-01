from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

DEEPSEEK_KEY = os.getenv('DEEPSEEK_TOKEN')

deepseek = OpenAI(api_key=DEEPSEEK_KEY, base_url="https://api.deepseek.com")