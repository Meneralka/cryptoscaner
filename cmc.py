import requests
from json import loads as json
from typing import List, Dict
from app.schemas import Crypto

class CoinMarketCap:
    def __init__(self):
        # Базовый URL для API CoinMarketCap с параметрами для получения рыночных пар
        self.BASE_URL = (
            "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/market-pairs/latest"
            "?slug={}"  # Плейсхолдер для имени криптовалюты (например, bitcoin)
            "&start=1"  # Начальная позиция в списке пар
            "&quoteCurrencyId=825"  # ID валюты котировки (825 = USDT)
            "&limit=20"  # Ограничение на количество возвращаемых пар
            "&category=spot"  # Категория торгов (спотовая торговля)
            "&centerType=all"  # Тип бирж (все)
            "&sort=cmc_rank_advanced"  # Сортировка по продвинутому рангу CMC
            "&direction=desc"  # Направление сортировки (убывание)
            "&spotUntracked=true"  # Включение неотслеживаемых спотовых пар
        )

    def get_pairs_usdt(self, coin: str = 'bitcoin') -> List[Dict]:
        # Форматируем URL, подставляя имя криптовалюты (по умолчанию 'bitcoin')
        url = self.BASE_URL.format(coin)
        # Выполняем GET-запрос к API
        response = requests.get(url)

        # Проверяем статус ответа; если не 200, поднимаем исключение
        if response.status_code != 200:
            print(f"Response status not 200: {response.status_code}")
            # Логируем ошибку с кодом статуса
            raise Exception(f"API request failed with status code {response.status_code}")

        # Преобразуем JSON-ответ в словарь
        data = json(response.text)
        # Проверяем код ошибки в статусе ответа
        if data['status']['error_code'] != "0":  # API возвращает строки для error_code

            raise Exception(f"API error: {data['status']['error_message']}")

        # Извлекаем список рыночных пар из данных
        market_pairs = data['data']['marketPairs']
        # Инициализируем пустой список для хранения пар
        pairs = []
        # Проходим по каждой паре в marketPairs
        for pair in market_pairs:
            # Добавляем словарь с данными пары в список
            pairs += [{
                'marketId': pair['marketId'],  # Уникальный ID рынка
                'exchangeSlug': pair['exchangeSlug'],  # Идентификатор биржи
                'price': pair['price'],  # Цена пары
                'marketUrl': pair['marketUrl'],  # URL рынка
                'marketPair': pair['marketPair'],  # Торговая пара (например, BTC/USDT)
                'lastUpdated': pair['lastUpdated']  # Время последнего обновления
            }]
        # Возвращаем список пар
        return pairs