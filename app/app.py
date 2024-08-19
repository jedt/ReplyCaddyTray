import asyncio
import json
import fitz
import numpy as np
import toml
import ollama
import websockets
from sentence_transformers import SentenceTransformer
from flask import Flask, jsonify, request, send_from_directory, url_for, render_template
from flask_cors import CORS
import requests
import os
import sqlite3
import chromadb
import multiprocessing
import argparse
import datetime
from tqdm import trange, tqdm
import faiss
import mimetypes

# Load model directly
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch


def calculate_perplexity(text):
    if text == "":
        return 0

    # Load model directly
    tokenizer = AutoTokenizer.from_pretrained("MBZUAI/LaMini-GPT-124M")
    model = AutoModelForCausalLM.from_pretrained("MBZUAI/LaMini-GPT-124M")
    # Tokenize the input text and create input IDs
    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    input_ids = inputs["input_ids"]

    # Shift the inputs for the labels (since it's a language model)
    labels = input_ids.clone()

    # Calculate the loss
    with torch.no_grad():
        outputs = model(input_ids, labels=labels)
        loss = outputs.loss

    # Calculate perplexity
    perplexity = torch.exp(loss).item()

    # normalize perplexity
    normalized = (perplexity - 1) / 100

    return normalized


# Load the configuration file
def get_foo():
    file_path = "~/Downloads/essay.txt"
    with open(os.path.expanduser(file_path), "r") as f:
        text = f.read()
        f.close()

    # chunk_size = 2048
    chunk_size = 512
    overlap = 128
    chunks = [
        text[i : i + chunk_size] for i in range(0, len(text), chunk_size - overlap)
    ]

    print("Total:", len(chunks))
    text_embeddings = np.array(
        [get_sample_rag_text_embedding(chunk) for chunk in chunks]
    )

    question = "Where did the author go to college?"
    # question = "What were the two main things the author worked on before college?"
    # question = "What happened on the night of October, 2003?"
    question_embeddings = np.array([get_sample_rag_text_embedding(question)])
    d = text_embeddings.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(text_embeddings)
    D, I = index.search(question_embeddings, k=5)
    retrieved_chunks = [chunks[i] for i in I.tolist()[0]]

    context = ""
    for i, chunk in enumerate(retrieved_chunks):
        print("\n===> chunk no. ", i)
        print(chunk)
        context += f"{chunk}\n"

    prompt_with_context = f"""
You are a super helpful AI assistant. You are asked to answer a question based on the following context information.
Ensure to answer the Query beginning with the sentence 
"First, here is the most relevant sentence in the context information:"
Context information are the following text chunks:
---------------------
{context}
---------------------
Given the context information and not prior knowledge, Ensure to answer the query.
Query: {question}
Answer:
"""
    print("\n[prompt_with_context]", prompt_with_context)
    stream = ollama.chat(
        model="llama3.1:8b",
        options={"temperature": 0},
        messages=[
            {
                "role": "system",
                "content": "You are a super helpful helper",
            },
            {"role": "user", "content": prompt_with_context},
        ],
        stream=True,
    )

    for item in stream:
        print(item["message"]["content"], end="", flush=True)

    exit(0)


def load_config(path_file):
    with open(path_file, "r") as f:
        config = toml.load(f)
    return config


def get_default_toml():
    downloads_file_path = os.path.join(os.path.expanduser("~"), "Downloads")
    documents_file_path = os.path.join(os.path.expanduser("~"), "Documents")

    return f"""
title = "ReplyCaddy Configuration"

[settings]
chunk_size = 512
overlap = 128
db_name = "local_docs.db"
chunks_db_name = "chroma.db"

[folders]
downloads = "{downloads_file_path}"
documents = "{documents_file_path}"
"""


# set static folder to build
app = Flask(__name__, static_folder="build/static", template_folder="build")
# set images folder to build/images

CORS(app)


@app.route("/images/<path:path>")
def send_images(path):
    return send_from_directory("build/images", path)


@app.route("/")
def home():
    return send_from_directory("build", "index.html")


# cors
@app.route("/api/settings", methods=["GET"])
def get_settings():
    # Load the configuration file from the Library/Application Support directory
    toml_file_path = os.path.join(
        os.path.expanduser("~"), "Library/Application Support/ReplyCaddy/config.toml"
    )
    # if the file does not exist, mkdir and create the file
    if not os.path.exists(toml_file_path):
        os.makedirs(os.path.dirname(toml_file_path), exist_ok=True)
        with open(toml_file_path, "w") as f:
            f.write(get_default_toml())

    config = load_config(toml_file_path)
    return jsonify(config)


