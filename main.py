from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import users, conversions, economics, referrals, operations
from database import engine
import models
from fastapi.responses import RedirectResponse

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

@app.get("/", include_in_schema=False)
def root_redirect():
    return RedirectResponse(url="/docs")