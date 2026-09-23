"""
=================================================

Knowledge Builder

Prompt Builder

Builds the final prompt sent to the ChatBot
using:

1. System instructions
2. Retrieved knowledge
3. User question

Pipeline:

User Question
      ↓
Retriever
      ↓
Relevant Knowledge
      ↓
Prompt Builder
      ↓
Final Prompt
      ↓
ChatBot

Version: 1.0

=================================================
"""

from pathlib import Path

from config import Config
from logger import Logger


class PromptBuilder:

    def __init__(self):

        self.config = Config()

        self.logger = Logger()

        self.logger.info(
            "Prompt Builder initialized."
        )

        self.prompt_folder = Path(
            "prompts"
        )

        self.system_prompt_file = (
            self.prompt_folder
            / "system_prompt.txt"
        )

        self.system_prompt = (
            self.load_system_prompt()
        )

    # -------------------------------------------------
    # LOAD SYSTEM PROMPT
    # -------------------------------------------------

    def load_system_prompt(self):

        self.logger.info(
            "Loading system prompt..."
        )

        if not self.system_prompt_file.exists():

            self.logger.error(
                f"System prompt not found: "
                f"{self.system_prompt_file}"
            )

            return ""

        try:

            prompt = (
                self.system_prompt_file.read_text(
                    encoding="utf-8"
                )
            )

            prompt = prompt.strip()

            self.logger.info(
                "System prompt loaded."
            )

            return prompt

        except Exception as ex:

            self.logger.error(
                f"Unable to load system prompt: "
                f"{ex}"
            )

            return ""

    # -------------------------------------------------
    # FORMAT RETRIEVED KNOWLEDGE
    # -------------------------------------------------

    def format_knowledge(
        self,
        results
    ):

        if not results:

            return (
                "No relevant knowledge was "
                "retrieved from the knowledge base."
            )

        knowledge_sections = []

        for position, result in enumerate(
            results,
            start=1
        ):

            source = result.get(
                "source",
                "Unknown"
            )

            chunk = result.get(
                "chunk",
                "Unknown"
            )

            score = result.get(
                "score",
                0.0
            )

            text = result.get(
                "text",
                ""
            )

            section = (
                f"--- KNOWLEDGE CHUNK "
                f"{position} ---\n"
                f"Source: {source}\n"
                f"Chunk: {chunk}\n"
                f"Similarity: {score:.6f}\n\n"
                f"{text}"
            )

            knowledge_sections.append(
                section
            )

        return "\n\n".join(
            knowledge_sections
        )

    # -------------------------------------------------
    # BUILD PROMPT
    # -------------------------------------------------

    def build_prompt(
        self,
        question,
        results
    ):

        if not question or not question.strip():

            self.logger.error(
                "Cannot build prompt from "
                "an empty question."
            )

            return ""

        question = question.strip()

        knowledge = (
            self.format_knowledge(
                results
            )
        )

        prompt_parts = []

        if self.system_prompt:

            prompt_parts.append(
                "===== SYSTEM INSTRUCTIONS =====\n"
                + self.system_prompt
            )

        prompt_parts.append(
            "===== RETRIEVED KNOWLEDGE =====\n"
            + knowledge
        )

        prompt_parts.append(
            "===== USER QUESTION =====\n"
            + question
        )

        prompt_parts.append(
            "===== RESPONSE INSTRUCTIONS =====\n"
            "Answer the user's question using "
            "the retrieved knowledge above. "
            "Do not invent facts that are not "
            "supported by the available knowledge. "
            "If the retrieved knowledge does not "
            "contain enough information to answer "
            "the question, clearly state that the "
            "available knowledge does not provide "
            "enough information."
        )

        final_prompt = "\n\n".join(
            prompt_parts
        )

        self.logger.info(
            "Prompt built successfully."
        )

        return final_prompt

    # -------------------------------------------------
    # BUILD CHAT INPUT
    # -------------------------------------------------

    def build_chat_input(
        self,
        question,
        results
    ):

        prompt = self.build_prompt(
            question=question,
            results=results
        )

        if not prompt:

            return ""

        return prompt

    # -------------------------------------------------
    # DISPLAY PROMPT
    # -------------------------------------------------

    def display_prompt(
        self,
        prompt
    ):

        print()

        print("=" * 60)
        print("GENERATED PROMPT")
        print("=" * 60)

        print()

        print(prompt)

    # -------------------------------------------------
    # TEST PROMPT BUILDER
    # -------------------------------------------------

    def test_prompt(
        self,
        question,
        results
    ):

        print()

        print("=" * 60)
        print("PROMPT BUILDER TEST")
        print("=" * 60)

        print()

        print(
            "Question:",
            question
        )

        print(
            "Retrieved results:",
            len(results)
        )

        prompt = self.build_chat_input(
            question=question,
            results=results
        )

        self.display_prompt(
            prompt
        )

        return prompt


# =================================================
# MAIN TEST
# =================================================

if __name__ == "__main__":

    print()

    print("=" * 60)
    print("PROMPT BUILDER")
    print("=" * 60)

    builder = PromptBuilder()

    print()

    print(
        "Prompt folder:",
        builder.prompt_folder
    )

    print(
        "System prompt:",
        builder.system_prompt_file
    )

    print()

    print("=" * 60)
    print("SYSTEM PROMPT TEST")
    print("=" * 60)

    if builder.system_prompt:

        print()
        print(
            builder.system_prompt[:1000]
        )

        if len(
            builder.system_prompt
        ) > 1000:

            print()
            print(
                "... [truncated for test]"
            )

    else:

        print(
            "WARNING: System prompt is empty."
        )

    # -------------------------------------------------
    # SAMPLE RETRIEVED RESULTS
    # -------------------------------------------------

    sample_results = [

        {
            "id": 1,
            "source": (
                "knowledge_source/"
                "services/services.md"
            ),
            "chunk": 0,
            "score": 0.833248,
            "text": (
                "# INTELLECTUAL PROPERTY "
                "LEGAL SERVICES KNOWLEDGE ARTICLE\n\n"
                "NECS Legal provides intellectual "
                "property legal services including "
                "Trademarks, Patents, Industrial "
                "Designs, Anti-Counterfeiting, "
                "IP Litigation, Domain Names, "
                "Commercial IP, and Strategic "
                "IP Advisory."
            )
        },

        {
            "id": 8,
            "source": (
                "knowledge_source/"
                "services/services.md"
            ),
            "chunk": 7,
            "score": 0.792041,
            "text": (
                "NECS Legal specializes in "
                "Patents, Trademarks, Industrial "
                "Designs, Anti-Counterfeiting, "
                "IP Litigation & Disputes, "
                "Domain Names, Commercial IP, "
                "and IP Advisory."
            )
        }
    ]

    question = (
        "What intellectual property services "
        "does NECS Legal provide?"
    )

    builder.test_prompt(
        question=question,
        results=sample_results
    )
