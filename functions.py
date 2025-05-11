# Import Libraries
import pdfplumber
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import nltk
from nltk.tokenize import sent_tokenize
import logging
from dotenv import load_dotenv
import os
from pdf2image import convert_from_path
import pytesseract
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# Set up logging to debug issues
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Download NLTK Data
nltk.download('punkt')


# Function to extract text from PDF
def extract_text_from_pdf(file_path):
    logger.debug(f"Extracting text from PDF: {file_path}")
    text = ""
    
    # Try extracting text with pdfplumber first
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        logger.debug(f"Extracted {len(text)} characters with pdfplumber")
    except Exception as e:
        logger.warning(f"pdfplumber failed: {e}")
    
    # If text is empty, try OCR
    if not text:
        logger.debug("Insufficient text extracted; attempting OCR")
        try:
            # Set Tesseract path explicitly
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            # Convert PDF pages to images with explicit poppler path
            logger.debug("Attempting to convert PDF to images with poppler")
            images = convert_from_path(file_path, poppler_path=r'C:\poppler\Library\bin')
            logger.debug(f"Converted PDF to {len(images)} images")
            ocr_text = ""
            for i, image in enumerate(images):
                # Extract text from each image using Tesseract
                page_text = pytesseract.image_to_string(image, lang='eng')
                if page_text:
                    ocr_text += page_text + "\n"
                logger.debug(f"OCR extracted {len(page_text)} characters from page {i+1}")
            text = ocr_text if ocr_text.strip() else text
            logger.debug(f"Total OCR text: {len(text)} characters")
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            if "poppler" in str(e).lower() or "page count" in str(e).lower():
                raise ValueError("OCR failed: Ensure poppler is installed")
            if "tesseract" in str(e).lower():
                raise ValueError("OCR failed: Ensure Tesseract is installed")
            # Continue to check for meaningful text
    
    # Final check for meaningful text
    if not text or len(text.strip()) < 50:
        logger.error("No meaningful text extracted from PDF")
        raise ValueError("No meaningful text extracted from the PDF. It may be scanned with poor quality or empty.")
    
    logger.debug("Text extraction successful")
    return text

# Function to split text into chunks for embedding
def chunk_text(text,chunk_size=200,overlap_ratio=0.2):
    logger.debug(f"Chunking text into chunks of size {chunk_size} with overlap {overlap_ratio}")
    sentences = sent_tokenize(text)
    chunks = []
    overlap_size = int(chunk_size * overlap_ratio)
    for i in range(0,len(sentences),chunk_size-overlap_size):
        chunk = sentences[i:i+chunk_size]
        chunks.append(' '.join(chunk))
    logger.debug(f"Successfully chunked text into {len(chunks)} chunks")
    return chunks

# Function to create vector database from text chunks
def create_vector_db(chunks):
    logger.debug("Creating vector database from text chunks")
    # Load pre-trained model for embeddings
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    logger.debug("Successfully loaded SentenceTransformer model")
    # Generate embeddings for each chunk
    embeddings = embedder.encode(chunks,convert_to_numpy=True)
    logger.debug(f"Successfully generated embeddings for {len(chunks)} chunks")
    # Get dimension of embeddings
    dimension = embeddings.shape[1]
    logger.debug(f"Embeddings have dimension {dimension}")
    # Initialize FAISS index
    index = faiss.IndexFlatL2(dimension)
    # Add embeddings to FAISS index
    index.add(embeddings)
    logger.debug("Successfully added embeddings to FAISS index")
    return index, chunks, embedder

# Function to retrieve relevant chunks from vector database based on user query
def retrieve_chunks(query,index,chunks,embedder,k=3):
    try:
        # Retrieve the relevant chunks from the vector database
        logger.debug(f"Retrieving {k} relevant chunks for query: {query}")
        query_embedding = embedder.encode([query],convert_to_numpy=True)
        distances,indices = index.search(query_embedding,k)
        logger.debug(f"Successfully retrieved {k} chunks")
        # Return the retrieved chunks
        retrieved_chunks = [chunks[idx] for idx in indices[0]]
        return retrieved_chunks
    except Exception as e:
        logger.error(f"Error retrieving chunks: {e}")
        return []


# Funtion to generate a response using a language model
def generate_response(query, retrieved_chunks):
    logger.debug("Generating response with Gemini")
    # Join the retrieved chunks into a single string
    context = " ".join(retrieved_chunks)
    # Generate a prompt for the language model
    prompt = f"""
    You are a helpful assistant answering questions based on a provided PDF document. 
    Use only the following context to generate a concise and accurate answer. 
    Do not use external knowledge or make up information. If the context lacks sufficient information, say so clearly.

    Context: {context}

    Question: {query}

    Answer:
    """
    try:
        model = genai.GenerativeModel('gemini-2.0-flash') 
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.0,  # Minimize creativity to reduce hallucination
                "max_output_tokens": 512
            }
        )
        # Get the answer from the language model
        answer = response.text.strip()
        # Check if the answer is empty or "none"
        if not answer or answer.lower() == "none":
            logger.debug("No meaningful answer found")
            return "Sorry, I couldn't find a meaningful answer in the PDF content."
        logger.debug(f"Answer generated: {answer}")
        return answer
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return "Sorry, I couldn't process the query due to an API error."
