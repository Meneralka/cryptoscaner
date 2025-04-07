from typing import Dict

from pydantic import BaseModel
from pydantic_settings import BaseSettings

class DatabaseSettings(BaseModel):
    db_user: str = "postgres"  # Имя пользователя
    db_password: str = "veryhardpassword"  # Пароль
    db_host: str = "localhost"  # Хост
    db_port: str = "5432"  # Порт
    db_name: str = "postgres"  # Имя базы данных
    database_url: str = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


class KafkaSettings(BaseModel):
    bootstrap_host: str = 'host.docker.internal'
    bootstrap_port: int = 9092
    bootstrap_servers: str = 'host.docker.internal:9092'
    topic: str = 'crypto-pairs'
    producer_config: Dict = {'bootstrap.servers': bootstrap_servers}
    consumer_config: Dict = {
        'bootstrap.servers': bootstrap_servers,
        'group.id': 'crypto_worker_group',
        'auto.offset.reset': 'latest'
    }

class Settings(BaseSettings):
    kafka: KafkaSettings = KafkaSettings()
    database: DatabaseSettings = DatabaseSettings()


settings = Settings()
