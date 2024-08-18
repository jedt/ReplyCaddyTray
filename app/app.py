import asyncio
import json
import toml
import ollama
import websockets
from flask import Flask, jsonify, request, send_from_directory, url_for, render_template
from flask_cors import CORS
import requests
import os
import multiprocessing


# Load the configuration file
def load_config(path_file):
    with open(path_file, 'r') as f:
        config = toml.load(f)
    return config


def get_default_toml():
    downloads_file_path = os.path.join(os.path.expanduser('~'), 'Downloads')
    documents_file_path = os.path.join(os.path.expanduser('~'), 'Documents')

    return f"""
title = "ReplyCaddy Configuration"

[folders]
downloads = "{downloads_file_path}"
documents = "{documents_file_path}"
"""


# set static folder to build
app = Flask(__name__, static_folder='build/static', template_folder='build')
# set images folder to build/images

CORS(app)

@app.route('/images/<path:path>')
def send_images(path):
    return send_from_directory('build/images', path)

@app.route("/")
def home():
    return send_from_directory('build', 'index.html')

# cors
@app.route('/api/settings', methods=['GET'])
def get_settings():
    # Load the configuration file from the Library/Application Support directory
    toml_file_path = os.path.join(os.path.expanduser('~'), 'Library/Application Support/ReplyCaddy/config.toml')
    # if the file does not exist, mkdir and create the file
    if not os.path.exists(toml_file_path):
        os.makedirs(os.path.dirname(toml_file_path), exist_ok=True)
        with open(toml_file_path, 'w') as f:
            f.write(get_default_toml())

    config = load_config(toml_file_path)
    return jsonify(config)


@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify([
        {
            "file_name": "introduction_to_llm.pdf",
            "size": 48276,
            "tags": ["LLM", "tutorial", "basics"],
            "created_at": "2024-06-01T10:00:00Z",
            "modified_at": "2024-06-05T12:00:00Z",
            "author": "Alice Johnson",
            "description": "An introductory guide to understanding Large Language Models (LLMs) and their applications."
        },
        {
            "file_name": "rag_methods_research_paper.pdf",
            "size": 112356,
            "tags": ["RAG", "research", "methods"],
            "created_at": "2024-07-10T08:30:00Z",
            "modified_at": "2024-07-12T11:45:00Z",
            "author": "Dr. Emily Clark",
            "description": "A research paper detailing the various methods of implementing Retrieval-Augmented Generation in LLMs."
        },
        {
            "file_name": "llm_training_tips.docx",
            "size": 56384,
            "tags": ["LLM", "training", "guide"],
            "created_at": "2024-05-15T14:00:00Z",
            "modified_at": "2024-05-17T16:30:00Z",
            "author": "Michael Lee",
            "description": "A comprehensive guide on best practices for training large language models."
        },
        {
            "file_name": "rag_implementation_steps.pptx",
            "size": 80304,
            "tags": ["RAG", "implementation", "steps"],
            "created_at": "2024-08-01T09:15:00Z",
            "modified_at": "2024-08-03T14:20:00Z",
            "author": "Sophia Martinez",
            "description": "Step-by-step presentation on how to implement RAG in an existing LLM framework."
        },
        {
            "file_name": "llm_and_nlp_overview.pdf",
            "size": 67329,
            "tags": ["LLM", "NLP", "overview"],
            "created_at": "2024-04-20T11:00:00Z",
            "modified_at": "2024-04-22T13:45:00Z",
            "author": "David Brown",
            "description": "An overview document discussing the intersection of LLMs and NLP techniques."
        },
        {
            "file_name": "rag_benchmark_results.xlsx",
            "size": 92356,
            "tags": ["RAG", "benchmark", "results"],
            "created_at": "2024-07-25T07:45:00Z",
            "modified_at": "2024-07-27T09:50:00Z",
            "author": "Research Team",
            "description": "Excel sheet containing benchmark results for various RAG implementations."
        },
        {
            "file_name": "rag_training_data.json",
            "size": 154763,
            "tags": ["RAG", "training", "data"],
            "created_at": "2024-05-05T12:00:00Z",
            "modified_at": "2024-05-06T14:30:00Z",
            "author": "Training Data Team",
            "description": "Sample JSON file containing training data used for RAG."
        },
        {
            "file_name": "llm_security_considerations.pdf",
            "size": 49384,
            "tags": ["LLM", "security", "considerations"],
            "created_at": "2024-06-18T13:20:00Z",
            "modified_at": "2024-06-20T15:10:00Z",
            "author": "Karen Green",
            "description": "A document outlining the security considerations when deploying LLMs in production environments."
        },
        {
            "file_name": "rag_architecture_diagram.png",
            "size": 24321,
            "tags": ["RAG", "architecture", "diagram"],
            "created_at": "2024-08-02T10:30:00Z",
            "modified_at": "2024-08-03T12:40:00Z",
            "author": "Design Team",
            "description": "A high-level architecture diagram illustrating the components of a RAG system."
        },
        {
            "file_name": "llm_faq.docx",
            "size": 38476,
            "tags": ["LLM", "FAQ", "documentation"],
            "created_at": "2024-07-01T14:00:00Z",
            "modified_at": "2024-07-02T16:00:00Z",
            "author": "Support Team",
            "description": "Frequently asked questions and answers related to LLMs and their usage."
        }
    ])


# WebSocket setup
clients = set()

async def echo(websocket):
    start_of_response = {
        "id": "start_of_response"
    }

    chunk_response = {
        "id": "chunk_response",
        "content": ""
    }

    end_of_response = {
        "id": "end_of_response"
    }

    async for message in websocket:
        # send the start of response message
        # {promptText, messageHistoryID}
        print(message)
        json_dict = json.loads(message)
        await websocket.send(json.dumps(start_of_response))
        stream = ollama.chat(
            model='llama3.1:8b',
            messages=[{'role': 'user', 'content': json_dict['promptText']}],
            stream=True,
        )

        for chunk in stream:
            await websocket.send(json.dumps({
                "id": "chunk_response",
                "content": chunk['message']['content']
            }))

        await websocket.send(json.dumps(end_of_response))

async def start_websocket_server():
    async with websockets.serve(echo, "localhost", 8765):
        await asyncio.Future()  # Run forever

def run_flask():
    app.run(debug=True, port=8971, use_reloader=False)


if __name__ == '__main__':
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
