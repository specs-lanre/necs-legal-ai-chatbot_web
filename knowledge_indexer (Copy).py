"""
=================================================

Knowledge Builder

Knowledge Indexer

Reads AI-generated Markdown documents and prepares
them for embedding and semantic search.

Version: 1.0

=================================================
"""

from pathlib import Path

from config import Config
from logger import Logger
from gemini_manager import GeminiManager


class KnowledgeIndexer:

    def __init__(self):
        """
        Initializes the Knowledge Indexer.
        """

        self.config = Config()

        self.logger = Logger()

        self.logger.info(
            "Knowledge Indexer initialized."
        )

        # ------------------------------------
        # Gemini
        # ------------------------------------

        self.gemini = GeminiManager()

        self.client = self.gemini.get_client()

        self.embedding_model = (
            self.gemini.get_embedding_model()
        )

        # ------------------------------------
        # Project folders
        # ------------------------------------

        self.source_folder = Path(
            "knowledge_source"
        )

        self.index_folder = Path(
            "knowledge_index"
        )

        self.index_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        # ------------------------------------
        # Working data
        # ------------------------------------

        self.documents = []

        self.chunks = []

    def load_documents(self):
        """
        Loads every Markdown document inside
        the knowledge_source folder.

        Returns
        -------
        list[Path]
        """

        self.logger.info(
            "Loading Markdown documents..."
        )

        self.documents = sorted(
            self.source_folder.rglob("*.md")
        )

        self.logger.info(
            f"{len(self.documents)} documents loaded."
        )

        return self.documents

    def split_document(
        self,
        filepath: Path,
        chunk_size=2000
    ):
        """
        Splits one Markdown document into
        fixed-size text chunks.

        Parameters
        ----------
        filepath : Path

        chunk_size : int

        Returns
        -------
        list[str]
        """

        self.logger.info(
            f"Splitting : {filepath.name}"
        )

        try:

            text = filepath.read_text(
                encoding="utf-8"
            )

        except Exception as ex:

            self.logger.error(ex)

            return []

        chunks = []

        start = 0

        while start < len(text):

            chunk = text[
                start:start + chunk_size
            ]

            chunks.append(chunk)

            start += chunk_size

        self.logger.info(
            f"{len(chunks)} chunks created."
        )

        return chunks


if __name__ == "__main__":

    indexer = KnowledgeIndexer()

    print()
    print("=" * 60)
    print("LOADING DOCUMENTS")
    print("=" * 60)

    documents = indexer.load_documents()

    for document in documents:

        print(document)

    if documents:

        print()
        print("=" * 60)
        print("SPLITTING FIRST DOCUMENT")
        print("=" * 60)

        chunks = indexer.split_document(
            documents[0]
        )

        print(
            f"Chunks created : {len(chunks)}"
        )

        if chunks:

            print()
            print("FIRST CHUNK")
            print("-" * 60)
            print(chunks[0][:500])
