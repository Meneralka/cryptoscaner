import asyncio
import logging
from confluent_kafka import Consumer, KafkaError
from typing import Dict
from json import loads

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Database
from app.models import CryptoPair
from app.schemas import Crypto

KAFKA_BOOTSTRAP_SERVERS = 'host.docker.internal:9092'
KAFKA_TOPIC = 'crypto-pairs'
KAFKA_GROUP_ID = 'crypto_worker_group'
CONSUMER_CONFIG = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': KAFKA_GROUP_ID,
        'auto.offset.reset': 'earliest'
    }


UPDATE_INTERVAL = 15

logger = logging.getLogger(__name__)


async def update_pairs(session: AsyncSession, pair_data: Dict):
    """
    Асинхронно обновляет или добавляет торговые пары в базу данных на основе данных от CoinMarketCap.
    """

    pair = Crypto(**pair_data)
    stmt = select(CryptoPair).where(
        CryptoPair.marketId == pair.marketId and CryptoPair.marketPair == pair.marketPair
    )
    result = await session.execute(stmt)
    existing_pair = result.scalar_one_or_none()

    if not existing_pair:
        new_pair = CryptoPair(
            marketUrl=pair.marketUrl,
            exchangeSlug=pair.exchangeSlug,
            price=pair.price,
            marketPair=pair.marketPair,
            marketId=pair.marketId
        )
        session.add(new_pair)
    else:
        existing_pair.price = pair.price
    await session.commit()



async def worker():
    db = Database()
    session_factory = db.new_session()

    CONSUMER = Consumer(CONSUMER_CONFIG)
    CONSUMER.subscribe([KAFKA_TOPIC])

    while True:
        try:
            msg = CONSUMER.poll(0.1)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    logger.error(f"Kafka ошибка: {msg.error()}")
                    break

            pair_json = msg.value().decode('utf-8')
            pair_data = loads(pair_json)

            async with session_factory() as session:
                await update_pairs(session, pair_data)
            print(f"Пары обновлены в {asyncio.get_event_loop().time()}")
        except Exception as e:
            print(f"Ошибка в воркере: {e}")
        await asyncio.sleep(UPDATE_INTERVAL)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    asyncio.run(worker())