@app.route("/api/data", methods=["GET"])
def get_data():
    # Load the configuration file from the Library/Application Support directory
    toml_file_path = os.path.join(
        os.path.expanduser("~"), "Library/Application Support/ReplyCaddy/config.toml"
    )
    config = load_config(toml_file_path)
    db_name = config["settings"]["db_name"]
    local_db_file_path = os.path.join(get_local_db_dir_path(), db_name)

    conn = sqlite3.connect(local_db_file_path)
    cursor = conn.cursor()
    # use page number to get the data
    cursor.execute("SELECT * FROM documents")
    documents = cursor.fetchall()
    conn.close()
    return jsonify(documents)


# WebSocket setup
clients = set()


async def echo(websocket):
    start_of_response = {"id": "start_of_response"}

    chunk_response = {"id": "chunk_response", "content": ""}

    end_of_response = {"id": "end_of_response"}

    async for message in websocket:
        # send the start of response message
        # {promptText, messageHistoryID}
        json_dict = json.loads(message)
        await websocket.send(json.dumps(start_of_response))
        prompt_with_rag = get_rag_prompt_on_sqlite_chunks_table(json_dict["promptText"])

        stream = ollama.chat(
            model="llama3.1:8b",
            messages=[{"role": "user", "content": prompt_with_rag}],
            stream=True,
        )

        for chunk in stream:
            await websocket.send(
                json.dumps(
                    {"id": "chunk_response", "content": chunk["message"]["content"]}
                )
            )

        await websocket.send(json.dumps(end_of_response))


async def start_websocket_server():
    async with websockets.serve(echo, "localhost", 8765):
        await asyncio.Future()  # Run forever


def run_flask():
    app.run(debug=True, port=8971, use_reloader=False)


def check_if_table_exists(table_name, local_db_file_path):
    conn = sqlite3.connect(local_db_file_path)
    c = conn.cursor()
    c.execute(
        f"""
        SELECT count(name) 
        FROM sqlite_master 
        WHERE type='table' AND name='{table_name}'
        """
    )
    if c.fetchone()[0] == 1:
        conn.close()
        return True

    conn.close()
    return False


