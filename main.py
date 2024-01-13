from fastapi import FastAPI

from src.routing import publications

app = FastAPI()

app.include_router(publications.router, prefix="/api")


@app.get("/")
def index():
    return {"message": "Address Book Application"}
