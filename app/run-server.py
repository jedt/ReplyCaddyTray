from flask import Flask, jsonify, request, send_from_directory, url_for, render_template
from flask_cors import CORS
import requests
import os
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
    # query = request.args.get('query', 'cats')  # Default to 'nature' if no query provided
    # url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={query}&image_type=photo"
    # response = requests.get(url)
    #
    # if response.status_code == 200:
    #     return jsonify(response.json())
    # else:
    #     return jsonify({"error": "Unable to fetch data from Pixabay"}), response.status_code

if __name__ == '__main__':
    app.run(debug=True, port=8971)
