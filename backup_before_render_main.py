from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routers.chat import router as chat_router

app = FastAPI(title="NECS Legal AI")


app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

app.include_router(chat_router)
