from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.utils.logger import logger
from app import auth, claims


logger.info("Starting the Claims Portal API application")


app = FastAPI(title='Jubilee Portal API')

Instrumentator().instrument(app).expose(app, include_in_schema=False)

app.include_router(auth.router, tags=["Auth"], prefix="/api/auth")
app.include_router(claims.router, tags=["Claims"], prefix="/api/claims")
