from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy import select, func

from db.database import Database
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import CryptoPair


router = APIRouter(prefix='/pairs', tags=['Crypto-пары'])

# Определяем зависимость для получения сессии базы данных
# Annotated используется для типизации и внедрения зависимости через Depends
sessionDep = Annotated[AsyncSession, Depends(Database().get_session)]

@router.get('/all')
async def list_of_crypto(session: sessionDep):
    """
    Возвращает список доступных криптовалют и спреды для них
    :return:
    """

    query = select(CryptoPair.marketPair,
                   (func.max(CryptoPair.price) - func.min(CryptoPair.price)).label('spread'),
                   ((func.max(CryptoPair.price) - func.min(CryptoPair.price)) / (func.min(CryptoPair.price) // 100)).label('percent')
                   ).group_by(CryptoPair.marketPair)

    result = await session.execute(query)
    data = result.all()
    return {'data':[{'marketPair': pair,
                     'spreadUSDT': spread,
                     'percent': percent} for pair, spread, percent in data], 'statusCode': 200}

@router.get('/best_pairs')
async def best_pairs(session: sessionDep, active: str ='BTC/USDT'):
    """
    :param active:
    :param session:

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

    try:
        result = await session.execute(query)
        max_price = result.scalar_one()
    except:
        return {'data': [], 'statusCode': 404}

    # Запрос для поиска записи с минимальной ценой для заданной пары
    query = select(CryptoPair).where(
        CryptoPair.price == select(
            func.min(CryptoPair.price)
        ).where(CryptoPair.marketPair == active).where(
            CryptoPair.lastUpdated >= (datetime.utcnow() - timedelta(minutes=10))
        ).scalar_subquery()
    )
    try:
        result = await session.execute(query)
        min_price = result.scalar_one()
    except:
        return {'data':[], 'statusCode': 404}


    return {"data" : {'max_price': [max_price], 'min_price': [min_price]}, 'statusCode': 200}
