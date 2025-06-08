import json
import os
from pathlib import Path
from typing import Dict, Optional, Any


class Storage:
    """Класс для хранения и управления пользовательскими данными в JSON-файле."""

    def __init__(self, file_path: str = None):
        """
        Инициализация хранилища.

        Args:
            file_path: Путь к файлу данных. Если не указан, используется user_data.json в корне проекта.
        """
        BASE_DIR = Path(__file__).parent.parent
        self.file_path = file_path or str(BASE_DIR / 'user_data.json')
        self.data: Dict[str, Dict] = self._load_data()
        self.stats = {
            'total_users': len(self.data),
            'active_users': sum(1 for user in self.data.values() if not user.get('banned', False)),
            'weather_requests': 0,
            'forecast_requests': 0
        }

    def _load_data(self) -> Dict[str, Dict]:
        """Загружает данные из JSON-файла или возвращает пустой словарь, если файл не существует."""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except json.JSONDecodeError:
            logging.error(f"Ошибка чтения файла {self.file_path}, создан новый файл")
        return {}

    def save_data(self) -> None:
        """Сохраняет текущие данные в JSON-файл."""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def get_user_data(self, user_id: int) -> Dict[str, Any]:
        """Возвращает все данные пользователя."""
        return self.data.get(str(user_id), {})

    def get_user_city(self, user_id: int) -> Optional[str]:
        """Возвращает сохраненный город пользователя."""
        return self.get_user_data(user_id).get('city')

    def set_user_city(self, user_id: int, city: str) -> None:
        """Устанавливает город для пользователя."""
        user_id = str(user_id)
        if user_id not in self.data:
            self.data[user_id] = {}
            self.stats['total_users'] = len(self.data)
        self.data[user_id]['city'] = city
        self.save_data()

    def get_user_language(self, user_id: int) -> str:
        """Возвращает язык пользователя (по умолчанию 'ru')."""
        return self.get_user_data(user_id).get('language', 'ru')

    def set_user_language(self, user_id: int, language: str) -> None:
        """Устанавливает язык для пользователя."""
        user_id = str(user_id)
        if user_id not in self.data:
            self.data[user_id] = {}
            self.stats['total_users'] = len(self.data)
        self.data[user_id]['language'] = language
        self.save_data()

    def increment_stat(self, stat_name: str) -> None:
        """Увеличивает счетчик статистики на 1."""
        if stat_name in self.stats:
            self.stats[stat_name] += 1
            self.save_data()

    def ban_user(self, user_id: int) -> None:
        """Блокирует пользователя."""
        user_id = str(user_id)
        self.data.setdefault(user_id, {})['banned'] = True
        self.save_data()
        self.stats['active_users'] = sum(1 for user in self.data.values() if not user.get('banned', False))

    def unban_user(self, user_id: int) -> None:
        """Разблокирует пользователя."""
        user_id = str(user_id)
        if user_id in self.data and 'banned' in self.data[user_id]:
            del self.data[user_id]['banned']
            self.save_data()
            self.stats['active_users'] = sum(1 for user in self.data.values() if not user.get('banned', False))

    def is_banned(self, user_id: int) -> bool:
        """Проверяет, заблокирован ли пользователь."""
        return self.get_user_data(user_id).get('banned', False)

    def get_stats(self) -> Dict[str, int]:
        """Возвращает текущую статистику."""
        return self.stats


# Глобальный экземпляр хранилища для использования в проекте
user_storage = Storage()