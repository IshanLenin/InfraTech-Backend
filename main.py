from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from schemas.user_growth import UserAnalyticsResponse
from schemas.engagement import ConversionAnalyticsResponse
from schemas.economics import EconomicsAnalyticsResponse
from schemas.referrals import ReferralAnalyticsResponse
from schemas.operations import OperationsAnalyticsResponse
from routers import users, conversions, economics, referrals, operations
from database import get_db, engine, Base
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Cashback Analytics API",
    version="1.0.0",
    description="Internal dashboard backend for platform metrics"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#The routers are mounted here
app.include_router(users.router)
app.include_router(conversions.router)
app.include_router(economics.router)
app.include_router(referrals.router)
app.include_router(operations.router)

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "operational", "version": "1.0.0"}