def extract_text_from_pdf(pdf_file_path):
    text = ""
    with fitz.open(pdf_file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text


def save_text_to_db(
    file_path, file_name, file_type, source, length, text, local_db_file_path
):

    conn = sqlite3.connect(local_db_file_path)
    cursor = conn.cursor()

    time_now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    cursor.execute(
        """
        INSERT INTO documents (file_path, file_name, type, extension, size, created_at, modified_at, content)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (file_path, file_name, file_type, source, length, time_now, time_now, text),
    )

    conn.commit()
    conn.close()


def is_binary(file_path):
    mime = mimetypes.guess_type(file_path)[0]
    return mime is None or "text" not in mime


def extract_text_from_all_pdfs_with_folders(toml_file_path, local_db_file_path):
    config = load_config(toml_file_path)
    folders = config["folders"]
    extract_folders = [folders["downloads"], folders["documents"]]
    for folder in extract_folders:
        for root, dirs, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith(".txt"):
                    if is_binary(file_path):
                        continue  # skip binary files or handle them differently
                    # safe read the text file avoid UnicodeDecodeError
                    with open(
                        file_path,
                        "r",
                        encoding="mac_roman",
                        errors="ignore",
                    ) as f:
                        text = f.read()
                        # save the text to the local SQLite database
                        save_text_to_db(
                            file_path,
                            file,
                            "txt",
                            "txt",
                            len(text),
                            text,
                            local_db_file_path,
                        )
                elif file.endswith(".pdf"):
                    # extract text from the pdf file
                    text = extract_text_from_pdf(file_path)
                    # save the text to the local SQLite database
                    save_text_to_db(
                        file_path,
                        file,
                        "pdf",
                        "pdf",
                        len(text),
                        text,
                        local_db_file_path,
                    )


def get_local_db_dir_path():
    parent_db_file_path = os.path.join(
        os.path.expanduser("~"),
        "Library/Application Support/ReplyCaddy/",
    )

    database_folder_name = "db"
    local_db_dir_file_path = os.path.join(parent_db_file_path, database_folder_name)
    return local_db_dir_file_path


def build_local_docs_db(db_name):
    local_db_file_path = get_local_db_dir_path()
    if not os.path.exists(local_db_file_path):
        os.makedirs(local_db_file_path, exist_ok=True)

    local_db_file_path = os.path.join(local_db_file_path, db_name)
    if os.path.exists(local_db_file_path):
        pass

    # Create the local SQLite database with table schema
    # schema for documents table
    # id, file_name, type,  extension, size, created_at, modified_at, content
    conn = sqlite3.connect(local_db_file_path)
    # if the table already exists, skip the creation
    if not check_if_table_exists("documents", local_db_file_path):
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                file_name TEXT NOT NULL,
                type TEXT NOT NULL,
                extension TEXT NOT NULL,
                size INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                modified_at TEXT NOT NULL,
                content TEXT NOT NULL
            )
            """
        )
        conn.commit()
        conn.close()

    # read the config toml file
    toml_file_path = os.path.join(
        os.path.expanduser("~"), "Library/Application Support/ReplyCaddy/config.toml"
    )

    extract_text_from_all_pdfs_with_folders(toml_file_path, local_db_file_path)


def create_chunks_persistent_store_if_not_exists(
    local_db_folder, name="document_chunks"
):

    client = chromadb.PersistentClient(path=local_db_folder)
    return client.get_or_create_collection(name=name)


def delete_chromadb_chunk_collection():
    toml_file_path = os.path.join(
        os.path.expanduser("~"), "Library/Application Support/ReplyCaddy/config.toml"
    )
    client = chromadb.PersistentClient(path=get_local_db_dir_path())
    try:
        client.delete_collection("document_chunks")
    except:
        pass


def save_chunks_to_chroma_db():

    toml_file_path = os.path.join(
        os.path.expanduser("~"), "Library/Application Support/ReplyCaddy/config.toml"
    )
    config = load_config(toml_file_path)
    local_db_file_path = os.path.join(
        get_local_db_dir_path(), config["settings"]["db_name"]
    )
    chunk_size = config["settings"]["chunk_size"]
    overlap = config["settings"]["overlap"]

    collection = create_chunks_persistent_store_if_not_exists(get_local_db_dir_path())

    conn = sqlite3.connect(local_db_file_path)

    cursor = conn.cursor()
    # query all documents
    cursor.execute("SELECT * FROM documents")
    documents = cursor.fetchall()
    total_documents = len(documents)
    # print("total_documents", total_documents)
    # document_counter = 0
    for (
        document_id,
        file_path,
        file_name,
        type,
        extension,
        size,
        created_at,
        modified_at,
        text,
    ) in documents:
        # split text into chunks with overlap
        chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

        tdqm_chunks = tqdm(chunks, desc=f"{file_name} {document_id}/{total_documents}")
        for i, d in enumerate(tdqm_chunks):
            if calculate_perplexity(d) < 0.1:
                print(f"Perplexity is too low for chunk {i} in document {file_name}")
                continue

            collection.add(
                documents=[d],
                embeddings=[get_text_embedding_dim(d)],
                metadatas=[{"document_id": f"{document_id}"}],
                ids=[f"{document_id}_{i}"],
            )


def get_text_embedding_dim(input) -> list:
    result = ollama.embeddings(model="mxbai-embed-large", prompt=input)
    return result["embedding"]


def get_rag_prompt_on_sqlite_chunks_table(question, file_name):
    # Load configuration
    toml_file_path = os.path.join(
        os.path.expanduser("~"), "Library/Application Support/ReplyCaddy/config.toml"
    )
    config = load_config(toml_file_path)
    db_name = config["settings"]["db_name"]
    client = chromadb.PersistentClient(path=get_local_db_dir_path())
    collection = client.get_collection("document_chunks")
    print("collection", collection)

    # retrieve the document chunks
    retrieved_chunks = collection.query(
        query_texts=[question],
        n_results=2,
    )

    # Build the context from the retrieved chunks
    context = "\n".join(retrieved_chunks)

    # Construct the prompt
    prompt = f"""
You are a super helpful AI assistant. You are asked to answer a question based on the following context information.
Ensure to answer the Query beginning with the sentence "First, here is the most relevant sentence in the context information:"
Context information are the following text chunks:
---------------------
{context}
---------------------
Given the context information and not prior knowledge, Ensure to answer the query.
Query: {question}
Answer:
"""

    return prompt


def rerank_documents(question, documents):
    model = SentenceTransformer("BAAI/bge-reranker-base")
    question_embedding = model.encode(question)
    document_embeddings = model.encode(documents)
    # rerank the documents based on the similarity with the question
    scores = np.dot(document_embeddings, question_embedding)
    sorted_indices = np.argsort(scores)[::-1]
    return [documents[i] for i in sorted_indices]


# examples
# app.py --run-server --port 8971
# app.py --rebuild-local-docs local_docs.db
# app.py --delete-chunks
# app.py --save-chunks
# app.py --prompt-ollama "What is the capital of France?"
# app.py --help
def parse_args():
    parser = argparse.ArgumentParser(description="ReplyCaddy")
    parser.add_argument(
        "--run-server", action="store_true", help="Run the Flask server"
    )
    parser.add_argument(
        "--port", type=int, default=8971, help="Port number for the Flask server"
    )

    parser.add_argument(
        "--delete-chunks",
        action="store_true",
        help="Delete the chunks of the documents saved to the local SQLite database",
    )

    parser.add_argument(
        "--rebuild-local-docs",
        type=str,
        help="Rebuild the local SQLite database with the specified name ex. --rebuild-local-docs local_docs.db",
    )

    parser.add_argument(
        "--save-chunks",
        action="store_true",
        help="Save the chunks of the documents saved to the local SQLite database",
    )

    parser.add_argument(
        "--prompt-ollama",
        type=str,
        help="Prompt the Ollama model with your documents",
    )

    return parser.parse_args()


def get_sample_rag_text_embedding(input):
    result = ollama.embeddings(
        model="mxbai-embed-large",
        prompt=f"Represent this sentence for searching relevant passages: {input}",
    )

    if isinstance(result, dict):
        return np.array(result["embedding"])

    return np.array(result)


if __name__ == "__main__":
    args = parse_args()
    if args.rebuild_local_docs:
        # Rebuild the local SQLite database
        build_local_docs_db(args.rebuild_local_docs)
        exit(0)

    if args.delete_chunks:
        delete_chromadb_chunk_collection()
        exit(0)

    if args.save_chunks:
        # Save the chunks of the documents saved to the local SQLite database
        # delete_chromadb_chunk_collection()
        save_chunks_to_chroma_db()
        exit(0)

    if args.prompt_ollama:
        question = args.prompt_ollama

        response = ollama.embeddings(prompt=question, model="mxbai-embed-large")
        client = chromadb.PersistentClient(path=get_local_db_dir_path())

        collection = create_chunks_persistent_store_if_not_exists(
            get_local_db_dir_path()
        )

        results = collection.query(
            query_embeddings=[response["embedding"]], n_results=4
        )

        documents = results["documents"][0]
        context = ""

        documents = rerank_documents(question, documents)
        print("reranked documents", documents)

        for i, d in enumerate(documents):
            context += f"{d}\n"

        prompt_with_context = f"""
You are a super helpful AI assistant. You are asked to answer a question based on the following context information.
Ensure to answer the Query beginning with the sentence 
"First, here is the most relevant sentence in the context information:"
Context information are the following text chunks:
---------------------
{context}
---------------------
Given the context information and not prior knowledge, Ensure to answer the query.
Query: {question}
Answer:
"""

        #  print("\n[prompt_with_context]", prompt_with_context)

        # stream = ollama.chat(
        #     model="llama3.1:8b",
        #     options={"temperature": 0},
        #     messages=[
        #         {
        #             "role": "system",
        #             "content": "You are a super helpful helper",
        #         },
        #         {"role": "user", "content": prompt},
        #     ],
        #     stream=True,
        # )
        #
        # for item in stream:
        #     print(item["message"]["content"], end="", flush=True)

        exit(0)

    if args.run_server:
        # Run Flask server in a separate process
        # enable debug mode to auto-reload the server when changes are made
        flask_process = multiprocessing.Process(target=run_flask)
        flask_process.start()

        try:
            asyncio.run(start_websocket_server())
        except KeyboardInterrupt:
            pass
        finally:
            # Terminate the Flask process when exiting
            flask_process.terminate()
            flask_process.join()
    else:
        print("Please specify an action. Use --help for more information.")
        exit(1)
