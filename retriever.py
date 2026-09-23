"""
=================================================

Knowledge Builder

Retriever

Loads the knowledge index and retrieves the most
relevant knowledge chunks for a user query.

Pipeline:

User Query
    ↓
Query Embedding
    ↓
Cosine Similarity
    ↓
Rank Knowledge Chunks
    ↓
Top Relevant Chunks

Version: 1.0

=================================================
"""

import json
import math
from pathlib import Path

from config import Config
from logger import Logger
from gemini_manager import GeminiManager


class Retriever:

    def __init__(self):

        self.config = Config()

        self.logger = Logger()

        self.logger.info(
            "Retriever initialized."
        )

        self.gemini = GeminiManager()

        self.client = (
            self.gemini.get_client()
        )

        self.embedding_model = (
            self.gemini.get_embedding_model()
        )

        self.index_file = (
            Path("knowledge_index")
            / "embeddings.json"
        )

        self.index_data = {}

        self.chunks = []

    # -------------------------------------------------
    # LOAD KNOWLEDGE INDEX
    # -------------------------------------------------

    def load_index(self):

        self.logger.info(
            "Loading knowledge index..."
        )

        if not self.index_file.exists():

            self.logger.error(
                f"Index file not found: "
                f"{self.index_file}"
            )

            return False

        try:

            with self.index_file.open(
                "r",
                encoding="utf-8"
            ) as file:

                self.index_data = json.load(
                    file
                )

            self.chunks = (
                self.index_data.get(
                    "chunks",
                    []
                )
            )

            self.logger.info(
                f"Knowledge index loaded."
            )

            self.logger.info(
                f"Chunks available: "
                f"{len(self.chunks)}"
            )

            return True

        except Exception as ex:

            self.logger.error(
                f"Unable to load knowledge "
                f"index: {ex}"
            )

            return False

    # -------------------------------------------------
    # CREATE QUERY EMBEDDING
    # -------------------------------------------------

    def create_query_embedding(
        self,
        query
    ):

        if not query or not query.strip():

            self.logger.error(
                "Cannot embed an empty query."
            )

            return None

        try:

            response = (
                self.client.models.embed_content(
                    model=self.embedding_model,
                    contents=query
                )
            )

            if not response.embeddings:

                self.logger.error(
                    "Gemini returned no query embedding."
                )

                return None

            embedding = (
                response.embeddings[0]
            )

            values = embedding.values

            if not values:

                self.logger.error(
                    "Gemini returned an empty "
                    "query embedding."
                )

                return None

            return list(values)

        except Exception as ex:

            self.logger.error(
                f"Query embedding failed: {ex}"
            )

            return None

    # -------------------------------------------------
    # COSINE SIMILARITY
    # -------------------------------------------------

    def cosine_similarity(
        self,
        vector_a,
        vector_b
    ):

        if not vector_a or not vector_b:

            return 0.0

        if len(vector_a) != len(vector_b):

            self.logger.error(
                "Vector dimensions do not match."
            )

            return 0.0

        dot_product = sum(
            a * b
            for a, b in zip(
                vector_a,
                vector_b
            )
        )

        magnitude_a = math.sqrt(
            sum(
                a * a
                for a in vector_a
            )
        )

        magnitude_b = math.sqrt(
            sum(
                b * b
                for b in vector_b
            )
        )

        if (
            magnitude_a == 0
            or magnitude_b == 0
        ):

            return 0.0

        return (
            dot_product
            / (
                magnitude_a
                * magnitude_b
            )
        )

    # -------------------------------------------------
    # SEARCH
    # -------------------------------------------------

    def search(
        self,
        query,
        top_k=3
    ):

        self.logger.info(
            f"Searching knowledge for: "
            f"{query}"
        )

        if not self.chunks:

            if not self.load_index():

                return []

        query_embedding = (
            self.create_query_embedding(
                query
            )
        )

        if query_embedding is None:

            return []

        results = []

        for chunk in self.chunks:

            stored_embedding = (
                chunk.get(
                    "embedding"
                )
            )

            if not stored_embedding:

                continue

            score = (
                self.cosine_similarity(
                    query_embedding,
                    stored_embedding
                )
            )

            results.append(
                {
                    "id": chunk.get("id"),
                    "source": chunk.get(
                        "source"
                    ),
                    "chunk": chunk.get(
                        "chunk"
                    ),
                    "text": chunk.get(
                        "text"
                    ),
                    "score": score
                }
            )

        results.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        results = results[:top_k]

        self.logger.info(
            f"Retrieved {len(results)} "
            f"results."
        )

        return results

    # -------------------------------------------------
    # DISPLAY RESULTS
    # -------------------------------------------------

    def display_results(
        self,
        results
    ):

        print()

        print("=" * 60)
        print("RETRIEVAL RESULTS")
        print("=" * 60)

        if not results:

            print(
                "No relevant results found."
            )

            return

        for position, result in enumerate(
            results,
            start=1
        ):

            print()

            print(
                f"RESULT {position}"
            )

            print(
                "-" * 60
            )

            print(
                "ID       :",
                result["id"]
            )

            print(
                "Source   :",
                result["source"]
            )

            print(
                "Chunk    :",
                result["chunk"]
            )

            print(
                "Score    :",
                round(
                    result["score"],
                    6
                )
            )

            print()

            print(
                "TEXT:"
            )

            print(
                result["text"]
            )

    # -------------------------------------------------
    # TEST SEARCH
    # -------------------------------------------------

    def test_search(
        self,
        query,
        top_k=3
    ):

        print()

        print("=" * 60)
        print("RETRIEVER TEST")
        print("=" * 60)

        print()

        print(
            "Query:",
            query
        )

        print(
            "Embedding model:",
            self.embedding_model
        )

        print(
            "Index:",
            self.index_file
        )

        results = self.search(
            query=query,
            top_k=top_k
        )

        self.display_results(
            results
        )

        return results


# =================================================
# MAIN TEST
# =================================================

if __name__ == "__main__":

    print()

    print("=" * 60)
    print("RETRIEVER")
    print("=" * 60)

    retriever = Retriever()

    print()

    print(
        "Index file      :",
        retriever.index_file
    )

    print(
        "Embedding model :",
        retriever.embedding_model
    )

    print()

    print("=" * 60)
    print("LOADING INDEX")
    print("=" * 60)

    if not retriever.load_index():

        print()
        print(
            "ERROR: Knowledge index could "
            "not be loaded."
        )

        raise SystemExit(1)

    print()

    print(
        "Documents:",
        retriever.index_data.get(
            "document_count"
        )
    )

    print(
        "Chunks:",
        retriever.index_data.get(
            "chunk_count"
        )
    )

    print()

    print("=" * 60)
    print("SEARCH TEST")
    print("=" * 60)

    query = (
        "What intellectual property "
        "services does NECS Legal provide?"
    )

    retriever.test_search(
        query=query,
        top_k=3
    )
