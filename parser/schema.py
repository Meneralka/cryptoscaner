from pydantic import BaseModel

class Crypto(BaseModel):
    marketUrl: str
    price: float
    marketPair: str
    marketId: int
    exchangeSlug: str