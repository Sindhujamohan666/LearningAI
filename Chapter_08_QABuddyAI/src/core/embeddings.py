import os
from FlagEmbedding import BGEM3FlagModel
from src.core.config import get_settings

_embed_model = None
_reranker = None


def get_embedding_model() -> BGEM3FlagModel:
    global _embed_model
    if _embed_model is None:
        settings = get_settings()
        use_fp16 = os.environ.get("BGE_USE_FP16", "1") == "1"
        _embed_model = BGEM3FlagModel(
            settings.embed_model,
            use_fp16=use_fp16,
        )
    return _embed_model


def get_reranker():
    global _reranker
    if _reranker is None:
        from FlagEmbedding import FlagReranker

        settings = get_settings()
        _reranker = FlagReranker(
            settings.rerank_model,
            use_fp16=os.environ.get("BGE_USE_FP16", "1") == "1",
        )
    return _reranker


def embed_documents(texts: list[str]) -> list[list[float]]:
    model = get_embedding_model()
    output = model.encode(texts, return_dense=True, return_sparse=False)
    return output["dense_vecs"].tolist() if hasattr(output["dense_vecs"], "tolist") else [v.tolist() for v in output["dense_vecs"]]


def embed_query(text: str) -> list[float]:
    model = get_embedding_model()
    output = model.encode([text], return_dense=True, return_sparse=False)
    vecs = output["dense_vecs"]
    v = vecs[0] if hasattr(vecs, "__getitem__") and len(vecs) > 0 else vecs
    return v.tolist() if hasattr(v, "tolist") else v


def rerank(query: str, documents: list[str], top_k: int = 5) -> list[dict]:
    reranker = get_reranker()
    pairs = [[query, doc] for doc in documents]
    scores = reranker.compute_score(pairs)

    if isinstance(scores, float):
        scores = [scores]

    ranked = sorted(
        [{"doc": documents[i], "score": scores[i]} for i in range(len(documents))],
        key=lambda x: x["score"],
        reverse=True,
    )
    return ranked[:top_k]
