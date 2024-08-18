import asyncio
import json
import fitz
import numpy as np
import toml
import ollama
import websockets
from flask import Flask, jsonify, request, send_from_directory, url_for, render_template
from flask_cors import CORS
import requests
import os
import sqlite3
import multiprocessing
import argparse
import datetime
from tqdm import trange, tqdm
import faiss
import mimetypes


# Load the configuration file
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
        print(message)
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
    """
    Extract text from a PDF file.

    Parameters:
        pdf_file_path (str): Path to the PDF file.

    Returns:
        str: Extracted text from the PDF file.
    """
    text = ""
    with fitz.open(pdf_file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text


def save_text_to_db(file_name, file_type, source, length, text, local_db_file_path):
    """
    Save extracted text and metadata to the SQLite database.

    Parameters:
        file_name (str): Name of the file.
        file_type (str): Type of the file (e.g., "pdf").
        source (str): Source of the file (e.g., "downloads", "documents").
        length (int): Length of the extracted text.
        text (str): The extracted text content.

    the table schema for documents table
        CREATE TABLE documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT NOT NULL,
            type TEXT NOT NULL,
            extension TEXT NOT NULL,
            size INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            modified_at TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """

    conn = sqlite3.connect(local_db_file_path)
    cursor = conn.cursor()

    time_now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    cursor.execute(
        """
        INSERT INTO documents (file_name, type, extension, size, created_at, modified_at, content)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (file_name, file_type, source, length, time_now, time_now, text),
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
                            file_path, "txt", "txt", len(text), text, local_db_file_path
                        )
                elif file.endswith(".pdf"):
                    pass
                    # extract text from the pdf file
                    # text = extract_text_from_pdf(file_path)
                    # # save the text to the local SQLite database
                    # save_text_to_db(
                    #     file, "pdf", "pdf", len(text), text, local_db_file_path
                    # )


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


def create_chunks_table_if_not_exists(local_db_file_path):
    conn = sqlite3.connect(local_db_file_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chunk_order INTEGER NOT NULL,
            chunk_text TEXT NOT NULL,
            chunk_embedding BLOB,
            parent_document_id INTEGER NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def drop_chunks_table_if_exists():
    toml_file_path = os.path.join(
        os.path.expanduser("~"), "Library/Application Support/ReplyCaddy/config.toml"
    )
    config = load_config(toml_file_path)
    db_name = config["settings"]["db_name"]
    local_db_file_path = os.path.join(get_local_db_dir_path(), db_name)
    conn = sqlite3.connect(local_db_file_path)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS chunks")
    conn.commit()


def save_chunks_to_db():
    toml_file_path = os.path.join(
        os.path.expanduser("~"), "Library/Application Support/ReplyCaddy/config.toml"
    )
    config = load_config(toml_file_path)
    db_name = config["settings"]["db_name"]
    chunk_size = config["settings"]["chunk_size"]
    overlap = config["settings"]["overlap"]
    local_db_file_path = os.path.join(get_local_db_dir_path(), db_name)
    create_chunks_table_if_not_exists(local_db_file_path)

    conn = sqlite3.connect(local_db_file_path)

    cursor = conn.cursor()
    # query all documents
    cursor.execute("SELECT * FROM documents")
    documents = cursor.fetchall()
    total_documents = len(documents)

    document_counter = 0
    for (
        id,
        file_name,
        type,
        extension,
        size,
        created_at,
        modified_at,
        text,
    ) in documents:
        document_counter += 1
        # extract chunks from the document content
        # chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size-overlap)]

        # content field is the 8th field
        chunks = [
            text[i : i + chunk_size] for i in range(0, len(text), chunk_size - overlap)
        ]
        # Insert each chunk into the database
        total_chunks = len(chunks)
        # use tqdm for progress bar
        # use tqdm for progress bar with dynamic description
        for i, chunk in enumerate(
            tqdm(
                chunks,
                total=total_chunks,
                desc=f"Processing {file_name} [{document_counter}/{total_documents}]",
                ascii="░▒",
            )
        ):
            text_embeddings = np.array(get_text_embedding(chunk))
            cursor.execute(
                """
                INSERT INTO chunks (chunk_order, chunk_text, chunk_embedding, parent_document_id)
                VALUES (?, ?, ?, ?)
                """,
                (i, chunk, text_embeddings.tobytes(), id),
            )

            conn.commit()


def get_text_embedding(input):
    result = ollama.embeddings(
        model="mxbai-embed-large",
        prompt=f"Represent this sentence for searching relevant passages: {input}",
    )

    if isinstance(result, dict):
        embedding = np.array(result["embedding"])
    else:
        embedding = np.array(result)

    target_dim = 8192
    if embedding.shape[0] < target_dim:
        # Pad with zeros
        embedding = np.pad(embedding, (0, target_dim - embedding.shape[0]), "constant")
    elif embedding.shape[0] > target_dim:
        # Trim to target dimension
        embedding = embedding[:target_dim]

    return embedding


def get_rag_prompt_on_sqlite_chunks_table(question, file_name):
    # Load configuration
    toml_file_path = os.path.join(
        os.path.expanduser("~"), "Library/Application Support/ReplyCaddy/config.toml"
    )
    config = load_config(toml_file_path)
    db_name = config["settings"]["db_name"]
    local_db_file_path = os.path.join(get_local_db_dir_path(), db_name)

    # Connect to the SQLite database
    conn = sqlite3.connect(local_db_file_path)
    cursor = conn.cursor()

    # Retrieve the document ID from the database
    cursor.execute("SELECT id FROM documents WHERE file_name=?", (file_name,))
    document_id = cursor.fetchone()[0]

    # Retrieve all chunks and their embeddings from the database
    cursor.execute("SELECT * FROM chunks WHERE parent_document_id=?", (document_id,))
    chunks = cursor.fetchall()
    print(f"Total chunks: {len(chunks)}")

    # Extract chunk embeddings
    chunk_embeddings = np.array(
        [np.frombuffer(chunk[3], dtype=np.float32) for chunk in chunks]
    )

    # Chunk embeddings shape: (57630, 4096)
    print(f"Chunk embeddings shape: {chunk_embeddings.shape}")
    print(f"Chunk embeddings dtype: {chunk_embeddings.dtype}")

    # Build the FAISS index
    # Create a FAISS Index and Add the Chunk Embeddings:
    # A FAISS index is created using the embeddings, which will be used for similarity search.
    index = faiss.IndexFlatIP(chunk_embeddings.shape[1])
    index.add(chunk_embeddings)

    # Get the embedding for the question
    question_embedding = (
        np.array(get_text_embedding(question)).astype("float32").reshape(1, -1)
    )

    print(f"Question embedding shape: {question_embedding.shape}")

    # Ensure dimensions match before performing the search
    assert (
        question_embedding.shape[1] == chunk_embeddings.shape[1]
    ), f"Dimension mismatch: question embedding {question_embedding.shape[1]} vs chunk embeddings {chunk_embeddings.shape[1]}"

    # Perform the FAISS Search:
    # The FAISS index is queried with the question embedding to retrieve the most similar text chunks.
    distances, indices = index.search(question_embedding, k=5)

    # Gather the most relevant chunks
    retrieved_chunks = [
        chunks[i][2] for i in indices[0]
    ]  # [2] is assumed to be the chunk text field

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


# examples
# app.py --run-server --port 8971
# app.py --rebuild-local-docs local_docs.db
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
        "--sample-rag",
        action="store_true",
        help="Sample RAG",
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
    # if result is a dict
    # as np.array
    if isinstance(result, dict):
        return np.array(result["embedding"])

    return np.array(result)


if __name__ == "__main__":
    args = parse_args()
    if args.rebuild_local_docs:
        # Rebuild the local SQLite database
        build_local_docs_db(args.rebuild_local_docs)
        exit(0)

    if args.save_chunks:
        # Save the chunks of the documents saved to the local SQLite database
        drop_chunks_table_if_exists()
        save_chunks_to_db()
        exit(0)

    if args.sample_rag:
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

    if args.prompt_ollama:
        # Prompt the Ollama model with the specified text

        prompt_with_rag = get_rag_prompt_on_sqlite_chunks_table(
            args.prompt_ollama,
            "essay.txt",
        )
        stream = ollama.chat(
            model="llama3.1:8b",
            options={"temperature": 0},
            messages=[
                {
                    "role": "system",
                    "content": "You are a super helpful helper",
                },
                {"role": "user", "content": prompt_with_rag},
            ],
            stream=True,
        )

        for item in stream:
            print(item["message"]["content"], end="", flush=True)

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
