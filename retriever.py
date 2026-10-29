"""
=================================================
Knowledge Builder - Retriever
Loads the knowledge index and retrieves the most
relevant knowledge chunks for a user query.
=================================================

Pipeline:
User Query -> Query Embedding -> Cosine Similarity
-> Rank Knowledge Chunks -> Top Relevant Chunks

Version: 1.0
"""

import json
import math
import time
from pathlib import Path

from config import Config
from logger import Logger
from gemini_manager import GeminiManager


class Retriever:

    def __init__(self):
        # Initialization timing
        init_start = time.perf_counter()

        self.config = Config()
        self.logger = Logger()
        self.logger.info("Retriever initialized.")

        self.gemini = GeminiManager()
        self.client = self.gemini.get_client()
        self.embedding_model = self.gemini.get_embedding_model()

        self.index_file = Path("knowledge_index") / "embeddings.json"
        self.index_data = {}
        self.chunks = []

        # In-memory cache for recent query embeddings.
        # This cache is cleared whenever the API process restarts.
        self.embedding_cache = {}
        self.embedding_cache_max_size = 100

        init_time = time.perf_counter() - init_start
        self.logger.info(
            f"Retriever initialization time: {init_time:.4f} seconds"
        )

    # -------------------------------------------------
    # LOAD KNOWLEDGE INDEX
    # -------------------------------------------------

    def load_index(self):
        load_start = time.perf_counter()
        self.logger.info("Loading knowledge index...")

        if not self.index_file.exists():
            self.logger.error(f"Index file not found: {self.index_file}")
            return False

        try:
            with self.index_file.open("r", encoding="utf-8") as file:
                self.index_data = json.load(file)

            self.chunks = self.index_data.get("chunks", [])

            load_time = time.perf_counter() - load_start
            self.logger.info("Knowledge index loaded.")
            self.logger.info(f"Chunks available: {len(self.chunks)}")
            self.logger.info(f"Index loading time: {load_time:.4f} seconds")
            return True

        except Exception as ex:
            load_time = time.perf_counter() - load_start
            self.logger.error(f"Unable to load knowledge index: {ex}")
            self.logger.error(
                f"Index loading failed after {load_time:.4f} seconds"
            )
            return False

    # -------------------------------------------------
    # CREATE QUERY EMBEDDING (WITH CACHE)
    # -------------------------------------------------

    def create_query_embedding(self, query):
        if not query or not query.strip():
            self.logger.error("Cannot embed an empty query.")
            return None

        # Normalize surrounding whitespace and case for cache matching.
        # The original query is still used for the Gemini API call on a miss.
        cache_key = query.strip().casefold()

        if cache_key in self.embedding_cache:
            self.logger.info("Query embedding cache hit.")
            return self.embedding_cache[cache_key]

        self.logger.info("Query embedding cache miss.")

        try:
            embedding_start = time.perf_counter()

            response = self.client.models.embed_content(
                model=self.embedding_model,
                contents=query
            )

            embedding_api_time = time.perf_counter() - embedding_start
            self.logger.info("----------------------------------------")
            self.logger.info(
                f"Gemini embedding API time: {embedding_api_time:.4f} seconds"
            )
            self.logger.info("----------------------------------------")

            if not response.embeddings:
                self.logger.error("Gemini returned no query embedding.")
                return None

            embedding = response.embeddings[0]
            values = embedding.values

            if not values:
                self.logger.error("Gemini returned an empty query embedding.")
                return None

            embedding_values = list(values)

            self.logger.info(
                f"Query embedding dimensions: {len(embedding_values)}"
            )

            # Evict the oldest inserted entry when the cache is full.
            if len(self.embedding_cache) >= self.embedding_cache_max_size:
                oldest_key = next(iter(self.embedding_cache))
                del self.embedding_cache[oldest_key]

            self.embedding_cache[cache_key] = embedding_values
            return embedding_values

        except Exception as ex:
            self.logger.error(f"Query embedding failed: {ex}")
            return None

    # -------------------------------------------------
    # COSINE SIMILARITY
    # -------------------------------------------------

    def cosine_similarity(self, vector_a, vector_b):
        if not vector_a or not vector_b:
            return 0.0

        if len(vector_a) != len(vector_b):
            self.logger.error("Vector dimensions do not match.")
            return 0.0

        dot_product = sum(
            a * b for a, b in zip(vector_a, vector_b)
        )

        magnitude_a = math.sqrt(sum(a * a for a in vector_a))
        magnitude_b = math.sqrt(sum(b * b for b in vector_b))

        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0

        return dot_product / (magnitude_a * magnitude_b)

    # -------------------------------------------------
    # SEARCH
    # -------------------------------------------------

    def search(self, query, top_k=3):
        total_start = time.perf_counter()

        self.logger.info("")
        self.logger.info("========================================")
        self.logger.info("RETRIEVAL PERFORMANCE TIMING")
        self.logger.info("========================================")
        self.logger.info(f"Searching knowledge for: {query}")

        # Step 1: Load the index if it has not already been loaded.
        index_start = time.perf_counter()

        if not self.chunks:
            if not self.load_index():
                self.logger.error("Knowledge index could not be loaded.")
                return []

        index_time = time.perf_counter() - index_start

        # Step 2: Create or retrieve the query embedding.
        embedding_start = time.perf_counter()
        query_embedding = self.create_query_embedding(query)
        embedding_total_time = time.perf_counter() - embedding_start

        if query_embedding is None:
            self.logger.error("Unable to create query embedding.")
            return []

        # Step 3: Calculate similarity for each indexed chunk.
        similarity_start = time.perf_counter()
        results = []

        for chunk in self.chunks:
            stored_embedding = chunk.get("embedding")

            if not stored_embedding:
                continue

            score = self.cosine_similarity(
                query_embedding,
                stored_embedding
            )

            results.append({
                "id": chunk.get("id"),
                "source": chunk.get("source"),
                "chunk": chunk.get("chunk"),
                "text": chunk.get("text"),
                "score": score
            })

        similarity_time = time.perf_counter() - similarity_start

        # Step 4: Sort and return the top results.
        ranking_start = time.perf_counter()
        results.sort(key=lambda item: item["score"], reverse=True)
        results = results[:top_k]
        ranking_time = time.perf_counter() - ranking_start

        total_time = time.perf_counter() - total_start

        # Performance report
        self.logger.info("")
        self.logger.info("========================================")
        self.logger.info("RETRIEVAL PERFORMANCE REPORT")
        self.logger.info("========================================")
        self.logger.info(f"Index loading:       {index_time:.4f} seconds")
        self.logger.info(
            f"Query embedding:     {embedding_total_time:.4f} seconds"
        )
        self.logger.info(
            f"Cosine similarity:   {similarity_time:.4f} seconds"
        )
        self.logger.info(f"Ranking / sorting:   {ranking_time:.4f} seconds")
        self.logger.info(f"TOTAL RETRIEVAL:     {total_time:.4f} seconds")
        self.logger.info(f"Results returned:    {len(results)}")
        self.logger.info("========================================")

        return results

    # -------------------------------------------------
    # DISPLAY RESULTS
    # -------------------------------------------------

    def display_results(self, results):
        print()
        print("=" * 60)
        print("RETRIEVAL RESULTS")
        print("=" * 60)

        if not results:
            print("No relevant results found.")
            return

        for position, result in enumerate(results, start=1):
            print()
            print(f"RESULT {position}")
            print("-" * 60)
            print("ID       :", result["id"])
            print("Source   :", result["source"])
            print("Chunk    :", result["chunk"])
            print("Score    :", round(result["score"], 6))
            print()
            print("TEXT:")
            print(result["text"])

    # -------------------------------------------------
    # TEST SEARCH
    # -------------------------------------------------

    def test_search(self, query, top_k=3):
        print()
        print("=" * 60)
        print("RETRIEVER TEST")
        print("=" * 60)
        print()
        print("Query:", query)
        print("Embedding model:", self.embedding_model)
        print("Index:", self.index_file)
        print()

        test_start = time.perf_counter()
        results = self.search(query=query, top_k=top_k)
        test_time = time.perf_counter() - test_start

        self.display_results(results)

        print()
        print("=" * 60)
        print("COMPLETE RETRIEVER TEST TIME")
        print("=" * 60)
        print(f"{test_time:.4f} seconds")
        print("=" * 60)

        return results


# =================================================
# MAIN TEST
# =================================================

if __name__ == "__main__":
    print()
    print("=" * 60)
    print("RETRIEVER")
    print("=" * 60)

    program_start = time.perf_counter()
    retriever = Retriever()

    print()
    print("Index file      :", retriever.index_file)
    print("Embedding model :", retriever.embedding_model)
    print()

    print("=" * 60)
    print("LOADING INDEX")
    print("=" * 60)

    load_start = time.perf_counter()

    if not retriever.load_index():
        print()
        print("ERROR: Knowledge index could not be loaded.")
        raise SystemExit(1)

    load_time = time.perf_counter() - load_start

    print()
    print("Documents:", retriever.index_data.get("document_count"))
    print("Chunks:", retriever.index_data.get("chunk_count"))
    print(f"Index load time: {load_time:.4f} seconds")
    print()

    print("=" * 60)
    print("SEARCH TEST")
    print("=" * 60)

    query = "What intellectual property services does NECS Legal provide?"
    retriever.test_search(query=query, top_k=3)

    program_time = time.perf_counter() - program_start
    print()
    print("=" * 60)
    print("COMPLETE PROGRAM TIME")
    print("=" * 60)
    print(f"{program_time:.4f} seconds")
    print("=" * 60)
