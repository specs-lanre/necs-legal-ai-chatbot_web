from dotenv import load_dotenv
import os

load_dotenv()

DB_URL = os.getenv("DB_URL")
DEBUG = os.getenv("DEBUG")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-3.5-flash"











