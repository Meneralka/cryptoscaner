from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy import select, func

from app.database import Database
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import CryptoPair


router = APIRouter(prefix='/pairs', tags=['Crypto-пары'])

# Определяем зависимость для получения сессии базы данных
# Annotated используется для типизации и внедрения зависимости через Depends
sessionDep = Annotated[AsyncSession, Depends(Database().get_session)]


@router.get('/best_pairs')
async def best_pairs(session: sessionDep, active: str ='BTC/USDT'):
    """
    Эндпоинт для получения пар с максимальной и минимальной ценой для указанной торговой пары (marketPair).

    Args:
        active (str): Торговая пара (по умолчанию 'BTC/USDT'), для которой ищутся лучшие цены.

    Returns:
        dict: Словарь с максимальной и минимальной ценой в виде списка объектов CryptoPair.
    """

    # Запрос для поиска записи с максимальной ценой для заданной пары

    query = select(CryptoPair).where(
        # Условие: цена равна максимальной цене И marketPair соответствует active
        CryptoPair.price == select(
            func.max(CryptoPair.price)).where(CryptoPair.marketPair == active
                                              ).where(
        CryptoPair.lastUpdated >= (datetime.utcnow() - timedelta(minutes=10))
    ).scalar_subquery()

    )

    result = await session.execute(query)
    max_price = result.scalar_one()

    # Запрос для поиска записи с минимальной ценой для заданной пары
    query = select(CryptoPair).where(
        CryptoPair.price == select(
            func.min(CryptoPair.price)
        ).where(CryptoPair.marketPair == active).where(
            CryptoPair.lastUpdated >= (datetime.utcnow() - timedelta(minutes=10))
        ).scalar_subquery()
    )

    result = await session.execute(query)
    min_price = result.scalar_one()

    # Возвращаем результат в виде словаря с максимальной и минимальной ценой
    return {'max_price': [max_price], 'min_price': [min_price]}


@router.get('/current_pairs')
async def current_pairs(session: sessionDep):
    """
    Эндпоинт для получения всех текущих торговых пар из базы данных.

    Returns:
        list: Список всех объектов CryptoPair из таблицы.
    """

    query = select(CryptoPair)
    result = await session.execute(query)
    return result.scalars().all()