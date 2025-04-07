import logging
import asyncio

from config import settings
from parser.coinmarketcap import CoinMarketCup, Currencies


from confluent_kafka import Producer


producer = Producer(settings.kafka.producer_config)
logger = logging.getLogger(__name__)

async def main():
    cmc = CoinMarketCup()

    while True:
        try:
            pairs = await cmc.get_pairs(Currencies.OM)
            for pair in pairs:
                pair_json = pair.model_dump_json()
                producer.produce(
                    settings.kafka.topic,
                    value=pair_json,
                    key=f'OM/USDT')
            producer.flush()
            await asyncio.sleep(30)

        except Exception as error:
            logger.error(error)
            await asyncio.sleep(10)


if __name__ == '__main__':
    asyncio.run(main())
