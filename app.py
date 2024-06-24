import pickle
import os
from flask import Flask, request, jsonify
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain.document_loaders import UnstructuredURLLoader
from github import Github
from dotenv import load_dotenv
import base64

app = Flask(__name__)
load_dotenv()

# GitHub setup
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPO = os.getenv('GITHUB_REPO')
FAISS_INDEX_FILE = 'faiss_store_hf.pkl'

# Initialize GitHub client
g = Github(GITHUB_TOKEN)
repo = g.get_repo(GITHUB_REPO)

# Function to upload the FAISS index to GitHub
def upload_to_github(filename):
    try:
        # Try to get the file to check if it exists
        file = repo.get_contents(filename)
        sha = file.sha
        # Update the existing file
        with open(filename, "rb") as f:
            content = f.read()
        content_b64 = base64.b64encode(content).decode('utf-8')
        repo.update_file(filename, "Update FAISS index", content_b64, sha)
    except:
        # If the file does not exist, create it
        with open(filename, "rb") as f:
            content = f.read()
        content_b64 = base64.b64encode(content).decode('utf-8')
        repo.create_file(filename, "Add FAISS index", content_b64)

# Function to download the FAISS index from GitHub
def download_from_github(filename):
    file = repo.get_contents(filename)
    content_b64 = file.content
    content = base64.b64decode(content_b64)
    with open(filename, "wb") as f:
        f.write(content)

# Function to setup and save the FAISS vector store
def setup_faiss_store(urls, api_key, filename):
    loader = UnstructuredURLLoader(urls=urls)
    data = loader.load()

    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    docs = text_splitter.split_documents(data)
    hf_embeddings = HuggingFaceInferenceAPIEmbeddings(api_key=api_key)
    vectorStore_hf = FAISS.from_documents(docs, hf_embeddings)

    with open(filename, "wb") as f:
        pickle.dump(vectorStore_hf, f)

    upload_to_github(filename)

# Function to load the FAISS vector store
def load_faiss_store(filename):
    download_from_github(filename)
    with open(filename, "rb") as f:
        return pickle.load(f)

# Function to embed the user query and retrieve relevant documents
def get_relevant_docs(query, vector_store, embeddings):
    embedded_query = embeddings.embed_query(query)
    docs = vector_store.similarity_search_by_vector(embedded_query)
    return docs

# Endpoint to handle GET requests to root URL
@app.route("/", methods=["GET"])
def home():
    return "Page is working"

# Endpoint to handle POST requests
@app.route("/generate_response", methods=["POST"])
def generate_response():
    data = request.get_json()

    if "query" not in data or "url" not in data:
        return jsonify({"error": "Missing 'query' or 'url' in request"}), 400

    user_query = data["query"]
    user_url = data["url"]

    # Setup FAISS vector store with new URL passed by user
    setup_faiss_store([user_url], os.getenv('hf_api_key'), FAISS_INDEX_FILE)

    # Load FAISS vector store
    vectorStore_hf = load_faiss_store(FAISS_INDEX_FILE)

    # Process relevant documents with LLM if vector store exists
    if vectorStore_hf:
        hf_embeddings = HuggingFaceInferenceAPIEmbeddings(api_key=os.getenv('hf_api_key'))
        relevant_docs = get_relevant_docs(user_query, vectorStore_hf, hf_embeddings)

        if relevant_docs:
            relevant_texts = [doc.page_content for doc in relevant_docs]  # Assuming 'page_content' attribute
            combined_text = "\n".join(relevant_texts)

            # Initialize GoogleGenerativeAI with your model and API key
            llm = GoogleGenerativeAI(model="models/text-bison-001", google_api_key=os.getenv('g_api_key'))
            response = llm.invoke(combined_text + " " + user_query)

            return jsonify({"response": response}), 200
        else:
            return jsonify({"message": "No relevant documents found."}), 404
    else:
        return jsonify({"error": "Failed to load FAISS vector store from GitHub"}), 500

if __name__ == "__main__":
    app.run(debug=True)
