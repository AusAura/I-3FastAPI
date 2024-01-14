from fastapi import FastAPI, Depends

from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request

from fastapi import APIRouter
# from src.services.auth import auth_service

import uvicorn

from src.routing.comments import router as comments_router


# alembic revision --autogenerate -m 'Init'
# alembic upgrade head

# docker-compose up -d
# docker exec -it dcb9d sh

# uvicorn main:app --host localhost --port 8000 --reload


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

@app.get('/', dependencies=[]) # Depends(RateLimiter(times=2, seconds=5))
def read_root():
    return {'message': 'It works!'}

if __name__ == '__main__':
    uvicorn.run('main:app', port=8000, reload=True)