# Migrations

V1 uses hand-written raw SQL migration files against Supabase, not Alembic —
the schema is small (3 tables) and stable for V1, so autogenerate/diffing
overhead isn't justified yet (revisit for V2 if the schema grows).

Each `NNNN_description.sql` file must be kept in sync by hand with the
SQLModel classes in `backend/src/halal_screener/models.py`.

Apply a migration against your Supabase project:

```sh
psql "$SUPABASE_DB_URL" -f migrations/0001_init.sql
```

Local dev against SQLite (the default `DATABASE_URL`) doesn't need this —
`create_db_and_tables()` (called on app startup) creates tables directly
from the SQLModel classes.
