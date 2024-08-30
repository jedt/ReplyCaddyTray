[test-recording.webm](https://github.com/user-attachments/assets/f0131324-fcb1-4641-9dc9-3fa3b487e3a9)

# ReplyCaddy Tray
This is a RAG implementation for Front end ReactJS and Flask backend

Requirements:
- MacOS
- Python 3.11
- Ollama
  - llama3.1:8b
  - mxbai-embed-large
- HuggingFace
  - MBZUAI/LaMini-GPT-124M (for perplexity)

## How it works

Basic RAG + reranker
- First, it reads your text and PDF files inside your Downloads and Documents for context. Then it saves them to Chromadb.
- During ETL, the app will check any tokens that exceeded 0.3 of normalized perplexity
  - `normalized = (perplexity - 1) / 100`
  - This will help ignore noise. Text from log dumps and unreadable sections of pdf files. These happen to generate spam in the retrieval process because they always appear in the results. Like when we enter a query on google and all it returns are spam websites.
- Then we chunk the data into 512 tokens with an overlap of 128
- websockets for the chat ui
