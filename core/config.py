from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    SERVER_URL : str = os.getenv("SERVER_URL")

settings = Settings()