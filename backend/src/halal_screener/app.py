from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from halal_screener.api.routes import companies, health, screening
from halal_screener.database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    # No-op against Postgres (schema is applied via migrations/0001_init.sql);
    # creates tables for local SQLite dev where no migration has been run.
    create_db_and_tables()
    yield


app = FastAPI(title="Halal Screener API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(companies.router, prefix="/api", tags=["companies"])
app.include_router(screening.router, prefix="/api", tags=["screening"])
