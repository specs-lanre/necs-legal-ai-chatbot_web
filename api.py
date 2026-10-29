
import os
import re
import time

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from retriever import Retriever
from prompt_builder import PromptBuilder
from chatbot import ChatBot


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

app = FastAPI(
    title="NECS Legal AI Chatbot API",
    description="RAG-based AI chatbot for NECS Legal",
    version="1.1.7",
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
# REQUEST AND RESPONSE MODELS
# ============================================================

class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    question: str
    answer: str


# ============================================================
# RESPONSE MODE
# ============================================================

# "direct" uses deterministic handlers and retrieval.
# "gemini" uses the existing prompt builder and ChatBot.
CHAT_RESPONSE_MODE = os.getenv(
    "CHAT_RESPONSE_MODE",
    "direct",
).strip().lower()


# ============================================================
# RETRIEVAL THRESHOLDS
# ============================================================

MIN_SIMILARITY_SCORE = 0.75
MIN_PROCESS_SCORE = 0.60
MIN_FAQ_SCORE = 0.60
MIN_DIRECT_SCORE = 0.60


# ============================================================
# CONTACT DETAILS AND STANDARD ANSWERS
# ============================================================

CONTACT_DETAILS = (
    "Telephone/WhatsApp: +2348107251119\n"
    "Email: info@necs-legal.com"
)

ESCALATION_ANSWER = (
    "I couldn't confirm that information from the available "
    "NECS Legal knowledge base. Please contact the firm directly.\n\n"
    + CONTACT_DETAILS
)

LEGAL_ADVICE_ANSWER = (
    "I can provide general information about NECS Legal's services, "
    "but I cannot assess your individual legal situation or recommend "
    "a legal course of action. Please consult a lawyer at NECS Legal "
    "for advice specific to your circumstances.\n\n"
    + CONTACT_DETAILS
)

GREETING_ANSWER = (
    "Hello! I'm Sujo, the AI Legal Assistant for NECS Legal.\n\n"
    "I can help you learn about our legal services, intellectual "
    "property practice areas, and general legal information.\n\n"
    "How may I assist you today?"
)

# This answer is returned directly for general services questions.
# It does not depend on retrieval scores or a Markdown heading.
SERVICES_ANSWER = (
    "NECS Legal provides intellectual property (IP) legal "
    "services in Nigeria and across African markets, including:\n\n"
    "- Trademarks\n"
    "- Patents\n"
    "- Industrial designs\n"
    "- Anti-counterfeiting\n"
    "- IP litigation and dispute resolution\n"
    "- Domain names\n"
    "- Commercial IP and licensing\n"
    "- Strategic IP advisory\n\n"
    "For assistance with a specific matter, please contact "
    "NECS Legal:\n"
    + CONTACT_DETAILS
)


# ============================================================
# TEXT PROCESSING
# ============================================================

STOP_WORDS = {
    "a", "an", "the", "is", "are", "do", "does", "did",
    "can", "could", "would", "will", "what", "which", "how",
    "where", "when", "why", "who", "whom", "i", "we", "you",
    "they", "it", "my", "our", "your", "their", "me", "us",
    "to", "for", "of", "in", "on", "at", "by", "with",
    "and", "or", "about", "please", "tell", "explain",
    "provide", "give", "necs", "legal", "firm", "company",
}


def tokenize(text: str) -> set:
    """Return useful words for simple evidence matching."""
    words = re.findall(r"[a-z0-9]+", text.lower())

    return {
        word
        for word in words
        if word not in STOP_WORDS and len(word) > 1
    }


# ============================================================
# QUESTION CLASSIFICATION
# ============================================================

def is_greeting(question: str) -> bool:
    """Recognize standalone greetings."""
    text = question.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()

    greetings = {
        "hello",
        "hi",
        "hey",
        "howdy",
        "greetings",
        "good morning",
        "good afternoon",
        "good evening",
        "hello sujo",
        "hi sujo",
        "hey sujo",
        "good morning sujo",
        "good afternoon sujo",
        "good evening sujo",
    }

    if text in greetings:
        return True

    words = text.split()

    if len(words) <= 2 and words:
        if words[0] in {"hello", "hi", "hey"}:
            return len(words) == 1 or words[1] in {
                "sujo",
                "there",
            }

    return False


def requires_personal_legal_advice(question: str) -> bool:
    """Detect common requests for advice about an individual situation."""
    text = question.lower()

    patterns = [
        r"\bwhat should i do\b",
        r"\bwhat can i do\b",
        r"\bshould i sue\b",
        r"\bcan i sue\b",
        r"\bshould i file\b",
        r"\bmy case\b",
        r"\bin my case\b",
        r"\bmy situation\b",
        r"\bmy trademark\b",
        r"\bmy patent\b",
        r"\bmy company\b",
        r"\bi received (a|an|the)\b",
        r"\bi have been sued\b",
        r"\bi was sued\b",
        r"\bi am being sued\b",
        r"\bi am facing\b",
        r"\bmy opponent\b",
        r"\bmy lawyer\b",
        r"\bmy business partner\b",
        r"\bwhat legal action should\b",
        r"\bwhat are my legal options\b",
    ]

    return any(
        re.search(pattern, text)
        for pattern in patterns
    )


def is_trademark_process_question(question: str) -> bool:
    """Identify questions asking about trademark registration."""
    text = question.lower()

    trademark_terms = [
        "trademark",
        "trade mark",
        "trade-mark",
    ]

    process_terms = [
        "process",
        "procedure",
        "steps",
        "how to",
        "how do i",
        "how can i",
        "register",
        "registration",
        "apply",
        "application",
        "filing",
        "file a",
    ]

    mentions_trademark = any(
        term in text for term in trademark_terms
    )

    asks_about_process = any(
        term in text for term in process_terms
    )

    return mentions_trademark and asks_about_process


def is_services_question(question: str) -> bool:
    """Recognize general questions about NECS Legal's services."""
    text = question.lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    service_phrases = [
        "services",
        "practice areas",
        "areas of law",
        "legal services",
        "what do you do",
        "what does necs do",
        "what does the firm do",
        "what legal work",
        "what do you specialize in",
        "what do you specialise in",
        "what are you specialized in",
        "what are you specialised in",
        "what can your firm help with",
        "what kind of law",
    ]

    if any(phrase in text for phrase in service_phrases):
        return True

    # Recognize common variations such as:
    # "What are your services?"
    # "Tell me about your services."
    # "List the services offered by NECS Legal."
    service_patterns = [
        r"\bwhat are (your|the firm's|necs legal's) services\b",
        r"\blist (your|the firm's|necs legal's) services\b",
        r"\btell me about (your|the firm's|necs legal's) services\b",
        r"\bservices (offered|provided) by\b",
    ]

    return any(
        re.search(pattern, text)
        for pattern in service_patterns
    )


def is_contact_question(question: str) -> bool:
    """Identify questions asking for contact details."""
    text = question.lower()

    contact_terms = [
        "contact",
        "phone number",
        "telephone",
        "whatsapp",
        "email address",
        "email",
        "reach necs",
        "reach the firm",
        "contact details",
        "contact information",
        "phone",
        "call the firm",
        "how do i reach",
        "how can i reach",
    ]

    return any(
        term in text for term in contact_terms
    )


# ============================================================
# CONTACT ANSWER
# ============================================================

def contact_answer() -> str:
    """Return the configured NECS Legal contact details."""
    return (
        "You can contact NECS Legal using the following details:\n\n"
        + CONTACT_DETAILS
    )


# ============================================================
# FAQ EXTRACTION AND MATCHING
# ============================================================

def extract_faq_answers(results: list) -> list:
    """
    Extract FAQ question-and-answer pairs from Markdown chunks.
    Supports numbered and unnumbered bold FAQ questions.
    """
    candidates = []

    faq_pattern = re.compile(
        r"(?:^|\n)\s*(?:\d+\.\s*)?\*\*(.+?)\*\*\s*"
        r"(.*?)"
        r"(?=\n\s*(?:\d+\.\s*)?\*\*|\n#{1,4}\s|\Z)",
        re.DOTALL,
    )

    for result in results:
        chunk_text = (
            result.get("text")
            or result.get("content")
            or result.get("chunk")
            or ""
        )

        try:
            chunk_score = float(result.get("score", 0))
        except (TypeError, ValueError):
            chunk_score = 0.0

        for match in faq_pattern.finditer(chunk_text):
            faq_question = match.group(1).strip()
            faq_answer = match.group(2).strip()

            faq_answer = re.sub(r"\*\*", "", faq_answer)
            faq_answer = re.sub(
                r"\s+",
                " ",
                faq_answer,
            ).strip()

            if (
                faq_question
                and faq_answer
                and "?" in faq_question
            ):
                candidates.append({
                    "question": faq_question,
                    "answer": faq_answer,
                    "retrieval_score": chunk_score,
                })

    return candidates


def find_matching_faq(question: str, results: list):
    """Find an FAQ with meaningful question-word overlap."""
    query_terms = tokenize(question)

    if not query_terms:
        return None

    best_match = None
    best_score = 0.0

    for candidate in extract_faq_answers(results):
        faq_question = candidate["question"].lower()

        if is_trademark_process_question(question):
            continue

        faq_terms = tokenize(faq_question)

        if not faq_terms:
            continue

        overlap = query_terms.intersection(faq_terms)
        overlap_score = len(overlap) / len(query_terms)

        if len(overlap) < 2 or overlap_score < 0.40:
            continue

        if candidate["retrieval_score"] < MIN_FAQ_SCORE:
            continue

        if overlap_score > best_score:
            best_score = overlap_score
            best_match = candidate

    if best_match:
        return best_match["answer"]

    return None


# ============================================================
# SERVICES SUMMARY EXTRACTION
# ============================================================

def extract_services_summary(results: list):
    """
    Optional retrieval-based services extraction.

    General services questions are answered by SERVICES_ANSWER
    before retrieval, so this function is not required for them.
    """
    for result in results:
        try:
            score = float(result.get("score", 0))
        except (TypeError, ValueError):
            continue

        if score < MIN_SIMILARITY_SCORE:
            continue

        text = (
            result.get("text")
            or result.get("content")
            or result.get("chunk")
            or ""
        )

        match = re.search(
            r"## SUMMARY\s*(.*?)(?=\n## |\Z)",
            text,
            re.DOTALL | re.IGNORECASE,
        )

        if not match:
            continue

        summary = match.group(1).strip()
        summary = re.sub(r"\*\*", "", summary)
        summary = re.sub(r"\s+", " ", summary).strip()

        if len(summary) >= 80:
            return SERVICES_ANSWER

    return None


# ============================================================
# TRADEMARK REGISTRATION PROCESS EXTRACTION
# ============================================================

def extract_process_answer(results: list):
    """Extract trademark-registration steps from retrieved knowledge."""
    process_candidates = []

    for result in results:
        try:
            score = float(result.get("score", 0))
        except (TypeError, ValueError):
            continue

        if score < MIN_PROCESS_SCORE:
            continue

        content = (
            result.get("text")
            or result.get("content")
            or result.get("chunk")
            or ""
        )

        if not content:
            continue

        section_match = re.search(
            r"##\s*STEP-BY-STEP PROCESS\s*\n"
            r"(.*?)(?=\n#{1,2}\s|\Z)",
            content,
            re.IGNORECASE | re.DOTALL,
        )

        if section_match:
            process_text = section_match.group(1).strip()
        else:
            step_match = re.search(
                r"(?ms)^\s*\d+\.\s*\*\*"
                r"(?:Client Intake|Availability Search|"
                r"Application Preparation|Prosecution|"
                r"Grant\s*(?:&|and)\s*Registration)"
                r".*?"
                r"(?=^\s*#{1,4}\s|\Z)",
                content,
                re.IGNORECASE,
            )

            if not step_match:
                continue

            process_text = step_match.group(0).strip()

        process_text = re.sub(
            r"\n{3,}",
            "\n\n",
            process_text,
        )

        text_lower = process_text.lower()

        has_process_content = (
            len(process_text) >= 100
            and (
                "application" in text_lower
                or "availability search" in text_lower
                or "client intake" in text_lower
            )
            and (
                "filing" in text_lower
                or "registration" in text_lower
                or "registry" in text_lower
            )
        )

        if has_process_content:
            process_candidates.append({
                "score": score,
                "text": process_text,
            })

    if not process_candidates:
        print(
            "PROCESS EXTRACTION: No qualifying process chunk found."
        )
        return None

    process_candidates.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    best_candidate = process_candidates[0]

    print(
        "PROCESS EXTRACTION: Matching process found "
        f"(score={best_candidate['score']:.4f})."
    )

    return best_candidate["text"]


# ============================================================
# DIRECT ANSWER ROUTER
# ============================================================

def direct_answer(question: str, results: list) -> str:
    """
    Produce deterministic answers using configured handlers
    and retrieved knowledge.
    """

    if is_greeting(question):
        return GREETING_ANSWER

    if requires_personal_legal_advice(question):
        return LEGAL_ADVICE_ANSWER

    if is_contact_question(question):
        return contact_answer()

    # General services questions do not depend on retrieval.
    if is_services_question(question):
        return SERVICES_ANSWER

    if not results:
        return ESCALATION_ANSWER

    valid_scores = []

    for result in results:
        try:
            valid_scores.append(float(result.get("score", 0)))
        except (TypeError, ValueError):
            continue

    if not valid_scores:
        return ESCALATION_ANSWER

    top_score = max(valid_scores)

    print(
        f"Direct-answer top similarity score: {top_score:.4f}"
    )

    if top_score < MIN_DIRECT_SCORE:
        return ESCALATION_ANSWER

    # Handle trademark-registration questions before FAQs.
    if is_trademark_process_question(question):
        process_answer = extract_process_answer(results)

        if process_answer:
            return (
                "The trademark-registration process described in "
                "the available NECS Legal knowledge base is:\n\n"
                + process_answer
                + "\n\nFor assistance with your specific application, "
                "please contact NECS Legal:\n"
                + CONTACT_DETAILS
            )

        print(
            "PROCESS EXTRACTION: Relevant process could not be "
            "extracted from the retrieved results."
        )
        return ESCALATION_ANSWER

    faq_answer = find_matching_faq(question, results)

    if faq_answer:
        return faq_answer + "\n\n" + CONTACT_DETAILS

    return ESCALATION_ANSWER


# ============================================================
# INITIALIZE RAG COMPONENTS
# ============================================================

print("=" * 70)
print("INITIALIZING NECS LEGAL RAG API")
print("=" * 70)

retriever = Retriever()
prompt_builder = PromptBuilder()
chatbot = ChatBot()

print(f"Response mode: {CHAT_RESPONSE_MODE}")

if CHAT_RESPONSE_MODE not in {"direct", "gemini"}:
    raise ValueError(
        "CHAT_RESPONSE_MODE must be 'direct' or 'gemini'."
    )

print("All RAG components initialized successfully.")
print("=" * 70)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "NECS Legal AI Chatbot API",
        "response_mode": CHAT_RESPONSE_MODE,
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
            detail="Question cannot be empty.",
        )

    start_time = time.perf_counter()

    try:
        # ----------------------------------------------------
        # FAST PATH 1: GREETINGS
        # ----------------------------------------------------
        if is_greeting(question):
            answer = GREETING_ANSWER

            print(
                "GREETING RESPONSE: "
                f"{time.perf_counter() - start_time:.4f} seconds."
            )

            return ChatResponse(
                question=question,
                answer=answer,
            )

        # ----------------------------------------------------
        # FAST PATH 2: PERSONAL LEGAL ADVICE SAFEGUARD
        # ----------------------------------------------------
        if requires_personal_legal_advice(question):
            answer = LEGAL_ADVICE_ANSWER

            print(
                "LEGAL SAFEGUARD RESPONSE: "
                f"{time.perf_counter() - start_time:.4f} seconds."
            )

            return ChatResponse(
                question=question,
                answer=answer,
            )

        # ----------------------------------------------------
        # FAST PATH 3: CONTACT DETAILS
        # ----------------------------------------------------
        if (
            CHAT_RESPONSE_MODE == "direct"
            and is_contact_question(question)
        ):
            answer = contact_answer()

            print(
                "CONTACT RESPONSE: "
                f"{time.perf_counter() - start_time:.4f} seconds."
            )

            return ChatResponse(
                question=question,
                answer=answer,
            )

        # ----------------------------------------------------
        # FAST PATH 4: GENERAL SERVICES QUESTIONS
        # ----------------------------------------------------
        # This runs before retrieval, so a general services
        # question cannot fail because of a similarity threshold.
        if (
            CHAT_RESPONSE_MODE == "direct"
            and is_services_question(question)
        ):
            answer = SERVICES_ANSWER

            print(
                "SERVICES RESPONSE: "
                f"{time.perf_counter() - start_time:.4f} seconds."
            )

            return ChatResponse(
                question=question,
                answer=answer,
            )

        # ----------------------------------------------------
        # NORMAL RAG PIPELINE
        # ----------------------------------------------------
        print("\nSTEP 1: RETRIEVING KNOWLEDGE...")

        results = retriever.search(
            question,
            top_k=13,
        )

        if not results:
            print(
                "RETRIEVAL FAILED: No knowledge results returned."
            )

            raise HTTPException(
                status_code=503,
                detail=(
                    "The knowledge retrieval service is temporarily "
                    "unavailable. Please try again shortly."
                ),
            )

        print(
            f"RETRIEVAL SUCCESS: {len(results)} result(s) returned."
        )

        if CHAT_RESPONSE_MODE == "direct":
            print("STEP 2: PRODUCING DIRECT ANSWER...")

            answer = direct_answer(
                question,
                results,
            )

        else:
            print("STEP 2: BUILDING PROMPT...")

            prompt = prompt_builder.build_prompt(
                question,
                results,
            )

            if not prompt or not prompt.strip():
                raise HTTPException(
                    status_code=500,
                    detail="Unable to prepare the chatbot request.",
                )

            print("STEP 3: GENERATING RESPONSE WITH GEMINI...")

            answer = chatbot.generate_response(prompt)

        if not answer or not answer.strip():
            raise HTTPException(
                status_code=502,
                detail="The chatbot returned an empty response.",
            )

        elapsed = time.perf_counter() - start_time

        print(
            f"RESPONSE COMPLETED IN {elapsed:.4f} SECONDS."
        )

        return ChatResponse(
            question=question,
            answer=answer,
        )

    except HTTPException:
        raise

    except Exception as e:
        print("=" * 70)
        print("CHAT ERROR")
        print("=" * 70)
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {e}")
        print("=" * 70)

        raise HTTPException(
            status_code=500,
            detail=(
                "An error occurred while processing the question."
            ),
        )
