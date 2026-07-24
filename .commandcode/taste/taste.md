# Taste (Continuously Learned by [CommandCode][cmd])

[cmd]: https://commandcode.ai/

# architecture
- Use Qdrant as the vector store for RAG pipelines. Confidence: 0.70
- Use BAAI/bge-m3 for embeddings and BAAI/bge-reranker-v2-m3 for reranking with BGE_USE_FP16=1. Confidence: 0.70

# llm
- Use DeepSeek (deepseek-chat) as the LLM provider via OpenAI-compatible API. Confidence: 0.65

# ui
- Use light mode for UI design. Confidence: 0.65

