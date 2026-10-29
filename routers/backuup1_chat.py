
from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from schemas.chat import ChatRequest
from schemas.chat import ChatResponse

from services.chat_service import process_chat

router = APIRouter()

templates = Jinja2Templates(directory="templates")


# -------------------------------------------------
# Display Chat Page
# -------------------------------------------------

@router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):

	return templates.TemplateResponse(
    request=request,
    name="chatbot.html"
	)


# -------------------------------------------------
# Chat API
# -------------------------------------------------

@router.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):

    reply = process_chat(request.message)

    return ChatResponse(reply=reply)
