from pydantic import BaseModel, Field, AnyHttpUrl
from datetime import datetime

class Crypto(BaseModel):
        marketUrl: str = AnyHttpUrl
        price: float
        marketPair: str
        marketId: int
        exchangeSlug: str


if __name__ == "__main__":
    pass
