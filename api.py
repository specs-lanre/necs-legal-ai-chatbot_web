from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from retriever import Retriever
from prompt_builder import PromptBuilder
from chatbot import ChatBot


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="NECS Legal AI Chatbot API",
    description="RAG-based AI chatbot for NECS Legal",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# REQUEST / RESPONSE MODELS
# ============================================================

class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    question: str
    answer: str


# ============================================================
# INITIALIZE RAG COMPONENTS
# ============================================================

print("=" * 70)
print("INITIALIZING NECS LEGAL RAG API")
print("=" * 70)

retriever = Retriever()
prompt_builder = PromptBuilder()
chatbot = ChatBot()

print()
print("All RAG components initialized successfully.")
print("=" * 70)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "NECS Legal AI Chatbot API"
    }


# ============================================================
# CHAT ENDPOINT
# ============================================================

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:

        # ----------------------------------------------------
        # STEP 1 — RETRIEVE KNOWLEDGE
        # ----------------------------------------------------

        results = retriever.search(
            question,
            top_k=3
        )

        # ----------------------------------------------------
        # STEP 2 — BUILD FINAL PROMPT
        # ----------------------------------------------------

        prompt = prompt_builder.build_prompt(
            question,
            results
        )

        # ----------------------------------------------------
        # STEP 3 — SEND PROMPT TO GEMINI
        # ----------------------------------------------------

        answer = chatbot.generate_response(prompt)

        # ----------------------------------------------------
        # STEP 4 — RETURN RESPONSE
        # ----------------------------------------------------

        return ChatResponse(
            question=question,
            answer=answer
        )

    except Exception as e:

        print()
        print("=" * 70)
        print("CHAT ERROR")
        print("=" * 70)
        print(str(e))
        print("=" * 70)

        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing the question."
        )
