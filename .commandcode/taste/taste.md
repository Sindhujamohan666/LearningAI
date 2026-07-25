# Taste (Continuously Learned by [CommandCode][cmd])

[cmd]: https://commandcode.ai/

# architecture
- Use Qdrant as the vector store for RAG pipelines. Confidence: 0.70
- Use BAAI/bge-m3 for embeddings and BAAI/bge-reranker-v2-m3 for reranking with BGE_USE_FP16=1. Confidence: 0.70

# llm
- Use DeepSeek (deepseek-chat) as the LLM provider via OpenAI-compatible API. Confidence: 0.65

# diagramming
- Prefers architecture and flow diagrams in valid Mermaid.js syntax. Confidence: 0.80
- Prefers polished architecture overview diagrams as self-contained HTML+SVG (JetBrains Mono, color-coded sections) over plain Mermaid renders for presentation artifacts. Confidence: 0.55
- Prefers Claude/Anthropic-inspired light cream color palette (#FAF6EF background, warm off-white cards, terracotta orange accents) for architecture diagrams. Confidence: 0.60
- Prefers self-contained HTML documentation pages for technical architecture and backend documentation (rather than markdown wikis or external doc tools). Confidence: 0.55

# git
- Uses `master` as the default branch name (not `main`). Confidence: 0.65
- Uses GitHub for remote repository hosting. Confidence: 0.55
- Expects `.env.example` files to be committed and tracked in git. Prefers narrow `.env` patterns in `.gitignore` over broad `.env.*` wildcards, so `.env.example` is naturally not ignored without needing explicit whitelist exceptions. Confidence: 0.75

# ui
- Use light mode for UI design. Confidence: 0.75

