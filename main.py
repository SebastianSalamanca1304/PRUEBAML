from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.chat.chat_history import ChatHistoryRepository
from app.rag.rag_service import OpenAILLMClient, RAGService


app = FastAPI(
    title="BBVA RAG API",
    description="API para consultas sobre contenido scrapeado e indexado.",
    version="1.0.0"
)


history_repo = ChatHistoryRepository()
llm_client = OpenAILLMClient()
rag_service = RAGService(
    history_repo=history_repo,
    llm_client=llm_client,
    history_limit=6,
    top_k=4
)


class AskRequest(BaseModel):
    session_id: str = Field(..., example="demo-session-001")
    question: str = Field(..., example="¿Qué tipos de productos ofrece el banco?")


class SourceItem(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    section: Optional[str] = None
    content_type: Optional[str] = None
    chunk_index: Optional[int | str] = None


class AskResponse(BaseModel):
    session_id: str
    question: str
    answer: str
    sources: List[SourceItem]
    history_used: int


@app.get("/")
def root():
    return {
        "message": "BBVA RAG API funcionando",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask_question(payload: AskRequest):
    try:
        result = rag_service.ask(
            session_id=payload.session_id,
            question=payload.question
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history/{session_id}")
def get_history(session_id: str) -> Dict[str, Any]:
    try:
        messages = history_repo.get_last_messages(session_id, limit=20)
        return {
            "session_id": session_id,
            "messages": messages
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))