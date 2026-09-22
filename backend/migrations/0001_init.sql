-- 0001_init.sql
-- Keep this file in sync by hand with backend/src/halal_screener/models.py
-- (V1 uses raw SQL migrations against Supabase, not Alembic — see plan doc).
--
-- Apply with: psql "$SUPABASE_DB_URL" -f migrations/0001_init.sql

create extension if not exists pgcrypto;

create table if not exists companies (
    id uuid primary key default gen_random_uuid(),
    ticker text not null,
    exchange text not null,
    name text not null,
    country text,
    sector text,
    industry text,
    currency text,
    isin text,
    logo_url text,
    is_active boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (ticker, exchange)
);

create index if not exists idx_companies_name on companies (name);
create index if not exists idx_companies_ticker on companies (ticker);

create table if not exists financial_ratios (
    id uuid primary key default gen_random_uuid(),
    company_id uuid not null references companies (id) on delete cascade,
    as_of_date date,
    market_cap numeric,
    total_debt numeric,
    cash_and_equivalents numeric,
    total_revenue numeric,
    -- Reserved for V2 — no data source for these in V1 (see plan doc).
    non_compliant_revenue numeric,
    impure_revenue_ratio numeric,
    debt_ratio numeric,
    cash_ratio numeric,
    sector text,
    industry text,
    raw_provider_payload jsonb,
    source text not null default 'eodhd',
    fetched_at timestamptz not null default now()
);

create index if not exists idx_financial_ratios_company_id on financial_ratios (company_id);

create table if not exists screening_results (
    id uuid primary key default gen_random_uuid(),
    company_id uuid not null references companies (id) on delete cascade,
    financial_ratios_id uuid not null references financial_ratios (id) on delete cascade,
    business_activity_status text not null check (business_activity_status in ('compliant', 'non_compliant', 'review')),
    debt_ratio_pass boolean not null,
    cash_ratio_pass boolean not null,
    verdict text not null check (verdict in ('halal', 'haram', 'questionable')),
    -- Reserved for V2 (no impure-revenue data source in V1).
    purification_pct numeric,
    flagged_reasons jsonb not null default '[]'::jsonb,
    screened_at timestamptz not null default now()
);

create index if not exists idx_screening_results_company_id_screened_at
    on screening_results (company_id, screened_at desc);
