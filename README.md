# ReplyCaddy Tray
This is a RAG implementation for Front end ReactJS and Flask backend

Requirements:

- Python 3.11
- Ollama
  - llama3.1:8b
  - mxbai-embed-large
- HuggingFace
  - MBZUAI/LaMini-GPT-124M

## How it works

Basic RAG + reranker
- First it reads all of your Text and PDFs for the context. Then it saves them to Chromadb.
- websockets for the chat ui
