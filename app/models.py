from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass

class CryptoPair(Base):
    __tablename__ = 'crypto_pairs'

    id: Mapped[int] = mapped_column(primary_key=True)
    marketUrl: Mapped[str]
    exchangeSlug: Mapped[str]
    price: Mapped[float]
    marketPair: Mapped[str]
    marketId: Mapped[int]
    lastUpdated: Mapped[str]
