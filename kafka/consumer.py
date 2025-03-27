import asyncio
import json
import logging

from config import settings

from confluent_kafka import Consumer, KafkaError

logger = logging.getLogger(__name__)

async def consume_messages():

    consumer = Consumer(settings.kafka.consumer_config)
    consumer.subscribe([settings.kafka.topic])

    while True:
        try:
            msg = consumer.poll(1.0)
            print(msg)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                logger.error('Consumer error: %s', msg.error())

            pair_json = msg.value().decode('utf-8')
            pair = json.loads(pair_json)




        except KafkaError as e:
            logger.error('Consumer error: %s', e)

        except Exception as e:
            logger.error('Consumer error: %s', e)
            await asyncio.sleep(1)




if __name__ == '__main__':
    asyncio.run(consume_messages())
