import asyncio
import json
import logging
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession
from confluent_kafka import Consumer, KafkaError

from db.update_pairs import update_pairs
from config import settings
from db.database import Database

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logger.addHandler(handler)

@asynccontextmanager
async def get_db_session():
    database = Database()
    session_factory = database.new_session()
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()

async def process_message(session: AsyncSession, message: bytes) -> None:
    try:
        pair_json = message.decode('utf-8')
        pair = json.loads(pair_json)

        await update_pairs(session, pair)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode message: {e}")
    except Exception as e:
        logger.error(f"Failed to process message: {e}")
        raise

async def consume_messages():
    consumer = Consumer(settings.kafka.consumer_config)
    consumer.subscribe([settings.kafka.topic])
    
    try:
        while True:
            try:
                msg = consumer.poll(0.1)
                
                if msg is None:
                    continue
                    
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        logger.info("Reached end of partition")
                        continue
                    logger.error(f"Consumer error: {msg.error()}")
                    continue

                async with get_db_session() as session:

                    await process_message(session, msg.value())
                    
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await asyncio.sleep(1)
                
    except KeyboardInterrupt:
        logger.info("Shutting down consumer...")
    finally:
        consumer.close()
        logger.info("Consumer closed")

if __name__ == '__main__':
    try:
        asyncio.run(consume_messages())
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
