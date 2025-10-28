from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .db import create_db_and_tables
from .seed import seed_db
from .routers import auth, members
from .routers import loans, payments, fines, profit
from .routers import dashboard, portal
from .routers import users

app = FastAPI(title="Malabo Microcrédito API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    create_db_and_tables()
    if settings.SEED_ON_STARTUP:
        seed_db()

@app.get("/")
async def root():
    return {"message": "API ok. Veja /health e /docs"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/ping")
async def ping():
    return "pong"

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(members.router, prefix="/members", tags=["members"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(loans.router, prefix="/loans", tags=["loans"])
app.include_router(payments.router, prefix="/payments", tags=["payments"])
app.include_router(fines.router, prefix="/fines", tags=["fines"])
app.include_router(profit.router, prefix="/profit-sharing", tags=["profit"]) 
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"]) 
app.include_router(portal.router, prefix="/portal", tags=["portal"]) 
