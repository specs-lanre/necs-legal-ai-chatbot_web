from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from routers.chat import router as chat_router


# -------------------------------------------------
# FastAPI Application
# -------------------------------------------------

app = FastAPI(
    title="NECS Legal AI"
)


# -------------------------------------------------
# CORS Configuration
# -------------------------------------------------

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://necs-legal-ai-chatbot-webfrontend.onrender.com",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# -------------------------------------------------
# Health Check
# -------------------------------------------------

@app.get("/")
def root():

    return {
        "status": "online",
        "service": "NECS Legal AI"
    }


# -------------------------------------------------
# Static Files
# -------------------------------------------------

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# -------------------------------------------------
# Chat Router
# -------------------------------------------------

app.include_router(
    chat_router
)
