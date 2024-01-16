from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from fastapi import APIRouter

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import uvicorn

# alembic revision --autogenerate -m 'Init'
# alembic upgrade head
# docker-compose up -d
# docker exec -it dcb9d sh
# uvicorn main:app --host localhost --port 8000 --reload

from src.routing.comments import router as comments_router
from src.routing import auth
from src.routing import publications
from src.routing import tags
from src.database.db import get_db

# from src.services.auth import auth_service


app = FastAPI()

origins = [
    "http://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.on_event('startup')
# async def startup():
#     await FastAPILimiter.init(auth_service.r)

app.include_router(comments_router, prefix='/api')
app.include_router(auth.router, prefix="/api")
app.include_router(publications.router, prefix="/api")
app.include_router(tags.router, prefix="/api")


@app.get('/', dependencies=[])  # Depends(RateLimiter(times=2, seconds=5))
def read_root():
    return {'message': 'It works!'}


@app.get("/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    The healthchecker function is a simple function that checks the health of the database.
    It does this by making a request to the database and checking if it returns any results.
    If it doesn't, then we know something is wrong with our connection.

    :param db: AsyncSession: Pass the database session to the function
    :return: A dictionary with a message
    :doc-author: Trelent
    """
    try:
        # Make request
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")


if __name__ == '__main__':
    uvicorn.run('main:app', port=8000, reload=True)
