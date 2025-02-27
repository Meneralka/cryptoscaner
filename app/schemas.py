from pydantic import BaseModel, Field, AnyHttpUrl

class Crypto(BaseModel):
        marketUrl: str = AnyHttpUrl
        price: float
        marketPair: str
        marketId: int
        lastUpdated: str
        exchangeSlug: str


if __name__ == "__main__":
    pass
