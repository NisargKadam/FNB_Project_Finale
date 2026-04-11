import chromadb
from chromadb.config import Settings
import PyPDF2
from sentence_transformers import SentenceTransformer


class ChromaStore:

    def __init__(self):
        # -------------------------
        # Chroma DB
        # -------------------------
        self.chroma = chromadb.Client(
            Settings(persist_directory="./chroma_db")
        )

        self.collection = self.chroma.get_or_create_collection(
            name="cuisine_books"
        )

        # -------------------------
        # HuggingFace Embeddings
        # -------------------------
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    # =========================
    # EMBEDDING FUNCTION (HF)
    # =========================
    def embed(self, text: str):
        return self.model.encode(text).tolist()

    # =========================
    # PDF EXTRACTION
    # =========================
    def extract_pdf(self, pdf_path: str) -> str:
        text = ""

        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)

            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        return text

    # =========================
    # CHUNK TEXT
    # =========================
    def chunk_text(self, text: str, chunk_size: int = 800):
        words = text.split()

        for i in range(0, len(words), chunk_size):
            yield " ".join(words[i:i + chunk_size])

    # =========================
    # INGEST PDF
    # =========================
    def add_pdf(self, pdf_path: str):

        text = self.extract_pdf(pdf_path)
        chunks = list(self.chunk_text(text))

        for i, chunk in enumerate(chunks):

            self.collection.add(
                documents=[chunk],
                embeddings=[self.embed(chunk)],
                ids=[f"{pdf_path}_{i}"],
                metadatas=[
                    {
                        "source": pdf_path,
                        "chunk": i
                    }
                ]
            )

        print(f"[CHROMA] Indexed PDF: {pdf_path} | chunks={len(chunks)}")

    # =========================
    # SEARCH
    # =========================
    def search(self, query: str, top_k: int = 5):

        results = self.collection.query(
            query_embeddings=[self.embed(query)],
            n_results=top_k
        )

        return results["documents"][0]