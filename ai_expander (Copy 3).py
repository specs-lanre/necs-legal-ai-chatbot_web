"""
=================================================

Knowledge Builder

AI Expander

Uses Gemini to convert cleaned website text
into structured Markdown knowledge.

Version: 1.0

=================================================
"""

from pathlib import Path

from config import Config
from logger import Logger
from gemini_manager import GeminiManager


class AIExpander:

    def __init__(self):

        self.config = Config()

        self.logger = Logger()

        self.logger.info("AI Expander initialized.")

        # ------------------------------------
        # Gemini Manager
        # ------------------------------------

        self.gemini = GeminiManager()

        self.client = self.gemini.get_client()

        self.model = self.gemini.get_chat_model()

        # ------------------------------------
        # Project folders
        # ------------------------------------

        self.input_folder = Path("clean_text")

        self.output_folder = Path("knowledge_source")

        self.output_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        self.prompt_folder = Path("prompts")

        self.generated_files = []

    def load_text(self, filepath: Path):

        self.logger.info(f"Loading : {filepath.name}")

        try:

            text = filepath.read_text(
                encoding="utf-8"
            )

            self.logger.info(
                f"Loaded {len(text):,} characters."
            )

            return text

        except Exception as ex:

            self.logger.error(
                f"Unable to load {filepath.name} : {ex}"
            )

            return None

    def load_prompt(self, filename):

        """
        Loads one prompt template.
        """

        filepath = self.prompt_folder / filename

        self.logger.info(
            f"Loading prompt : {filepath.name}"
        )

        try:

            prompt = filepath.read_text(
                encoding="utf-8"
            )

            self.logger.info(
                f"Loaded {len(prompt):,} characters."
            )

            return prompt

        except Exception as ex:

            self.logger.error(
                f"Unable to load prompt : {ex}"
            )

            return None

    def build_prompt(
        self,
        prompt_template,
        content
    ):

        """
        Builds the final prompt sent to Gemini.
        """

        self.logger.info(
            "Building AI prompt..."
        )

        if prompt_template is None:

            self.logger.error(
                "Prompt template is missing."
            )

            return None

        if content is None:

            self.logger.error(
                "Content is missing."
            )

            return None

        prompt = prompt_template.replace(
            "{{CONTENT}}",
            content.strip()
        )

        self.logger.info(
            f"Prompt built ({len(prompt):,} characters)."
        )

        return prompt

    def call_gemini(self, prompt):

        """
        Sends a prompt to Gemini.
        """

        self.logger.info(
            "Sending prompt to Gemini..."
        )

        if prompt is None:

            self.logger.error(
                "Prompt is empty."
            )

            return None

        try:

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )

            markdown = response.text

            self.logger.info(
                f"Gemini returned {len(markdown):,} characters."
            )

            return markdown

        except Exception as ex:

            self.logger.error(
                f"Gemini failed : {ex}"
            )

            import traceback

            print()
            print("=" * 60)
            print("FULL GEMINI ERROR")
            print("=" * 60)

            traceback.print_exc()

            return None

    def save_markdown(
        self,
        markdown,
        category,
        filename
    ):

        """
        Saves AI-generated Markdown.
        """

        if markdown is None:

            self.logger.error(
                "Nothing to save."
            )

            return None

        try:

            folder = self.output_folder / category

            folder.mkdir(
                parents=True,
                exist_ok=True
            )

            if not filename.endswith(".md"):

                filename += ".md"

            filepath = folder / filename

            filepath.write_text(
                markdown,
                encoding="utf-8"
            )

            self.logger.info(
                f"Saved : {filepath}"
            )

            self.generated_files.append(filepath)

            return filepath

        except Exception as ex:

            self.logger.error(
                f"Unable to save markdown : {ex}"
            )

            return None


if __name__ == "__main__":

    expander = AIExpander()

    filepath = Path("clean_text/index.txt")

    text = expander.load_text(filepath)

    template = expander.load_prompt(
        "service_prompt.md"
    )

    prompt = expander.build_prompt(
        template,
        text
    )

    markdown = expander.call_gemini(prompt)

    print()
    print("=" * 60)
    print("GEMINI RESPONSE")
    print("=" * 60)

    if markdown:

        print(markdown[:4000])

    else:

        print("Gemini returned None.")

    filepath = expander.save_markdown(
        markdown,
        "services",
        "homepage"
    )

    print()
    print("=" * 60)
    print("SAVED FILE")
    print("=" * 60)
    print(filepath)
