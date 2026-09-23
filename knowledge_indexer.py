"""
=================================================

Knowledge Builder

Knowledge Indexer

Reads AI-generated Markdown documents from
knowledge_source/, splits them into chunks,
creates Gemini embeddings, and saves the
search index.

Pipeline:

knowledge_source/*.md
        ↓
    Documents
        ↓
      Chunks
        ↓
Gemini Embeddings
        ↓
knowledge_index/embeddings.json

Version: 1.0

=================================================
"""

import json
from pathlib import Path

from config import Config
from logger import Logger
from gemini_manager import GeminiManager


class KnowledgeIndexer:

    def __init__(self):
        """
        Initialize the Knowledge Indexer.
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
            "Knowledge Indexer initialized."
        )

        # ----------------------------------------
        # Gemini
        # ----------------------------------------

        self.gemini = GeminiManager()

        self.client = self.gemini.get_client()

        self.embedding_model = (
            self.gemini.get_embedding_model()
        )

        # ----------------------------------------
        # Project folders
        # ----------------------------------------

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

        # ----------------------------------------
        # Index file
        # ----------------------------------------

        self.index_file = (
            self.index_folder / "embeddings.json"
        )

        # ----------------------------------------
        # Working data
        # ----------------------------------------

        self.documents = []

        self.chunks = []

        self.embeddings = []

        self.index_data = {}

    # =================================================
    # LOAD DOCUMENTS
    # =================================================

    def load_documents(self):
        """
        Load every Markdown document inside
        knowledge_source/.

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

    # =================================================
    # SPLIT DOCUMENT
    # =================================================

    def split_document(
        self,
        filepath: Path,
        chunk_size=2000
    ):
        """
        Split one Markdown document into
        fixed-size text chunks.

        Parameters
        ----------
        filepath : Path
            Markdown file.

        chunk_size : int
            Maximum number of characters per chunk.

        Returns
        -------
        list[str]
        """

        self.logger.info(
            f"Splitting : {filepath}"
        )

        try:

            text = filepath.read_text(
                encoding="utf-8"
            )

        except Exception as ex:

            self.logger.error(
                f"Unable to read {filepath}: {ex}"
            )

            return []

        text = text.strip()

        if not text:

            self.logger.error(
                f"Empty document : {filepath}"
            )

            return []

        chunks = []

        start = 0

        while start < len(text):

            chunk = text[
                start:start + chunk_size
            ]

            chunk = chunk.strip()

            if chunk:

                chunks.append(chunk)

            start += chunk_size

        self.logger.info(
            f"{len(chunks)} chunks created."
        )

        return chunks

    # =================================================
    # CREATE EMBEDDING
    # =================================================

    def create_embedding(self, text):
        """
        Create a Gemini embedding for one text chunk.

        Parameters
        ----------
        text : str

        Returns
        -------
        list[float] or None
        """

        if not text or not text.strip():

            self.logger.error(
                "Cannot create embedding for empty text."
            )

            return None

        try:

            response = self.client.models.embed_content(
                model=self.embedding_model,
                contents=text
            )

            if not response.embeddings:

                self.logger.error(
                    "Gemini returned no embeddings."
                )

                return None

            embedding = response.embeddings[0]

            values = embedding.values

            if not values:

                self.logger.error(
                    "Gemini returned an empty embedding."
                )

                return None

            return list(values)

        except Exception as ex:

            self.logger.error(
                f"Embedding request failed: {ex}"
            )

            return None

    # =================================================
    # BUILD INDEX
    # =================================================

    def build_index(self, chunk_size=2000):
        """
        Build the complete embedding index.

        Process:

        Markdown documents
              ↓
        Text chunks
              ↓
        Gemini embeddings
              ↓
        Index records

        Returns
        -------
        dict
        """

        self.logger.info(
            "Building knowledge index..."
        )

        # ----------------------------------------
        # Load documents
        # ----------------------------------------

        documents = self.load_documents()

        if not documents:

            self.logger.error(
                "No Markdown documents found."
            )

            return {}

        # ----------------------------------------
        # Reset working data
        # ----------------------------------------

        self.chunks = []

        self.embeddings = []

        # ----------------------------------------
        # Process documents
        # ----------------------------------------

        chunk_counter = 0

        for document in documents:

            document_chunks = self.split_document(
                document,
                chunk_size=chunk_size
            )

            for chunk_number, chunk_text in enumerate(
                document_chunks
            ):

                chunk_counter += 1

                self.logger.info(
                    f"Creating embedding "
                    f"{chunk_counter}..."
                )

                embedding = self.create_embedding(
                    chunk_text
                )

                if embedding is None:

                    self.logger.error(
                        f"Skipping chunk "
                        f"{chunk_counter}."
                    )

                    continue

                record = {
                    "id": chunk_counter,
                    "source": str(document),
                    "chunk": chunk_number,
                    "text": chunk_text,
                    "embedding": embedding
                }

                self.chunks.append(record)

                self.embeddings.append(
                    embedding
                )

        # ----------------------------------------
        # Build final index
        # ----------------------------------------

        if not self.chunks:

            self.logger.error(
                "No indexed chunks were created."
            )

            return {}

        dimension = len(
            self.chunks[0]["embedding"]
        )

        self.index_data = {
            "version": "1.0",
            "embedding_model": self.embedding_model,
            "embedding_dimension": dimension,
            "document_count": len(documents),
            "chunk_count": len(self.chunks),
            "chunks": self.chunks
        }

        self.logger.info(
            f"Index built successfully."
        )

        self.logger.info(
            f"Documents : {len(documents)}"
        )

        self.logger.info(
            f"Chunks    : {len(self.chunks)}"
        )

        self.logger.info(
            f"Dimension : {dimension}"
        )

        return self.index_data

    # =================================================
    # SAVE INDEX
    # =================================================

    def save_index(self):
        """
        Save the current index to embeddings.json.

        Returns
        -------
        bool
        """

        if not self.index_data:

            self.logger.error(
                "No index data available to save."
            )

            return False

        try:

            self.index_folder.mkdir(
                parents=True,
                exist_ok=True
            )

            with self.index_file.open(
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    self.index_data,
                    file,
                    indent=2,
                    ensure_ascii=False
                )

            self.logger.info(
                f"Index saved : {self.index_file}"
            )

            return True

        except Exception as ex:

            self.logger.error(
                f"Unable to save index: {ex}"
            )

            return False

    # =================================================
    # LOAD INDEX
    # =================================================

    def load_index(self):
        """
        Load an existing embeddings.json file.

        Returns
        -------
        dict
        """

        if not self.index_file.exists():

            self.logger.error(
                f"Index file not found : "
                f"{self.index_file}"
            )

            return {}

        try:

            with self.index_file.open(
                "r",
                encoding="utf-8"
            ) as file:

                self.index_data = json.load(
                    file
                )

            self.chunks = self.index_data.get(
                "chunks",
                []
            )

            self.embeddings = [
                chunk["embedding"]
                for chunk in self.chunks
                if "embedding" in chunk
            ]

            self.logger.info(
                f"Index loaded : {self.index_file}"
            )

            self.logger.info(
                f"Chunks loaded : {len(self.chunks)}"
            )

            return self.index_data

        except Exception as ex:

            self.logger.error(
                f"Unable to load index: {ex}"
            )

            return {}

    # =================================================
    # REBUILD
    # =================================================

    def rebuild(self, chunk_size=2000):
        """
        Completely rebuild the knowledge index.

        Process:

        knowledge_source/
              ↓
        documents
              ↓
        chunks
              ↓
        embeddings
              ↓
        embeddings.json

        Returns
        -------
        dict
        """

        self.logger.info(
            "Rebuilding knowledge index..."
        )

        # ----------------------------------------
        # Remove previous index from memory
        # ----------------------------------------

        self.documents = []

        self.chunks = []

        self.embeddings = []

        self.index_data = {}

        # ----------------------------------------
        # Build new index
        # ----------------------------------------

        index = self.build_index(
            chunk_size=chunk_size
        )

        if not index:

            self.logger.error(
                "Index rebuild failed."
            )

            return {}

        # ----------------------------------------
        # Save new index
        # ----------------------------------------

        if not self.save_index():

            self.logger.error(
                "Index rebuild could not be saved."
            )

            return {}

        self.logger.info(
            "Knowledge index rebuilt successfully."
        )

        return self.index_data


# =====================================================
# MAIN TEST
# =====================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("KNOWLEDGE INDEXER")
    print("=" * 60)

    indexer = KnowledgeIndexer()

    print()
    print("Source folder    :", indexer.source_folder)
    print("Index folder     :", indexer.index_folder)
    print("Index file       :", indexer.index_file)
    print("Embedding model  :", indexer.embedding_model)

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
        print("BUILDING INDEX")
        print("=" * 60)

        index = indexer.build_index()

        if index:

            print()
            print("=" * 60)
            print("SAVING INDEX")
            print("=" * 60)

            if indexer.save_index():

                print()
                print("Index successfully saved.")

                print(
                    "File :",
                    indexer.index_file
                )

            else:

                print(
                    "ERROR: Unable to save index."
                )

        else:

            print(
                "ERROR: Index could not be built."
            )

    else:

        print()
        print(
            "No Markdown documents found."
        )
