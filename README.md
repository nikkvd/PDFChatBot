# PDF Chatbot

The **PDF Chatbot** is a web application that allows users to interact with PDF documents through a conversational interface. Powered by a Retrieval-Augmented Generation (RAG) architecture, it combines Natural Language Processing (NLP), vector similarity search, and Google Generative AI to provide accurate, document-specific answers. The chatbot supports both text-based and scanned PDFs using OCR when needed.

---

## Features

- **PDF Upload**: Simple web interface for uploading PDFs.
- **Text Extraction**: Uses `pdfplumber` for text-based PDFs and `pytesseract` with `pdf2image` for scanned PDFs.
- **Text Chunking**: Splits text into overlapping chunks for better context retrieval.
- **Vector Database**: Uses `all-MiniLM-L6-v2` and `FAISS` for fast similarity search.
- **Query Processing**: Natural language queries processed via Google Generative AI.
- **Chat Interface**: Responsive chat UI for smooth interaction.
- **Recent Chats**: Last five interactions stored in a JSON file.
- **Upload Management**: Overwrites old files to manage storage.
- **OCR Support**: Handles image-based PDFs using Tesseract OCR.

---

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- `pip` for dependency management
- **Poppler**: Required by `pdf2image` for scanned PDFs.
- **Tesseract OCR**: Required for extracting text from scanned PDFs.

### Installation Steps

1. **Create a Virtual Environment** (optional but recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate   # Linux/macOS
    venv\Scripts\activate      # Windows
    ```

2. **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

    Key packages include:

    - `sentence-transformers`
    - `faiss-cpu`
    - `nltk`
    - `pdfplumber`
    - `flask`
    - `werkzeug`
    - `python-dotenv`
    - `google-generativeai`
    - `pdf2image`
    - `pytesseract`

3. **Install Poppler**:

    - **Windows**:
        - Download from: https://github.com/oschwartz10612/poppler-windows
        - Extract and add the path (e.g., `C:\poppler\Library\bin`) to the system environment variables.
        - Verify: `pdftoppm -v`
    - **Linux**:

        ```bash
        sudo apt-get install poppler-utils
        ```

    - **macOS**:

        ```bash
        brew install poppler
        ```

4. **Install Tesseract OCR**:

    - **Windows**:
        - Download from: https://github.com/UB-Mannheim/tesseract
        - Install and ensure the path is added to system variables.
        - Verify: `tesseract --version`
    - **Linux**:

        ```bash
        sudo apt-get install tesseract-ocr
        ```

    - **macOS**:

        ```bash
        brew install tesseract
        ```

5. **Configure Google API Key**:

    - Create a `.env` file in the project root:

        ```env
        GOOGLE_API_KEY=your_api_key_here
        ```

6. **Download NLTK Data**:

    ```python
    import nltk
    nltk.download('punkt')
    ```

7. **Run the Application**:

    ```bash
    python app.py
    ```

    Open [http://localhost:5000](http://localhost:5000) in your browser.

---

## Folder Structure

- `uploads/` – Temporary uploaded PDFs (auto-cleared).
- `recent_chats/` – Stores chat history as `chats.json`.

---

## Usage

1. **Upload a PDF**: Navigate to the app and upload a PDF file (text-based or scanned).
2. **Interact**: Ask natural language questions about the document.
3. **Review History**: View the last five interactions saved for reference.

---

## Functional Overview

### PDF Processing

| Type         | Method Used                            |
|--------------|-----------------------------------------|
| Text-based   | `pdfplumber`                            |
| Scanned PDFs | `pdf2image` + `pytesseract` (Tesseract) |

- Text is chunked into 500-token segments with 20% overlap.

### Vector Search

- Embedding: `all-MiniLM-L6-v2`
- Search: `FAISS` (retrieves top 3 chunks per query)

### Query Handling (RAG)

- User query is embedded.
- Top chunks retrieved.
- Prompt + chunks are sent to Google Generative AI.
- Response is returned to the user.

---

## RAG Architecture

**Retrieval**:

- Chunk PDF into overlapping segments
- Store embeddings in FAISS index

**Augmentation**:

- On each query, retrieve the top 3 relevant chunks

**Generation**:

- Use Google Generative AI to craft a response using context

---

## Error Handling

Provides feedback for:

- Invalid file formats
- OCR failures
- Missing installations (Poppler, Tesseract)
- Empty/unreadable PDFs
- API key issues

---

## 📌 Tips for Scanned PDFs

- Use high-quality scans (300 DPI recommended)
- Ensure clear, legible text
- Troubleshoot OCR errors by checking Poppler/Tesseract installations

---
