from typing import Dict
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import CryptoPair
from parser.schema import Crypto

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
