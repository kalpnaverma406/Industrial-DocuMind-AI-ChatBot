import os
import sys
import shutil
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "models/embedding-001")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 800))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 100))
PDF_FOLDER = Path(__file__).parent / os.getenv("PDF_FOLDER", "../PDFs")
VECTOR_STORE_PATH = Path(__file__).parent / os.getenv("VECTOR_STORE_PATH", "./vector_store")


def validate():
    errors = []
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your-gemini-api-key-here":
        errors.append("GOOGLE_API_KEY not set in RAG/.env")
    if not PDF_FOLDER.exists():
        errors.append(f"PDFs folder not found at: {PDF_FOLDER.resolve()}")
    else:
        pdfs = list(PDF_FOLDER.glob("*.pdf"))
        if not pdfs:
            errors.append(f"No PDF files in: {PDF_FOLDER.resolve()}")
    if errors:
        print("\n".join(errors))
        sys.exit(1)


def detect_category(filename):
    name = filename.lower()
    if any(kw in name for kw in ["cda", "conduct", "discipline"]):
        return "CDA Rules"
    if any(kw in name for kw in ["it", "policy", "cyber", "internet"]):
        return "IT Policy"
    return "General"


def load_pdfs(pdf_folder):
    pdf_files = sorted(pdf_folder.glob("*.pdf"))
    print(f"\nFound {len(pdf_files)} PDF file(s)")
    all_docs = []
    for pdf_path in pdf_files:
        print(f"Loading: {pdf_path.name} ...", end=" ")
        try:
            loader = PyPDFLoader(str(pdf_path))
            docs = loader.load()
            for doc in docs:
                doc.metadata["source_file"] = pdf_path.name
                doc.metadata["category"] = detect_category(pdf_path.name)
            all_docs.extend(docs)
            print(f"OK ({len(docs)} pages)")
        except Exception as e:
            print(f"Failed: {e}")
    print(f"Total pages loaded: {len(all_docs)}")
    return all_docs


def split_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )
    chunks = splitter.split_documents(docs)
    print(f"Split into {len(chunks)} chunks")
    return chunks


def build_vector_store(chunks):
    if VECTOR_STORE_PATH.exists():
        print("Clearing existing vector store ...")
        shutil.rmtree(VECTOR_STORE_PATH)

    print(f"Creating embeddings using Google Gemini ...")

    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    BATCH = 50
    vector_store = None

    for i in range(0, len(chunks), BATCH):
        batch = chunks[i: i + BATCH]
        print(f"Batch {i//BATCH + 1} ({len(batch)} chunks) ...", end=" ", flush=True)
        if vector_store is None:
            vector_store = Chroma.from_documents(
                documents=batch,
                embedding=embeddings,
                persist_directory=str(VECTOR_STORE_PATH),
                collection_name="iocl_policies",
            )
        else:
            vector_store.add_documents(batch)
        print("done")

    print(f"Vector store saved at: {VECTOR_STORE_PATH.resolve()}")
    return vector_store


def main():
    print("IOCL ChatBot - PDF Ingestion")
    print("=" * 40)
    validate()
    docs = load_pdfs(PDF_FOLDER)
    chunks = split_documents(docs)
    build_vector_store(chunks)
    print("=" * 40)
    print("Ingestion complete!")
    print("Next step: python rag_service.py")


if __name__ == "__main__":
    main()