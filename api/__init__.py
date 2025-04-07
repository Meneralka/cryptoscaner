from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import crypto

class App:
    def __init__(self):
        """Конструктор FastAPI приложения"""
        self.app = FastAPI(title="Crypto List", version="1.0.0", prefix="/api")
        self._setup_cors()
        self._include_routers()


    def _setup_cors(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _include_routers(self):
        """Метод для подключения роутеров"""
        self.app.include_router(crypto.router)

    def get_app(self):
        """Метод для получения экземпляра FastAPI"""
        return self.app

