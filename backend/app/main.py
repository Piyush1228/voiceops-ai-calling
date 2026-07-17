from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.contacts.router import router as contacts_router
from app.modules.calls.router import router as calls_router
from app.modules.calls.webhooks import router as twilio_webhooks_router
from app.modules.calls.stream import router as twilio_stream_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.analytics.router import router as analytics_router
from app.modules.admin.router import router as admin_router

app = FastAPI(
    title=settings.app_name,
    description="AI Voice Calling Platform",
    version="0.1.0",
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(contacts_router)
app.include_router(calls_router)
app.include_router(twilio_webhooks_router)
app.include_router(twilio_stream_router)
app.include_router(dashboard_router)
app.include_router(analytics_router)
app.include_router(admin_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}