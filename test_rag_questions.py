from retriever import Retriever
from prompt_builder import PromptBuilder
from chatbot import ChatBot


# ============================================================
# RAG PIPELINE TEST QUESTIONS
# ============================================================

TEST_CASES = [

    {
        "name": "DIRECT KNOWLEDGE",
        "question": (
            "What intellectual property services does "
            "NECS Legal provide?"
        ),
        "purpose": (
            "The knowledge base directly contains "
            "the answer."
        )
    },

    {
        "name": "SPECIFIC KNOWLEDGE",
        "question": (
            "How long does a trademark registration "
            "last in Nigeria according to the "
            "NECS Legal knowledge base?"
        ),
        "purpose": (
            "The Retriever should locate the specific "
            "trademark information."
        )
    },

    {
        "name": "INSUFFICIENT KNOWLEDGE",
        "question": (
            "What is the exact fee that NECS Legal "
            "charges for registering a trademark?"
        ),
        "purpose": (
            "The system should not invent a price if "
            "the knowledge base does not provide one."
        )
    },

    {
        "name": "UNRELATED QUESTION",
        "question": (
            "What is the current exchange rate between "
            "the Nigerian naira and the US dollar?"
        ),
        "purpose": (
            "The system should not manufacture an NECS "
            "Legal answer to an unrelated question."
        )
    }
]


# ============================================================
# HEADER
# ============================================================

print()
print("=" * 80)
print("RAG PIPELINE — MULTI-QUESTION TEST")
print("=" * 80)

print()
print(
    "Pipeline:"
)
print(
    "Question → Retriever → Prompt Builder → "
    "ChatBot → Gemini → Answer"
)


# ============================================================
# INITIALIZE COMPONENTS ONCE
# ============================================================

print()
print("=" * 80)
print("INITIALIZING RAG COMPONENTS")
print("=" * 80)

print()
print("Initializing Retriever...")

retriever = Retriever()

print()
print("Initializing Prompt Builder...")

builder = PromptBuilder()

print()
print("Initializing ChatBot...")

chatbot = ChatBot()

print()
print("All components initialized successfully.")


# ============================================================
# RUN TEST CASES
# ============================================================

for number, test_case in enumerate(
    TEST_CASES,
    start=1
):

    name = test_case["name"]
    question = test_case["question"]
    purpose = test_case["purpose"]

    print()
    print()
    print("#" * 80)
    print(
        f"TEST {number} — {name}"
    )
    print("#" * 80)

    print()
    print("Question:")
    print(question)

    print()
    print("Purpose:")
    print(purpose)

    # --------------------------------------------------------
    # RETRIEVAL
    # --------------------------------------------------------

    print()
    print("-" * 80)
    print("RETRIEVAL")
    print("-" * 80)

    results = retriever.search(
        question,
        top_k=3
    )

    print()
    print(
        f"Retrieved {len(results)} result(s)."
    )

    if results:

        for position, result in enumerate(
            results,
            start=1
        ):

            print()
            print(
                f"Result {position}:"
            )

            print(
                "  ID:",
                result.get("id")
            )

            print(
                "  Source:",
                result.get("source")
            )

            print(
                "  Chunk:",
                result.get("chunk")
            )

            print(
                "  Score:",
                round(
                    result.get("score", 0.0),
                    6
                )
            )

    else:

        print(
            "No knowledge chunks retrieved."
        )

    # --------------------------------------------------------
    # PROMPT BUILDING
    # --------------------------------------------------------

    print()
    print("-" * 80)
    print("PROMPT BUILDING")
    print("-" * 80)

    prompt = builder.build_prompt(
        question=question,
        results=results
    )

    if not prompt:

        print()
        print(
            "ERROR: Prompt Builder returned "
            "an empty prompt."
        )

        continue

    print()
    print(
        "Prompt successfully generated."
    )

    # --------------------------------------------------------
    # GEMINI
    # --------------------------------------------------------

    print()
    print("-" * 80)
    print("CHATBOT / GEMINI")
    print("-" * 80)

    try:

        answer = chatbot.generate_response(
            prompt
        )

    except Exception as ex:

        print()
        print(
            "ERROR: ChatBot failed:"
        )

        print(ex)

        continue

    # --------------------------------------------------------
    # ANSWER
    # --------------------------------------------------------

    print()
    print("-" * 80)
    print("FINAL ANSWER")
    print("-" * 80)

    print()
    print(answer)

    # --------------------------------------------------------
    # TEST END
    # --------------------------------------------------------

    print()
    print(
        f"TEST {number} COMPLETE"
    )


# ============================================================
# FINAL STATUS
# ============================================================

print()
print()
print("=" * 80)
print("RAG MULTI-QUESTION TEST COMPLETE")
print("=" * 80)

print()
print(
    "All four test cases have been processed."
)

print()
print(
    "Review the retrieval scores and final answers "
    "above to evaluate grounding behavior."
)

print()
print("=" * 80)
