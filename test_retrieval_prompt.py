from retriever import Retriever
from prompt_builder import PromptBuilder


# --------------------------------------------------
# TEST QUESTION
# --------------------------------------------------

question = "What intellectual property services does NECS Legal provide?"


# --------------------------------------------------
# INITIALIZE RETRIEVER
# --------------------------------------------------

print("=" * 70)
print("INITIALIZING RETRIEVER")
print("=" * 70)

retriever = Retriever()


# --------------------------------------------------
# RETRIEVE KNOWLEDGE
# --------------------------------------------------

print()
print("=" * 70)
print("RETRIEVING KNOWLEDGE")
print("=" * 70)

results = retriever.search(
    question,
    top_k=3
)


# --------------------------------------------------
# SHOW RETRIEVAL RESULTS
# --------------------------------------------------

print()
print("=" * 70)
print("RETRIEVED RESULTS")
print("=" * 70)

retriever.display_results(results)


# --------------------------------------------------
# INITIALIZE PROMPT BUILDER
# --------------------------------------------------

print()
print("=" * 70)
print("INITIALIZING PROMPT BUILDER")
print("=" * 70)

builder = PromptBuilder()


# --------------------------------------------------
# BUILD FINAL PROMPT
# --------------------------------------------------

print()
print("=" * 70)
print("BUILDING FINAL PROMPT")
print("=" * 70)

prompt = builder.build_prompt(
    question,
    results
)


# --------------------------------------------------
# DISPLAY FINAL PROMPT
# --------------------------------------------------

print()
print("=" * 70)
print("FINAL PROMPT")
print("=" * 70)

print(prompt)


# --------------------------------------------------
# TEST COMPLETE
# --------------------------------------------------

print()
print("=" * 70)
print("INTEGRATION TEST COMPLETE")
print("=" * 70)
