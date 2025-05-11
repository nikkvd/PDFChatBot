# Import Libraries
from flask import Flask,request,render_template,jsonify,url_for,redirect
from functions import extract_text_from_pdf,chunk_text,create_vector_db,retrieve_chunks,generate_response
from werkzeug.utils import secure_filename
import json
from datetime import datetime
import os
import logging

# Set up logging to debug issues
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
RECENT_CHATS_FOLDER = 'recent_chats'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RECENT_CHATS_FOLDER'] = RECENT_CHATS_FOLDER
ALLOWED_EXTENSIONS = {'pdf'}

# Ensure upload folder and recent chats folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RECENT_CHATS_FOLDER, exist_ok=True)
# Global variables to store vector database, embedder, and recent chats
index = None
chunks = None
embedder = None
recent_chats = [] # Store the recent chats
current_filename = None  # Store the current PDF filename


# Function to check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to clear existing PDFs in the uploads folder
def clear_uploads_folder():
    logger.debug(f"Clearing existing PDFs in {UPLOAD_FOLDER}")
    try:
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(file_path) and allowed_file(filename):
                os.remove(file_path)
                logger.debug(f"Deleted file: {file_path}")
    except Exception as e:
        logger.error(f"Error clearing uploads folder: {e}")
        raise


# Route for the main page
@app.route('/', methods=['GET', 'POST'])
def index():
    global index, chunks, embedder, recent_chats, current_filename
    error = None
    message = request.args.get('message')
    show_chat = message == 'success'
    
    # Handle invalid GET requests with file query parameter
    if request.method == 'GET' and request.args.get('file'):
        error = "Failed: Invalid request. Please upload a PDF using the form."
        logger.error(f"Invalid GET request with file parameter: {request.args.get('file')}")
        return render_template('index.html', error=error, message=None, show_chat=False, recent_chats=recent_chats, current_filename=current_filename)
    
    # Handle POST requests for PDF upload
    if request.method == 'POST':
        logger.debug("Processing PDF upload")
        if 'file' not in request.files:
            error = "Failed: No file uploaded."
            logger.error(error)
        else:
            # Get the uploaded file
            file = request.files['file']
            # Check if the file has a filename
            if file.filename == '':
                error = "Failed: No file selected."
                logger.error(error)
            #
            elif file and allowed_file(file.filename):
                file.seek(0, os.SEEK_END)
                file_size = file.tell()
                # Check if the file is empty
                if file_size == 0:
                    error = "Failed: Uploaded file is empty."
                    logger.error(error)
                else:
                    # Seek to the beginning of the file
                    file.seek(0)
                    # Secure the filename
                    filename = secure_filename(file.filename)
                    # Get the file path
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    try:
                        # Clear existing PDFs before saving the new one
                        clear_uploads_folder()
                        file.save(file_path)
                        logger.debug(f"PDF saved to {file_path}")
                        text = extract_text_from_pdf(file_path)
                        if not text:
                            error = "Failed: No text extracted from the PDF. It may be scanned or image-based."
                            logger.error(error)
                        else:
                            chunks = chunk_text(text)
                            index, chunks, embedder = create_vector_db(chunks)
                            recent_chats = []  # Reset chats on new PDF upload
                            current_filename = filename[:-4]  # Store the new filename (without .pdf)
                            logger.debug("PDF processing completed")
                            return redirect(url_for('index', message='success'))
                    except Exception as e:
                        error = f"Failed: Error processing PDF: {str(e)}"
                        logger.error(error)
            else:
                error = "Failed: Unsupported file type. Please upload a PDF."
                logger.error(f"Non-PDF upload attempt: {file.filename}")
                logger.debug(f"Rendering template with error: {error}")
        # Render template for failed cases (non-PDF, empty file, etc.)
        return render_template('index.html', error=error, message=None, show_chat=False, recent_chats=recent_chats, current_filename=current_filename)
    # Render template for GET requests
    return render_template('index.html', error=error, message=message, show_chat=show_chat, recent_chats=recent_chats, current_filename=current_filename)

# Route to handle chat queries
@app.route('/query', methods=['POST'])
def query():
    global index, chunks, embedder, recent_chats
    logger.debug("Handling query request")
    # Get the query text from the request
    data = request.get_json()
    query_text = data.get('query', '')
    # Check if the query is empty
    if not query_text:
        logger.warning("Empty query received")
        return jsonify({'answer': "Please enter a query."})
    # Check if the index, chunks, or embedder is None
    if index is None or chunks is None or embedder is None:
        logger.error("No PDF processed")
        return jsonify({'answer': "No PDF processed. Please upload a PDF first."})
    # Retrieve the chunks from the vector database
    retrieved_chunks = retrieve_chunks(query_text, index, chunks, embedder)
    # Generate the response
    answer = generate_response(query_text, retrieved_chunks)
    logger.debug(f"Query response: {answer}")
    recent_chats.append({"query": query_text, "response": answer, "timestamp": datetime.now().isoformat()})
    recent_chats = recent_chats[-5:]  # Keep only the last 5 chats
    # Save the recent chats to a JSON file
    with open('recent_chats/chats.json', 'w') as f:
        json.dump(recent_chats, f)
    logger.debug(f"Recent chats: {recent_chats}")
    return jsonify({'answer': answer})

if __name__ == '__main__':
    app.run(debug=True)



