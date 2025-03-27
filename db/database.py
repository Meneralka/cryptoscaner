import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import settings
from db.models import Base

class Database:
    def __init__(self):
        self.engine = create_async_engine(settings.database.database_url)

    def new_session(self):
        return async_sessionmaker(self.engine, expire_on_commit=False)

    async def get_session(self):
        session = self.new_session()
        async with session() as session:
            yield session

    async def setup_database(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            print(settings.database.database_url)
            await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    db = Database()
    asyncio.run(db.setup_database())