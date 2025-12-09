import os

os.environ["TESTING"] = "0"  # normal run
from contextlib import asynccontextmanager
from logging import getLogger

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import Base, engine
from app.middleware.error_middleware import error_handler
from app.models.errors.app_error import AppError
from app.routes import auth_route, customer_route, products_route, user_route, orders_route

logger = getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        logger.info("Creating database tables...")
        await conn.run_sync(Base.metadata.create_all)
    yield 
    await engine.dispose()

app = FastAPI(title="EZShop", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # should allow all origins for dev purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# register routers
app.include_router(auth_route.router)
app.include_router(user_route.router)
app.include_router(customer_route.router)
app.include_router(products_route.router)
app.include_router(orders_route.router)

app.add_exception_handler(AppError, error_handler)
app.add_exception_handler(Exception, error_handler)


# simple root
@app.get("/")
def read_root():
    return {"message": "FastAPI MVC Demo"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)