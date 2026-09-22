"""Provider abstraction — lets the fundamentals data source be swapped later
(e.g. adding Financial Modeling Prep) without touching the screening engine
or API layer.
"""

from abc import ABC, abstractmethod

from halal_screener.providers.schemas import RawFundamentals, SearchResult


class FundamentalsProvider(ABC):
    @abstractmethod
    def search(self, query: str) -> list[SearchResult]:
        """Look up tickers by name/symbol fragment."""

    @abstractmethod
    def get_fundamentals(self, ticker: str, exchange: str) -> RawFundamentals:
        """Fetch normalized fundamentals for a single ticker.exchange pair."""
