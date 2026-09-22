"""FastAPI dependency for the fundamentals provider — lets tests swap in a
fake provider via `app.dependency_overrides` so they never hit real network.
"""

from functools import lru_cache

from halal_screener.providers.base import FundamentalsProvider
from halal_screener.providers.yfinance_provider import YFinanceProvider


@lru_cache
def get_fundamentals_provider() -> FundamentalsProvider:
    return YFinanceProvider()
