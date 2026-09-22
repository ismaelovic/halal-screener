"""One-time, resumable backfill of the seed ticker list into the database.

Rate-limit-friendly by design (Yahoo Finance can throttle/block scraping if
hit too fast): sleeps between calls, and supports --start-from / --only so a
partial run can resume without re-fetching tickers already done. Never run
this in CI — it hits the real (unofficial) Yahoo Finance API.

Usage:
    uv run python -m halal_screener.scripts.seed
    uv run python -m halal_screener.scripts.seed --start-from NOVO-B.CO
    uv run python -m halal_screener.scripts.seed --only AAPL.US,MSFT.US
"""

import argparse
import sys
import time

from sqlmodel import Session

from halal_screener.database import create_db_and_tables, engine
from halal_screener.providers.yfinance_provider import YFinanceProvider
from halal_screener.services.screening_service import screen_and_persist, upsert_company

# Draft list of ~40 tickers: Nordic/European names (repo_plan.md's target
# market) plus a handful of global names and deliberate non-compliant test
# cases (banks, insurers, a brewery, tobacco) to exercise every verdict
# branch. Exchange codes match Yahoo Finance's own ticker suffixes directly
# (verified live) — "DE" for Xetra, "L" for London, no suffix for "US".
# NOVOZ-B.CO and CHR.CO were dropped: both merged into Novonesis in 2024 and
# no longer trade under their old tickers; NSIS-B.CO covers the merged
# entity (still shows under its pre-merger name "Novozymes A/S" on Yahoo).
SEED_TICKERS: list[tuple[str, str]] = [
    ("NOVO-B", "CO"),
    ("MAERSK-B", "CO"),
    ("ORSTED", "CO"),
    ("VWS", "CO"),
    ("CARL-B", "CO"),
    ("DANSKE", "CO"),
    ("DSV", "CO"),
    ("NSIS-B", "CO"),
    ("GMAB", "CO"),
    ("COLO-B", "CO"),
    ("AMBU-B", "CO"),
    ("EQNR", "OL"),
    ("NHY", "OL"),
    ("TEL", "OL"),
    ("TOM", "OL"),
    ("VOLV-B", "ST"),
    ("HM-B", "ST"),
    ("NDA-SE", "ST"),
    ("SEB-A", "ST"),
    ("ATCO-A", "ST"),
    ("SAND", "ST"),
    ("EPI-A", "ST"),
    ("ASSA-B", "ST"),
    ("ERIC-B", "ST"),
    ("SAMPO", "HE"),
    ("NOKIA", "HE"),
    ("ASML", "AS"),
    ("SAP", "DE"),
    ("SIE", "DE"),
    ("ALV", "DE"),
    ("BAS", "DE"),
    ("MC", "PA"),
    ("AIR", "PA"),
    ("TTE", "PA"),
    ("DGE", "L"),
    ("BATS", "L"),
    ("AAPL", "US"),
    ("MSFT", "US"),
    ("TSLA", "US"),
    ("NVDA", "US"),
    ("JPM", "US"),
    ("PM", "US"),
]

SLEEP_SECONDS_BETWEEN_CALLS = 2.0


def run(tickers: list[tuple[str, str]]) -> None:
    create_db_and_tables()
    provider = YFinanceProvider()

    with Session(engine) as session:
        for i, (ticker, exchange) in enumerate(tickers, start=1):
            symbol = f"{ticker}.{exchange}"
            print(f"[{i}/{len(tickers)}] fetching {symbol} ...")
            try:
                fundamentals = provider.get_fundamentals(ticker, exchange)
                company = upsert_company(session, fundamentals)
                result = screen_and_persist(session, company, fundamentals)
                print(f"  -> {symbol}: {result.verdict} ({result.business_activity_status})")
            except Exception as exc:  # noqa: BLE001 — log, roll back, and keep going
                session.rollback()
                print(f"  !! failed to seed {symbol}: {exc}", file=sys.stderr)

            if i < len(tickers):
                time.sleep(SLEEP_SECONDS_BETWEEN_CALLS)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-from", help="Resume from this TICKER.EXCHANGE (inclusive)")
    parser.add_argument("--only", help="Comma-separated list of TICKER.EXCHANGE to seed")
    args = parser.parse_args()

    tickers = SEED_TICKERS
    if args.only:
        wanted = set(args.only.split(","))
        tickers = [(t, e) for t, e in tickers if f"{t}.{e}" in wanted]
    elif args.start_from:
        symbols = [f"{t}.{e}" for t, e in tickers]
        if args.start_from not in symbols:
            print(f"--start-from {args.start_from} not found in SEED_TICKERS", file=sys.stderr)
            sys.exit(1)
        tickers = tickers[symbols.index(args.start_from) :]

    run(tickers)


if __name__ == "__main__":
    main()
