import os
from pathlib import Path
from dotenv import load_dotenv

# Загрузка переменных окружения из файла
BASE_DIR = Path(__file__).parent.parent
env_path = BASE_DIR / 'keys.env'
load_dotenv(env_path)

# Конфигурационные данные (с fallback)
BOT_TOKEN = os.getenv("BOT_TOKEN") or "8110482192:AAEeQ4HLdn5_Jnl2wNyrHYbXet0ApTKzSX0"
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY") or "ed4d9a651ca4a2bc035ce6069c493b08"
ADMINS = [int(x) for x in os.getenv("ADMIN_ID", "1848239453").split(",")]

# Настройки логирования
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / 'bot.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'