from ingestion.embedder import get_model
from retrieval.reranker import get_reranker
from retrieval.vectorstore import get_collection


def preload_models():
    get_model()
    get_reranker()
    get_collection()