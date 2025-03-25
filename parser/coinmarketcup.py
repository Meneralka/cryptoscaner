import asyncio
import logging

from enum import Enum
import aiohttp

from parser.schema import CryptoPair

logger = logging.getLogger(__name__)


class Currencies(Enum):
    BTC = 'bitcoin'
    ETH = 'ethereum'
    XRP = 'xrp'
    BNB = 'bnb'
    SOL = 'solana'


class CoinMarketCup:
    BASE_URL = (
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


    async def get_pairs(self, currency: Currencies):
        if not isinstance(currency, Currencies):
            raise TypeError('currency must be of type Currencies')

        async with aiohttp.ClientSession() as session:
            async with session.get(self.BASE_URL.format(currency.value)) as response:

                if response.status != 200:
                    raise (f'Failed to fetch data: {response.status}')

                data = await response.json()
                pairs = data['data']['marketPairs']

                if data['status']['error_code'] != '0':
                    raise Exception(f'Failed to fetch data: {data["status"]["error_message"]}')

                return [CryptoPair(marketId=pair['marketId'], exchangeSlug=pair['exchangeSlug'], price=pair['price'], marketUrl=pair['marketUrl'], marketPair=pair['marketPair']) for pair in pairs]


async def main():
    cmc = CoinMarketCup()
    pairs = await cmc.get_pairs(Currencies.ETH)
    print(pairs)


if __name__ == '__main__':
    asyncio.run(main())