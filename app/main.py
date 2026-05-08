from fastapi import FastAPI

from app.config import settings
from app.routes import briefings, health

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description=(
        "Executive briefing intelligence layer that scores operating signals, "
        "generates narrative summaries, and ranks next-step actions."
    ),
)

app.include_router(health.router)
app.include_router(briefings.router)

