from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.contacts.router import router as contacts_router
from app.modules.calls.router import router as calls_router

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


@app.get("/health")
def health_check():
    return {"status": "ok"}