from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime


class Base(DeclarativeBase):
    pass

class CryptoPair(Base):
    __tablename__ = 'crypto_pairs'

    id: Mapped[int] = mapped_column(primary_key=True)
    marketUrl: Mapped[str] = mapped_column('market_url')
    exchangeSlug: Mapped[str] = mapped_column('exchange_slug')
    price: Mapped[float] = mapped_column('price')
    marketPair: Mapped[str] = mapped_column('market_pair')
    marketId: Mapped[int] = mapped_column('market_id')
    lastUpdated: Mapped[datetime] = mapped_column('last_updated', server_default=func.now(), onupdate=func.now())