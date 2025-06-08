import os
from pathlib import Path
from dotenv import load_dotenv

# Загрузка переменных окружения из файла
BASE_DIR = Path(__file__).parent.parent
env_path = BASE_DIR / 'keys.env'
load_dotenv(env_path)

# Конфигурационные данные (с fallback)
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
ADMINS = [int(x) for x in os.getenv("ADMIN_ID").split(",")]

# Настройки логирования
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / 'bot.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
