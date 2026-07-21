import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any

import chromadb
from chromadb.utils import embedding_functions


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
CLEAN_DATA_DIR = DATA_DIR / "clean"
CHROMA_DIR = DATA_DIR / "chroma"

CLEAN_DATA_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)


class DocumentLoader:
    def __init__(self, clean_data_path: Path):
        self.clean_data_path = Path(clean_data_path)

    def load(self) -> List[Dict]:
        documents = []

        if not self.clean_data_path.exists():
            print(f"[WARN] La carpeta no existe: {self.clean_data_path}")
            return documents

        for file in self.clean_data_path.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    documents.append(json.load(f))
            except Exception as e:
                print(f"[ERROR] No se pudo leer {file}: {e}")

        return documents


class TextChunker:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap debe ser menor que chunk_size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> List[str]:
        if not text or not text.strip():
            return []

        text = " ".join(text.split())
        chunks = []
        start = 0
        step = self.chunk_size - self.chunk_overlap

        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start += step

        return chunks


class ChromaIndexer:
    def __init__(
        self,
        persist_path: Path = CHROMA_DIR,
        collection_name: str = "bank_docs",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        self.persist_path = Path(persist_path)
        self.persist_path.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name

        self.client = chromadb.PersistentClient(path=str(self.persist_path))
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_model
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn
        )

    def reset_collection(self):
        existing = [c.name for c in self.client.list_collections()]
        if self.collection_name in existing:
            self.client.delete_collection(self.collection_name)

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_fn
        )

    def _make_chunk_id(self, url: str, chunk_index: int, chunk_text: str) -> str:
        raw = f"{url}|{chunk_index}|{chunk_text[:100]}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()

    def index_documents(self, documents: List[Dict], chunker: TextChunker) -> Dict[str, Any]:
        ids, texts, metadatas = [], [], []

        skipped = 0
        empty_chunks = 0

        for doc in documents:
            url = doc.get("url", "")
            title = doc.get("title", "")
            section = doc.get("section", "unknown")
            content_type = doc.get("content_type", "web_page")
            clean_text = doc.get("clean_text", "")

            if not clean_text or not clean_text.strip():
                skipped += 1
                continue

            chunks = chunker.split_text(clean_text)

            if not chunks:
                empty_chunks += 1
                continue

            for idx, chunk in enumerate(chunks):
                chunk_id = self._make_chunk_id(url, idx, chunk)
                ids.append(chunk_id)
                texts.append(chunk)
                metadatas.append({
                    "url": url,
                    "title": title,
                    "section": section,
                    "content_type": content_type,
                    "chunk_index": idx
                })

        if texts:
            self.collection.add(
                ids=ids,
                documents=texts,
                metadatas=metadatas
            )

        return {
            "documents_received": len(documents),
            "chunks_indexed": len(texts),
            "documents_skipped": skipped,
            "documents_without_chunks": empty_chunks,
            "collection_name": self.collection_name,
            "persist_path": str(self.persist_path)
        }

    def collection_stats(self) -> Dict[str, Any]:
        return {
            "collection_name": self.collection.name,
            "total_chunks": self.collection.count(),
            "persist_path": str(self.persist_path)
        }

    def peek(self, limit: int = 5) -> Dict[str, Any]:
        return self.collection.peek(limit=limit)

    def get_all(self, limit: int = 10) -> Dict[str, Any]:
        return self.collection.get(limit=limit)

    def pretty_print_sample(self, limit: int = 5):
        data = self.collection.get(limit=limit)

        ids = data.get("ids", [])
        documents = data.get("documents", [])
        metadatas = data.get("metadatas", [])

        if not ids:
            print("[INFO] La colección está vacía.")
            return

        print("\n=== MUESTRA DE LA COLECCIÓN ===")
        for i in range(len(ids)):
            print(f"\nRegistro {i + 1}")
            print(f"ID: {ids[i]}")
            print(f"Metadata: {metadatas[i]}")
            print(f"Documento: {documents[i][:500]}")
            print("-" * 80)

    def query(self, query_text: str, n_results: int = 3) -> Dict[str, Any]:
        return self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )

    def pretty_print_query(self, query_text: str, n_results: int = 3):
        results = self.query(query_text=query_text, n_results=n_results)

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0] if "distances" in results else []

        print(f"\n=== RESULTADOS PARA QUERY: {query_text} ===")
        if not documents:
            print("[INFO] No se encontraron resultados.")
            return

        for i, doc in enumerate(documents):
            print(f"\nResultado {i + 1}")
            if i < len(metadatas):
                print(f"Metadata: {metadatas[i]}")
            if i < len(distances):
                print(f"Distance: {distances[i]}")
            print(f"Chunk: {doc[:500]}")
            print("=" * 80)


def build_vector_db(
    clean_data_path: Path = CLEAN_DATA_DIR,
    persist_path: Path = CHROMA_DIR,
    collection_name: str = "bank_docs",
    chunk_size: int = 800,
    chunk_overlap: int = 150,
    reset: bool = False
) -> ChromaIndexer:
    loader = DocumentLoader(clean_data_path)
    documents = loader.load()

    chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    indexer = ChromaIndexer(
        persist_path=persist_path,
        collection_name=collection_name
    )

    if reset:
        print("[INFO] Reseteando colección...")
        indexer.reset_collection()

    result = indexer.index_documents(documents, chunker)

    print("\n=== INDEXACIÓN COMPLETADA ===")
    for k, v in result.items():
        print(f"{k}: {v}")

    print("\n=== ESTADÍSTICAS DE LA COLECCIÓN ===")
    stats = indexer.collection_stats()
    for k, v in stats.items():
        print(f"{k}: {v}")

    return indexer


if __name__ == "__main__":
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"CLEAN_DATA_DIR: {CLEAN_DATA_DIR}")
    print(f"CHROMA_DIR: {CHROMA_DIR}")

    indexer = build_vector_db(
        clean_data_path=CLEAN_DATA_DIR,
        persist_path=CHROMA_DIR,
        collection_name="bank_docs",
        chunk_size=800,
        chunk_overlap=150,
        reset=False
    )

    indexer.pretty_print_sample(limit=5)

    indexer.pretty_print_query(
        query_text="¿Qué tipos de productos ofrece el banco?",
        n_results=3
    )
