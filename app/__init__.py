from fastapi import FastAPI
from app.routers import items


class App:
    def __init__(self):
        """Конструктор FastAPI приложения"""
        self.app = FastAPI(title="FastAPI Project", version="1.0.0")
        self._include_routers()

    def _include_routers(self):
        """Метод для подключения роутеров"""
        self.app.include_router(items.router)

    def get_app(self):
        """Метод для получения экземпляра FastAPI"""
        return self.app

