from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS


class RAG:

    def __init__(self, file_path):
        # Textdatei laden
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()

        # Text in kleinere Teile teilen
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=50
        )

        chunks = splitter.split_text(text)

        # Gemini Embeddings
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001"
        )

        # Lokalen Vectorstore erstellen
        self.vectorstore = FAISS.from_texts(
            chunks,
            embeddings
        )

    def search(self, query):
        documents = self.vectorstore.similarity_search(
            query,
            k=3
        )

        return [doc.page_content for doc in documents]