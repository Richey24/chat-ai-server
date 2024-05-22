from flask import Flask, request
from flask_cors import CORS
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
)
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
CORS(app)
# put your open ai key
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

index = None

@app.route("/")
def hello():
    return "Hello, World!"


# upload file to local store and pass it into the index
@app.route("/upload", methods=["POST"])
def upload_file():
    global index
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        document = SimpleDirectoryReader(input_files=[file_path]).load_data()
        index = VectorStoreIndex.from_documents(document)
        return 'File successfully uploaded', 200
    

# query index using the uploaded file
@app.route("/query", methods=["POST"])
def query_index():
    global index
    data = request.get_json()
    query_text = data.get('question')
    if index is None:
        return (
            "Upload a pdf file first",
            400,
        )
    if query_text is None:
        return (
            "No text found, please include a question in the body",
            400,
        )
    query_engine = index.as_query_engine()
    response = query_engine.query(query_text)
    return str(response), 200