"""
IOCL ChatBot - RAG Service
Uses HuggingFace embeddings (offline) + Gemini Flash for answers
Run: python rag_service.py
"""

import os
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.llms import HuggingFaceHub

load_dotenv(Path(__file__).parent / ".env")

GOOGLE_API_KEY    = os.getenv("GOOGLE_API_KEY", "")
VECTOR_STORE_PATH = Path(__file__).parent / os.getenv("VECTOR_STORE_PATH", "./vector_store")
EMBEDDING_MODEL   = "all-MiniLM-L6-v2"

app = FastAPI(title="IOCL RAG Service", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])


class QueryRequest(BaseModel):
    question:   str
    language:   str = "en"
    session_id: Optional[str] = ""
    top_k:      Optional[int] = 4


class SourceChunk(BaseModel):
    content:     str
    source_file: str
    page:        int
    category:    str


class QueryResponse(BaseModel):
    answer:     str
    sources:    list[SourceChunk]
    language:   str
    found:      bool
    model_used: str


retriever   = None
qa_chain_en = None
qa_chain_hi = None

PROMPT_EN = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are IOCL ChatBot, an expert assistant for Indian Oil Corporation Limited officers.
Answer questions about IOCL IT Policies and CDA Rules using ONLY the context below.
If the answer is not in the context say: "I could not find this in the uploaded IOCL policy documents. Please contact your HR or IT department."

Be clear, professional and use bullet points for lists.

Context:
{context}

Question: {question}

Answer:"""
)

PROMPT_HI = PromptTemplate(
    input_variables=["context", "question"],
    template="""आप IOCL ChatBot हैं। नीचे दिए गए संदर्भ से ही उत्तर दें।
यदि उत्तर नहीं मिले तो कहें: "यह जानकारी IOCL नीति दस्तावेज़ों में नहीं मिली।"

संदर्भ:
{context}

प्रश्न: {question}

उत्तर:"""
)


@app.on_event("startup")
async def startup_event():
    global retriever, qa_chain_en, qa_chain_hi

    if not VECTOR_STORE_PATH.exists():
        print("Vector store not found. Run: python ingest.py")
        return

    print("Loading vector store ...")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    vector_store = Chroma(
        persist_directory=str(VECTOR_STORE_PATH),
        embedding_function=embeddings,
        collection_name="iocl_policies",
    )

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4},
    )

    # Use Google Gemini if API key available, else use a simple retrieval approach
    if GOOGLE_API_KEY and GOOGLE_API_KEY != "your-gemini-api-key-here":
        try:
            import google.generativeai as genai
            from langchain_google_genai import ChatGoogleGenerativeAI
            genai.configure(api_key=GOOGLE_API_KEY)
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=GOOGLE_API_KEY,
                temperature=0.1,
                convert_system_message_to_human=True,
            )
            print("Using Google Gemini for answers")
        except Exception as e:
            print(f"Gemini not available: {e}. Using retrieval only mode.")
            llm = None
    else:
        print("No API key set. Using retrieval only mode.")
        llm = None

    if llm:
        qa_chain_en = RetrievalQA.from_chain_type(
            llm=llm, chain_type="stuff", retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT_EN},
        )
        qa_chain_hi = RetrievalQA.from_chain_type(
            llm=llm, chain_type="stuff", retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT_HI},
        )
        print(f"RAG service ready with LLM")
    else:
        # Retrieval only mode - returns raw chunks without LLM generation
        qa_chain_en = "retrieval_only"
        qa_chain_hi = "retrieval_only"
        print("RAG service ready in retrieval-only mode")

    count = vector_store._collection.count()
    print(f"Chunks indexed: {count}")


@app.get("/health")
def health():
    return {
        "status": "ok" if retriever is not None else "not_ready",
        "vector_store_ready": retriever is not None,
        "model": "gemini-1.5-flash" if (qa_chain_en and qa_chain_en != "retrieval_only") else "retrieval-only",
    }


@app.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    if retriever is None:
        raise HTTPException(status_code=503,
            detail="RAG not ready. Run ingest.py first.")

    try:
        chain = qa_chain_hi if req.language == "hi" else qa_chain_en

        if chain == "retrieval_only":
            # Return raw retrieved chunks as answer
            docs = retriever.get_relevant_documents(req.question)
            answer = "\n\n".join([doc.page_content for doc in docs[:3]])
            source_docs = docs
        else:
            result = chain.invoke({"query": req.question})
            answer = result.get("result", "").strip()
            source_docs = result.get("source_documents", [])

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

    sources = []
    seen = set()
    for doc in source_docs:
        meta = doc.metadata
        key = (meta.get("source_file", ""), meta.get("page", 0))
        if key not in seen:
            seen.add(key)
            sources.append(SourceChunk(
                content=doc.page_content[:300] + "...",
                source_file=meta.get("source_file", "Unknown"),
                page=meta.get("page", 0) + 1,
                category=meta.get("category", "General"),
            ))

    found = bool(answer) and "could not find" not in answer.lower()

    return QueryResponse(
        answer=answer,
        sources=sources,
        language=req.language,
        found=found,
        model_used="gemini-1.5-flash" if chain != "retrieval_only" else "retrieval-only",
    )


@app.get("/stats")
def stats():
    if not VECTOR_STORE_PATH.exists():
        return {"indexed": False}
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL,
                                        model_kwargs={"device": "cpu"})
    vector_store = Chroma(persist_directory=str(VECTOR_STORE_PATH),
                          embedding_function=embeddings,
                          collection_name="iocl_policies")
    count = vector_store._collection.count()
    results = vector_store._collection.get(include=["metadatas"])
    files = list({m.get("source_file", "?") for m in results["metadatas"]})
    return {"indexed": True, "total_chunks": count, "source_files": sorted(files)}


if __name__ == "__main__":
    uvicorn.run("rag_service:app", host="0.0.0.0", port=8000, reload=False)
