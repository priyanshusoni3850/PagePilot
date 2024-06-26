from flask import Flask, request, jsonify
from langchain_google_genai import GoogleGenerativeAI
from langchain.document_loaders import UnstructuredURLLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_community.vectorstores import FAISS
import pickle
import os
import logging
from flask_cors import CORS
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)  # Set log level as needed

# Define constants
STORE_PATH = "faiss_store_hf.pkl"
NAME_STORE_PATH = "names.pkl"
API_KEY = os.getenv('hf_api_key')

# Initialize GoogleGenerativeAI with your model and API key
LLM_MODEL = "models/text-bison-001"
GOOGLE_API_KEY = os.getenv('g_api_key')
llm = GoogleGenerativeAI(model=LLM_MODEL, google_api_key=GOOGLE_API_KEY)

# Function to setup and save the FAISS vector store
def setup_faiss_store(urls, api_key, store_path=STORE_PATH):
    try:
        loader = UnstructuredURLLoader(urls=urls)
        data = loader.load()
        
        if not data:
            raise ValueError("No data loaded from the URL.")
        
        logging.info(f"Loaded data from URL: {data}")

        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            is_separator_regex=False,
        )
        docs = text_splitter.split_documents(data)

        if not docs:
            raise ValueError("No documents found or empty data after splitting.")
        
        logging.info(f"Number of documents after splitting: {len(docs)}")

        hf_embeddings = HuggingFaceInferenceAPIEmbeddings(api_key=api_key)
        vectorStore_hf = FAISS.from_documents(docs, hf_embeddings)
        
        with open(store_path, "wb") as f:
            pickle.dump(vectorStore_hf, f)

        logging.info(f"FAISS vector store setup successful with {len(docs)} documents.")
    except Exception as e:
        logging.error(f"Error setting up FAISS vector store: {str(e)}")
        raise  # Re-raise the exception to propagate it to the caller

# Function to load the FAISS vector store
def load_faiss_store(store_path=STORE_PATH):
    try:
        if os.path.exists(store_path):
            with open(store_path, "rb") as f:
                return pickle.load(f)
        else:
            return None
    except Exception as e:
        logging.error(f"Error loading FAISS vector store: {str(e)}")
        return None

# Function to embed the user query and retrieve relevant documents
def get_relevant_docs(query, vector_store, embeddings):
    try:
        embedded_query = embeddings.embed_query(query)
        docs = vector_store.similarity_search_by_vector(embedded_query)
        return docs
    except Exception as e:
        logging.error(f"Error retrieving relevant documents: {str(e)}")
        raise  # Re-raise the exception to propagate it to the caller

# Endpoint to handle GET requests to root URL
@app.route("/", methods=["GET"])
def home():
    return "Page is working"

# Endpoint to handle POST requests for generating responses
@app.route("/generate_response", methods=["POST"])
def generate_response():
    try:
        data = request.get_json()

        if "query" not in data or "url" not in data:
            return jsonify({"error": "Missing 'query' or 'url' in request"}), 400

        user_query = data["query"]
        user_url = data["url"]

        # Setup FAISS vector store with new URL passed by user
        setup_faiss_store([user_url], API_KEY, STORE_PATH)

        # Load FAISS vector store
        vectorStore_hf = load_faiss_store(STORE_PATH)
        if vectorStore_hf:
            hf_embeddings = HuggingFaceInferenceAPIEmbeddings(api_key=API_KEY)
            relevant_docs = get_relevant_docs(user_query, vectorStore_hf, hf_embeddings)

            if relevant_docs:
                relevant_texts = [doc.page_content for doc in relevant_docs]  # Assuming 'page_content' attribute
                combined_text = "\n".join(relevant_texts)

                # Invoke LLM with combined context and user query
                try:
                    response = llm.invoke(combined_text + " " + user_query)
                    return jsonify({"response": response}), 200
                except Exception as e:
                    logging.error(f"Error invoking LLM: {str(e)}")
                    return jsonify({"error": str(e)}), 500
            else:
                return jsonify({"message": "No relevant documents found."}), 404
        else:
            return jsonify({"error": f"Vector store '{STORE_PATH}' not found."}), 500
    except ValueError as ve:
        logging.error(f"ValueError in generate_response: {str(ve)}")
        return jsonify({"error": str(ve)}), 500
    except Exception as ex:
        logging.error(f"Unexpected error in generate_response: {str(ex)}")
        return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500

# Endpoint to handle POST requests for saving a name
@app.route("/save_name", methods=["POST"])
def save_name():
    try:
        data = request.get_json()

        if "name" not in data:
            return jsonify({"error": "Missing 'name' in request"}), 400

        name = data["name"]

        names = []
        if os.path.exists(NAME_STORE_PATH):
            with open(NAME_STORE_PATH, "rb") as f:
                names = pickle.load(f)

        names.append(name)

        with open(NAME_STORE_PATH, "wb") as f:
            pickle.dump(names, f)

        return jsonify({"message": f"Name '{name}' saved successfully."}), 200
    except Exception as e:
        logging.error(f"Error saving name: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
