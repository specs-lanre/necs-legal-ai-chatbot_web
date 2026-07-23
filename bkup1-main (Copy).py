from fastapi import FastAPI
from sqlalchemy import text
from database import engine

from fastapi import  Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from google import genai
from dotenv import load_dotenv
import os


app = FastAPI()

templates = Jinja2Templates(directory="templates")

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)



@app.get("/")
def home():
    return {"message": "FastAPI running"}

@app.get("/test-db")
def test_database():

    try:
        with engine.connect() as connection:

            result = connection.execute(text("SELECT version();"))

            version = result.scalar()

            return {
                "status": "success",
                "database": version
            }

    except Exception as e:

        return {
            "status": "failed",
            "error": str(e)
        }

@app.get("/chat", response_class=HTMLResponse)
async def chat(request: Request):
    return templates.TemplateResponse(
        "chatbot.html",
        {"request": request}
    )
















































