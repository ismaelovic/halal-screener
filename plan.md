# Roadmap / Open Tickets

Tracked here until this project has a real issue tracker. Not in scope for the V1 MVP delivered so far — see `README.md` for what's already built.

Status legend: 🔲 open · 🚧 in progress · ✅ done

---

### TICKET-1: Change main/default language to Danish 🔲

Default UI copy is currently English. Switch the default locale to Danish (targeting the Nordic market per the original project brief).

- Audit all user-facing strings in `frontend/app/` and `frontend/src/components/` and move them into a translation layer instead of hardcoding.
- Danish becomes the default locale; English can remain as a fallback/secondary (see TICKET-2).

### TICKET-2: Add language-switching functionality

Once strings are externalized (TICKET-1), let the user switch language at runtime (e.g. Danish / English toggle).

- Needs an i18n library decision for Expo (e.g. `i18next` + `react-i18next`, or `expo-localization` for device-default detection).
- Persist the user's choice (e.g. `AsyncStorage`) so it survives app restarts.
- Decide default: device locale if supported, else Danish (per TICKET-1), with manual override.

### TICKET-3: Redesign UI — currently too bare-bones ✅

Current screens (`app/index.tsx`, `app/stock/[ticker].tsx`) are functional but visually look like a scaffold/HelloWorld app, not a product.

- Needs an actual design pass: spacing, typography, color palette, iconography for verdicts (not just colored text), polished `VerdictCard`/`RatioBreakdown`/`SearchBar` components.
- Consider a lightweight component/styling library (e.g. `nativewind`/Tailwind-for-RN, `tamagui`, or `react-native-paper`) rather than hand-rolled `StyleSheet` for every component, to speed this up.
- Should still work identically across Expo Web and native.

**Shipped:** dark gradient-card aesthetic (NativeWind + `expo-linear-gradient` + `react-native-svg`); home screen shows "Recently screened" (persisted via `AsyncStorage`) and "Popular tickers" gradient cards; verdict card is a full gradient card with a big icon badge; debt/cash ratios render as circular SVG progress gauges against the AAOIFI threshold; search bar restyled as a dark pill. Verified on Expo Web.

### TICKET-4: Verify mobile-device preview (iPhone, Samsung, etc.) 🔲

Only tested via Expo Web (`npm run web`) so far — never previewed on an actual native device/simulator.

- Run via Expo Go on a real iPhone and Android device (or simulators: iOS Simulator, Android Emulator) and confirm layout, safe-area handling, and navigation work correctly outside the browser.
- Check that `EXPO_PUBLIC_API_BASE_URL` correctly resolves to the backend from a physical device (localhost won't work as-is — needs the dev machine's LAN IP or a tunnel).

### TICKET-5: Pull in live data instead of reading from seed ✅ (merged: [PR #1](https://github.com/ismaelovic/halal-screener/pull/1))

Search/screening currently only covers the ~42 tickers pre-loaded by `backend/src/halal_screener/scripts/seed.py` — there's no live/arbitrary ticker lookup.

- Extend `services/company_service.py` (or add a new path) to fall back to a live `provider.get_fundamentals()` / `provider.search()` call when a requested ticker isn't already in the `companies` table, then persist the result the same way `seed.py` does.
- Decide caching/refresh policy: how stale can a live-fetched `financial_ratios` row get before it's re-fetched (`fetched_at`-based TTL)?
- Consider rate-limiting/backoff given `yfinance` is an unofficial scraper (see README's "Data source" section) — a live per-request path is more exposed to throttling than the batch seed script.
- Frontend search (`SearchBar`) should surface a live-lookup result distinctly from an already-seeded one, or just make the seed list irrelevant once this ships.

**Shipped:** search merges local + live `yfinance` company-name results (verified: Yahoo's `symbol` field already matches our internal ticker/exchange convention); screening live-fetches and persists on cache miss or when cached data exceeds a 24h TTL (`FUNDAMENTALS_TTL_HOURS`); provider injected via FastAPI dependency so tests never hit real network; frontend search debounced 400ms.
