from threading import settrace
from typing import Dict

from pydantic import BaseModel
from pydantic_settings import BaseSettings

class KafkaSettings(BaseModel):
    bootstrap_host: str = 'host.docker.internal'
    bootstrap_port: int = 9092
    bootstrap_servers: str = 'host.docker.internal:9092'
    topic: str = 'crypto-pairs'
    producer_config: Dict = {'bootstrap.servers': bootstrap_servers}

class Settings(BaseSettings):
    kafka: KafkaSettings = KafkaSettings()


settings = Settings()


