import logging
from json import loads as json
from typing import List

import aiohttp

from confluent_kafka import Producer

from app.schemas import Crypto


KAFKA_BOOTSTRAP_SERVERS = 'host.docker.internal:9092'
KAFKA_TOPIC = 'crypto-pairs'
PRODUCER_CONFIG = {'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS}

try:
    PRODUCER = Producer(PRODUCER_CONFIG)
    print(f"Kafka Producer успешно инициализирован: {KAFKA_BOOTSTRAP_SERVERS}")
except Exception as e:
    print(f"Ошибка инициализации Kafka Producer: {e}")

logger = logging.getLogger(__name__)

def delivery_report(err, msg):
    if err is not None:
        print(f"Ошибка доставки: {err}")
    else:
        print(f"Сообщение доставлено в {msg.topic()} [partition {msg.partition()}]")

class CoinMarketCap:
    def __init__(self):
        # Базовый URL для API CoinMarketCap с параметрами для получения рыночных пар
        self.BASE_URL = (
            "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/market-pairs/latest"
            "?slug={}&start=1"  # Плейсхолдер для имени криптовалюты и начальная позиция
            "&quoteCurrencyId=825"  # ID валюты котировки (825 = USDT)
            "&limit=20"  # Ограничение на количество возвращаемых пар
            "&category=spot"  # Категория торгов (спотовая торговля)
            "&centerType=all"  # Тип бирж (все)
            "&sort=cmc_rank_advanced"  # Сортировка по продвинутому рангу CMC
            "&direction=desc"  # Направление сортировки (убывание)
            "&spotUntracked=true"  # Включение неотслеживаемых спотовых пар
        )

    async def get_pairs_usdt(self, coin: str = 'bitcoin') -> List[Crypto]:
        """
        Асинхронно получает список рыночных пар для указанной криптовалюты с котировкой в USDT.

        :Args:
            coin (str): Название криптовалюты (slug), по умолчанию 'bitcoin'.

        :Returns:
            List[Dict]: Список словарей с данными о рыночных парах.

        :Raises:
            Exception: Если запрос к API завершился неудачно или API вернул ошибку.
        """

        url = self.BASE_URL.format(coin)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    print(f"Ошибка: статус ответа {response.status}")
                    raise Exception(f"Запрос к API завершился с ошибкой: код {response.status}")

                text = await response.text()
                data = json(text)
                if data['status']['error_code'] != "0":
                    print(f"Ошибка API: {data['status']['error_message']}")
                    raise Exception(f"Ошибка API: {data['status']['error_message']}")

                market_pairs = data['data']['marketPairs']
                pairs = []
                for pair in market_pairs:
                    crypto_pair = Crypto(
                        marketId=pair['marketId'],
                        exchangeSlug=pair['exchangeSlug'],
                        price=pair['price'],
                        marketUrl=pair['marketUrl'],
                        marketPair=pair['marketPair']
                    )
                    pairs.append(crypto_pair)
                return pairs


async def main():
    cmc = CoinMarketCap()
    while True:
        try:
            pairs = await cmc.get_pairs_usdt("bitcoin")
            print('Пары получены')
            for pair in pairs:
                pair_json = pair.model_dump_json()
                PRODUCER.produce(
                    KAFKA_TOPIC,
                    value=pair_json.encode('utf-8'),
                    callback=delivery_report)
                PRODUCER.poll(0)

            PRODUCER.flush()
            print('Отправлено')
        except Exception as e:
            print(f"Произошла ошибка: {e}")
        await asyncio.sleep(5)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())