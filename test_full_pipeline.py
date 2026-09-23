from retriever import Retriever
from prompt_builder import PromptBuilder
from chatbot import ChatBot


# ==================================================
# TEST QUESTION
# ==================================================

question = (
    "What intellectual property services "
    "does NECS Legal provide?"
)


# ==================================================
# HEADER
# ==================================================

print()
print("=" * 70)
print("FULL KNOWLEDGE PIPELINE TEST")
print("=" * 70)

print()
print("Question:")
print(question)


# ==================================================
# STEP 1 — RETRIEVER
# ==================================================

print()
print("=" * 70)
print("STEP 1 — RETRIEVER")
print("=" * 70)

retriever = Retriever()

results = retriever.search(
    question,
    top_k=3
)

print()
print(
    f"Retrieved {len(results)} knowledge chunks."
)

retriever.display_results(
    results
)


# ==================================================
# STEP 2 — PROMPT BUILDER
# ==================================================

print()
print("=" * 70)
print("STEP 2 — PROMPT BUILDER")
print("=" * 70)

builder = PromptBuilder()

prompt = builder.build_prompt(
    question=question,
    results=results
)

if not prompt:

    print()
    print("ERROR: Prompt Builder returned an empty prompt.")

    raise SystemExit(1)


print()
print("Final prompt successfully generated.")

print()
print("-" * 70)
print("FINAL PROMPT")
print("-" * 70)

print(prompt)


# ==================================================
# STEP 3 — CHATBOT
# ==================================================

print()
print("=" * 70)
print("STEP 3 — CHATBOT")
print("=" * 70)

chatbot = ChatBot()

answer = chatbot.generate_response(
    prompt
)

if not answer:

    print()
    print("ERROR: ChatBot returned an empty answer.")

    raise SystemExit(1)


# ==================================================
# STEP 4 — FINAL ANSWER
# ==================================================

print()
print("=" * 70)
print("FINAL ANSWER")
print("=" * 70)

print()
print(answer)


# ==================================================
# TEST COMPLETE
# ==================================================

print()
print("=" * 70)
print("FULL PIPELINE TEST COMPLETE")
print("=" * 70)

print()
print("Pipeline:")
print(
    "Question → Retriever → Prompt Builder "
    "→ ChatBot → Gemini → Answer"
)

print()
print("STATUS: SUCCESS")
print()
