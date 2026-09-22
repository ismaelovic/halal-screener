"""Screening thresholds and the curated non-compliant sector/industry list.

No free/cheap fundamentals API has a per-category revenue breakdown, so the
"Five Percent Rule" business-activity screen is implemented as a core-business
exclusion list rather than a computed percentage — see the plan doc for why.
Sector/industry strings that aren't matched here (unmapped, or a
mixed/diversified business) fall through to the "review" status rather than
being assumed compliant.

Strings below are matched exactly (after lowercasing) against yfinance's
`sector`/`industry` fields — verified live against the full seed ticker list
(see providers/yfinance_provider.py's module docstring), not guessed.
"""

DEBT_RATIO_THRESHOLD = 0.33
CASH_RATIO_THRESHOLD = 0.33

# The whole "Financial Services" sector is excluded (conventional banking,
# insurance, credit services, capital markets, mortgage finance, asset
# management are all classified under it in Yahoo's taxonomy) — this alone
# catches every bank/insurer in the seed list (Danske, Nordea, SEB, Allianz,
# Sampo, JPM).
NON_COMPLIANT_SECTORS: set[str] = {
    "financial services",
}

NON_COMPLIANT_INDUSTRIES: set[str] = {
    # Conventional banking / interest-based lending & insurance — kept as a
    # second line of defense in case a future data source reports these
    # industries under a different sector than "Financial Services".
    "banks - diversified",
    "banks - regional",
    "consumer finance",
    "credit services",
    "insurance - diversified",
    "insurance - life",
    "insurance - property & casualty",
    "insurance - reinsurance",
    "insurance - specialty",
    "insurance brokers",
    "mortgage finance",
    # Alcohol
    "beverages - brewers",
    "beverages - wineries & distilleries",
    # Tobacco
    "tobacco",
    # Gambling
    "gambling",
    "resorts & casinos",
    # Pork / non-halal food processing
    "farm products",
    # Weapons / defense
    "aerospace & defense",
    # Adult entertainment — no dedicated public-market category observed;
    # kept defensively in case a data source ever reports one.
    "adult entertainment",
    "pornography",
}
