from pydantic import BaseModel

class CryptoPair(BaseModel):
    marketUrl: str
    price: float
    marketPair: str
    marketId: int
    exchangeSlug: str