import os
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv
from openai import OpenAI

from app.chat.chat_history import ChatHistoryRepository
from app.rag.indexer import ChromaIndexer, CHROMA_DIR


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env", override=True)


class OpenAILLMClient:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("LLM_MODEL", "gpt-4o-mini")

        if not self.api_key:
            raise ValueError(
                "No se encontró OPENAI_API_KEY. "
                "Crea un archivo .env en la raíz del proyecto con: "
                "OPENAI_API_KEY=tu_clave_real"
            )

        if "tu_api" in self.api_key.lower() or "aqui" in self.api_key.lower():
            raise ValueError(
                "OPENAI_API_KEY parece seguir teniendo un valor de ejemplo. "
                "Reemplázalo en .env por tu clave real."
            )

        self.client = OpenAI(api_key=self.api_key)

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres un asistente útil para responder preguntas sobre contenido "
                        "scrapeado de un sitio web bancario. "
                        "Responde únicamente con base en el contexto recuperado. "
                        "Si la información no aparece en el contexto, dilo claramente. "
                        "No inventes datos."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        return response.choices[0].message.content.strip()


class RAGService:
    def __init__(
        self,
        history_repo: ChatHistoryRepository,
        llm_client: OpenAILLMClient,
        persist_path=CHROMA_DIR,
        collection_name: str = "bank_docs",
        history_limit: int = 6,
        top_k: int = 4
    ):
        self.history_repo = history_repo
        self.llm_client = llm_client
        self.history_limit = history_limit
        self.top_k = top_k

        self.indexer = ChromaIndexer(
            persist_path=persist_path,
            collection_name=collection_name
        )
        self.collection = self.indexer.collection

    def retrieve_context(self, question: str) -> List[Dict[str, Any]]:
        results = self.collection.query(
            query_texts=[question],
            n_results=self.top_k
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0] if "distances" in results else []

        context_items = []
        for i, doc in enumerate(documents):
            context_items.append({
                "chunk": doc,
                "metadata": metadatas[i] if i < len(metadatas) else {},
                "distance": distances[i] if i < len(distances) else None
            })

        return context_items

    def get_chat_history(self, session_id: str) -> List[Dict[str, Any]]:
        return self.history_repo.get_last_messages(session_id, limit=self.history_limit)

    def format_history(self, history: List[Dict[str, Any]]) -> str:
        if not history:
            return "No hay historial previo."

        lines = []
        for msg in history:
            role = msg["role"].upper()
            content = msg["message"]
            lines.append(f"{role}: {content}")

        return "\n".join(lines)

    def format_context(self, context_items: List[Dict[str, Any]]) -> str:
        if not context_items:
            return "No se recuperó contexto."

        parts = []
        for i, item in enumerate(context_items, start=1):
            meta = item.get("metadata", {})
            chunk = item.get("chunk", "")

            title = meta.get("title", "Sin título")
            url = meta.get("url", "Sin URL")
            section = meta.get("section", "unknown")
            content_type = meta.get("content_type", "web_page")
            chunk_index = meta.get("chunk_index", "N/A")

            parts.append(
                f"[Contexto {i}]\n"
                f"Título: {title}\n"
                f"URL: {url}\n"
                f"Sección: {section}\n"
                f"Tipo: {content_type}\n"
                f"Chunk: {chunk_index}\n"
                f"Contenido:\n{chunk}"
            )

        return "\n\n".join(parts)

    def build_prompt(
        self,
        question: str,
        history: List[Dict[str, Any]],
        context_items: List[Dict[str, Any]]
    ) -> str:
        history_text = self.format_history(history)
        context_text = self.format_context(context_items)

        return f"""
Responde la pregunta del usuario usando únicamente el contexto recuperado.

Reglas:
- Usa solo la información del contexto.
- Si la respuesta no está en el contexto, responde: "No encontré información suficiente en el contenido recuperado."
- Si mencionas algo importante, apóyate en el contexto.
- Sé claro y breve.

Historial reciente:
{history_text}

Contexto recuperado:
{context_text}

Pregunta actual:
{question}

Respuesta:
""".strip()

    def ask(self, session_id: str, question: str) -> Dict[str, Any]:
        history = self.get_chat_history(session_id)
        context_items = self.retrieve_context(question)
        prompt = self.build_prompt(question, history, context_items)
        answer = self.llm_client.generate(prompt)

        self.history_repo.save_message(session_id, "user", question)
        self.history_repo.save_message(session_id, "assistant", answer)

        sources = []
        seen = set()

        for item in context_items:
            meta = item.get("metadata", {})
            source_key = (meta.get("url"), meta.get("chunk_index"))

            if source_key not in seen:
                seen.add(source_key)
                sources.append({
                    "title": meta.get("title"),
                    "url": meta.get("url"),
                    "section": meta.get("section"),
                    "content_type": meta.get("content_type"),
                    "chunk_index": meta.get("chunk_index")
                })

        return {
            "session_id": session_id,
            "question": question,
            "answer": answer,
            "sources": sources,
            "history_used": len(history)
        }


if __name__ == "__main__":
    history_repo = ChatHistoryRepository()
    llm_client = OpenAILLMClient()
    rag_service = RAGService(
        history_repo=history_repo,
        llm_client=llm_client,
        history_limit=6,
        top_k=4
    )

    session_id = "demo-session-001"
    question = "¿Qué tipos de productos ofrece el banco?"

    result = rag_service.ask(session_id=session_id, question=question)

    print("\n=== RESPUESTA RAG ===")
    print(result["answer"])

    print("\n=== FUENTES ===")
    for source in result["sources"]:
        print(source)