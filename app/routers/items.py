from typing import List, Annotated, Dict
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy import select, func

from app.database import Database  # Импортируем класс для работы с базой данных
from fastapi.logger import logger
from app.schemas import Crypto  # Схема данных для валидации
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, \
    AsyncSession  # Асинхронные инструменты SQLAlchemy
from app.models import Base, CryptoPair  # Модели базы данных
from cmc import CoinMarketCap  # Класс для работы с API CoinMarketCap

# Создаём маршрутизатор FastAPI с префиксом '/pairs' и тегом 'Crypto-пары'
router = APIRouter(prefix='/pairs', tags=['Crypto-пары'])

# Определяем зависимость для получения сессии базы данных
# Annotated используется для типизации и внедрения зависимости через Depends
sessionDep = Annotated[AsyncSession, Depends(Database().get_session)]


@router.get('/best_pairs')
async def best_pairs(session: sessionDep, active='BTC/USDT'):
    """
    Эндпоинт для получения пар с максимальной и минимальной ценой для указанной торговой пары (marketPair).

    Args:
        session (AsyncSession): Асинхронная сессия базы данных, внедряемая через зависимость.
        active (str): Торговая пара (по умолчанию 'BTC/USDT'), для которой ищутся лучшие цены.

    Returns:
        dict: Словарь с максимальной и минимальной ценой в виде списка объектов CryptoPair.
    """
    # Запрос для поиска записи с максимальной ценой для заданной пары
    query = select(CryptoPair).where(
        # Условие: цена равна максимальной цене (подзапрос) И marketPair соответствует active
        CryptoPair.price == select(func.max(CryptoPair.price)).scalar_subquery()
        and CryptoPair.marketPair == active
    )
    result = await session.execute(query)
    max_price = result.scalar_one()

    # Запрос для поиска записи с минимальной ценой для заданной пары
    query = select(CryptoPair).where(

        CryptoPair.price == select(func.min(CryptoPair.price)).scalar_subquery()
        and CryptoPair.marketPair == active
    )
    result = await session.execute(query)
    min_price = result.scalar_one()

    # Возвращаем результат в виде словаря с максимальной и минимальной ценой
    return {'max_price': [max_price], 'min_price': [min_price]}


@router.get('/current_pairs')
async def current_pairs(session: sessionDep):
    """
    Эндпоинт для получения всех текущих торговых пар из базы данных.

    Args:
        session (AsyncSession): Асинхронная сессия базы данных, внедряемая через зависимость.

    Returns:
        list: Список всех объектов CryptoPair из таблицы.
    """

    query = select(CryptoPair)
    result = await session.execute(query)
    return result.scalars().all()  # Возвращаем все записи как список объектов CryptoPair


@router.post('/update_pairs')
async def update_pairs(session: sessionDep):
    """
    Эндпоинт для обновления или добавления торговых пар в базу данных на основе данных от CoinMarketCap.

    Args:
        session (AsyncSession): Асинхронная сессия базы данных, внедряемая через зависимость.

    Returns:
        dict: Словарь с подтверждением успешного выполнения ('status': 'ok').
    """
    cmc = CoinMarketCap()  # Создаём экземпляр класса для работы с API CoinMarketCap
    pairs = cmc.get_pairs_usdt()  # Получаем список пар к USDT

    for i in pairs:
        smtm = select(CryptoPair).where(
            CryptoPair.marketId == i['marketId'] and CryptoPair.marketPair == i['MarketPair']
        )
        result = await session.execute(smtm)  # Выполняем запрос асинхронно
        existing_pair = result.scalar_one_or_none()  # Получаем одну запись или None

        if not existing_pair:
            # Если пара не существует, создаём новую
            new_pair = CryptoPair(
                marketUrl=i['marketUrl'],
                exchangeSlug=i['exchangeSlug'],
                price=i['price'],
                marketPair=i['marketPair'],
                marketId=i['marketId'],
                lastUpdated=i['lastUpdated']
            )

            session.add(new_pair)
        else:
            # Если пара существует, обновляем её цену и время последнего обновления
            existing_pair.price = i['price']
            existing_pair.lastUpdated = i['lastUpdated']

    await session.commit()
    return {'status': 'ok'}