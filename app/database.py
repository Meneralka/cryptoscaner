import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.models import Base

# Параметры подключения
DB_USER = "postgres"              # Имя пользователя
DB_PASSWORD = "AYETATARi1337"    # Пароль
DB_HOST = "localhost"            # Хост
DB_PORT = "5432"                 # Порт
DB_NAME = "postgres"             # Имя базы данных
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


class Database:
    def __init__(self):
        self.engine = create_async_engine(DATABASE_URL)

    def new_session(self):
        return async_sessionmaker(self.engine, expire_on_commit=False)

    async def get_session(self):
        session = self.new_session()
        async with session() as session:
            yield session

    async def setup_database(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    db = Database()
    asyncio.run(db.setup_database())