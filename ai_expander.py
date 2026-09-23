"""
=================================================

AI Expander

Reads cleaned text files and uses Gemini AI to
expand them into structured Markdown knowledge
documents.

Pipeline:

clean_text/*.txt
        ↓
AIExpander
        ↓
knowledge_source/<category>/*.md
        ↓
KnowledgeIndexer

Version: 1.0

=================================================
"""

from pathlib import Path

from config import Config
from logger import Logger
from gemini_manager import GeminiManager


class AIExpander:

    def __init__(self):
        """
        Initialize the AI Expander.
        """

        # ----------------------------------------
        # Configuration
        # ----------------------------------------

        self.config = Config()

        # ----------------------------------------
        # Logger
        # ----------------------------------------

        self.logger = Logger()

        self.logger.info(
            "AI Expander initialized."
        )

        # ----------------------------------------
        # Gemini
        # ----------------------------------------

        self.gemini = GeminiManager()

        self.client = self.gemini.get_client()

        self.chat_model = (
            self.gemini.get_chat_model()
        )

        # ----------------------------------------
        # Project folders
        # ----------------------------------------

        self.input_folder = Path(
            "clean_text"
        )

        self.output_folder = Path(
            "knowledge_source"
        )

        self.prompt_folder = Path(
            "prompts"
        )

        # ----------------------------------------
        # Create folders if necessary
        # ----------------------------------------

        self.input_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        self.output_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        self.prompt_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        # ----------------------------------------
        # Working data
        # ----------------------------------------

        self.generated_files = []

    # =================================================
    # LOAD PROMPT
    # =================================================

    def load_prompt(self, prompt_name):
        """
        Load an AI prompt from the prompts folder.

        Parameters
        ----------
        prompt_name : str
            Prompt filename.

        Returns
        -------
        str
            Prompt text.
        """

        filepath = (
            self.prompt_folder / prompt_name
        )

        self.logger.info(
            f"Loading prompt : {filepath}"
        )

        if not filepath.exists():

            self.logger.error(
                f"Prompt not found : {filepath}"
            )

            return ""

        try:

            prompt = filepath.read_text(
                encoding="utf-8"
            )

            return prompt

        except Exception as ex:

            self.logger.error(
                f"Unable to read prompt: {ex}"
            )

            return ""

    # =================================================
    # LOAD TEXT FILE
    # =================================================

    def load_text(self, filepath):
        """
        Load a cleaned text file.

        Parameters
        ----------
        filepath : Path

        Returns
        -------
        str
        """

        self.logger.info(
            f"Loading text : {filepath}"
        )

        try:

            return filepath.read_text(
                encoding="utf-8"
            )

        except Exception as ex:

            self.logger.error(
                f"Unable to read {filepath}: {ex}"
            )

            return ""

    # =================================================
    # EXPAND FILE
    # =================================================

    def expand_file(
        self,
        filepath: Path,
        prompt_name="service_prompt.md",
        category="services"
    ):
        """
        Expand one cleaned text file using Gemini.

        The generated Markdown is saved under:

        knowledge_source/<category>/

        Parameters
        ----------
        filepath : Path
            Input text file.

        prompt_name : str
            Prompt filename.

        category : str
            Output category.

        Returns
        -------
        Path or None
        """

        self.logger.info(
            f"Expanding : {filepath}"
        )

        # ----------------------------------------
        # Load source text
        # ----------------------------------------

        text = self.load_text(filepath)

        if not text.strip():

            self.logger.error(
                f"Empty input file : {filepath}"
            )

            return None

        # ----------------------------------------
        # Load prompt
        # ----------------------------------------

        prompt = self.load_prompt(
            prompt_name
        )

        if not prompt.strip():

            self.logger.error(
                f"Empty prompt : {prompt_name}"
            )

            return None

        # ----------------------------------------
        # Build AI request
        # ----------------------------------------

        full_prompt = f"""
{prompt}

SOURCE DOCUMENT
================

{text}

IMPORTANT INSTRUCTIONS
======================

Return only the final Markdown document.

Do not include explanations before the Markdown.

Do not include explanations after the Markdown.

Use clear headings and sections.

Preserve factual information from the source document.

Do not invent facts that are not supported by
the source document.
"""

        self.logger.info(
            f"Sending {filepath.name} to Gemini..."
        )

        # ----------------------------------------
        # Gemini request
        # ----------------------------------------

        try:

            '''
            response = (
                self.client.models.generate_content(
                    model=self.chat_model,
                    contents=full_prompt
                )
            )
            '''
            
            
            response = self.client.interactions.create(
            model=self.chat_model,input=full_prompt,store=False
            )

        except Exception as ex:

            self.logger.error(
                f"Gemini request failed: {ex}"
            )

            return None

        # ----------------------------------------
        # Extract response
        # ----------------------------------------

        try:

            #markdown = response.text
            markdown = response.output_text

        except Exception as ex:

            self.logger.error(
                f"Unable to read Gemini response: {ex}"
            )

            return None

        if not markdown or not markdown.strip():

            self.logger.error(
                "Gemini returned an empty response."
            )

            return None

        markdown = markdown.strip()

        # ----------------------------------------
        # Save Markdown
        # ----------------------------------------

        return self.save_markdown(
            filepath=filepath,
            markdown=markdown,
            category=category
        )

    # =================================================
    # SAVE MARKDOWN
    # =================================================

    def save_markdown(
        self,
        filepath: Path,
        markdown: str,
        category="services"
    ):
        """
        Save generated Markdown inside:

        knowledge_source/<category>/

        Example:

        clean_text/services.txt

                ↓

        knowledge_source/services/services.md
        """

        # ----------------------------------------
        # Create category directory
        # ----------------------------------------

        folder = (
            self.output_folder / category
        )

        folder.mkdir(
            parents=True,
            exist_ok=True
        )

        # ----------------------------------------
        # Output filename
        # ----------------------------------------

        filename = filepath.stem

        if not filename.endswith(".md"):

            filename += ".md"

        output_file = folder / filename

        # ----------------------------------------
        # Write Markdown
        # ----------------------------------------

        try:

            output_file.write_text(
                markdown,
                encoding="utf-8"
            )

        except Exception as ex:

            self.logger.error(
                f"Unable to save Markdown: {ex}"
            )

            return None

        self.generated_files.append(
            output_file
        )

        self.logger.info(
            f"Markdown saved : {output_file}"
        )

        return output_file

    # =================================================
    # EXPAND ALL
    # =================================================

    def expand_all(
        self,
        prompt_name="service_prompt.md",
        category="services"
    ):
        """
        Expand all TXT files in clean_text.

        NOTE:
        This method should only be used when all
        input files belong to the same category
        and prompt.

        Returns
        -------
        list[Path]
        """

        self.logger.info(
            "Starting batch expansion..."
        )

        # ----------------------------------------
        # Find text files
        # ----------------------------------------

        text_files = sorted(
            self.input_folder.glob("*.txt")
        )

        self.logger.info(
            f"{len(text_files)} text files found."
        )

        if not text_files:

            self.logger.info(
                "No text files found."
            )

            return []

        # ----------------------------------------
        # Process files
        # ----------------------------------------

        for filepath in text_files:

            self.expand_file(
                filepath=filepath,
                prompt_name=prompt_name,
                category=category
            )

        # ----------------------------------------
        # Summary
        # ----------------------------------------

        self.logger.info(
            f"{len(self.generated_files)} "
            f"Markdown files generated."
        )

        return self.generated_files


# =====================================================
# TEST / MAIN
# =====================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("AI EXPANDER")
    print("=" * 60)

    expander = AIExpander()

    print()
    print("Input folder  :", expander.input_folder)
    print("Output folder :", expander.output_folder)
    print("Prompt folder :", expander.prompt_folder)
    print("Chat model    :", expander.chat_model)

    print()
    print("=" * 60)
    print("AI EXPANDER READY")
    print("=" * 60)
