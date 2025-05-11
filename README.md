# PDF Chatbot

The **PDF Chatbot** is an advanced web application that allows users to upload PDF documents and interact with them through a conversational interface. Powered by a **Retrieval-Augmented Generation (RAG)** model, it combines natural language processing (NLP), vector search, and Google’s Generative AI to deliver accurate, document-specific answers.

---

## Features

- **PDF Upload:** Upload PDF files via a simple web interface.
- **Text Extraction:** Uses `pdfplumber` to extract reliable content from PDFs.
- **Text Chunking:** Splits text into sentence-overlapped chunks for better contextual understanding.
- **Vector Database:** Uses `all-MiniLM-L6-v2` and FAISS for fast similarity-based retrieval.
- **Query Processing:** Supports natural language queries with responses generated using Google Generative AI.
- **Chat Interface:** Clean, responsive UI for chat-based interaction.
- **Recent Chats:** Stores the last five interactions in a JSON file.
- **Upload Management:** Securely overwrites existing files to manage space.
- **Responsive Design:** Optimized for desktop, tablet, and mobile use.

---

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- `pip` for installing dependencies

### Installation Steps

1. **Create Virtual Environment (Optional but Recommended)**

    ```bash
    python -m venv venv
    `venv\Scripts\activate`
    ```

2. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

    Key dependencies include:

    - `sentence-transformers`
    - `faiss-cpu`
    - `nltk`
    - `pdfplumber`
    - `flask`
    - `werkzeug`
    - `python-dotenv`
    - `google-generativeai`

3. **Configure Google API Key**

    Create a `.env` file in the project root:

    ```env
    GOOGLE_API_KEY=your_api_key_here
    ```

4. **Download NLTK Data**

    ```python
    import nltk
    nltk.download('punkt')
    ```

5. **Run the Application**

    ```bash
    python app.py
    ```

    Visit `http://localhost:5000` in your browser.

6. **Ensure Folder Structure**

    - `uploads/`
    - `recent_chats/`

    These folders are auto-created if missing but must be writable.

---

## Usage

### 1. Upload a PDF

- Go to `http://localhost:5000`
- Upload your PDF file via the form
- Wait for the success message

### 2. Ask Questions

- Type a question about the PDF (e.g., "What is the main topic?")
- Press **Send** or hit Enter
- View the AI-generated, document-specific answer

### 3. View Recent Chats

- The interface shows the last 5 interactions
- Chat history is stored in `recent_chats/chats.json`

---

## Configuration

- **API Key:** Set via `.env`
- **Uploads:** Stored in `uploads/`; older files are overwritten
- **Recent Chats:** Stored in `recent_chats/chats.json`
- **Security:** File uploads are sanitized using `secure_filename`

---

## Functionalities

### PDF Processing

- Extracts text via `pdfplumber`
- Splits content into overlapping sentence chunks

### Vector Database

- Embeds text chunks using `all-MiniLM-L6-v2`
- FAISS index enables rapid similarity search

### Query Handling (RAG-Based)

- Embeds user query and retrieves top 3 relevant chunks
- Uses Google Generative AI to generate responses

### Chat Interface

- Responsive chat layout
- Displays user queries and AI responses
- Stores recent chats in JSON

### Upload Management

- Clears `uploads/` before each new file
- Sanitizes filenames to prevent directory traversal

### Error Handling

- Provides user-friendly error messages for:
  - Invalid file types
  - Empty documents
  - API/key issues

### Logging

- Logs key events for debugging and monitoring

---

## RAG-Based Architecture

### Retrieval

- PDF content is chunked and embedded
- Embeddings indexed with FAISS
- Top 3 relevant chunks retrieved per query

### Generation

- Chunks and user query are sent to Google Generative AI
- Response is generated based on PDF content and context

This hybrid architecture ensures accuracy, speed, and relevance in responses.

---

## Storage and Chat History

### Recent Chats

- Stored in `recent_chats/chats.json`
- Stores query, response, and timestamp
- Helps maintain context across sessions

### PDF Uploads

- Stored in `uploads/`
- Automatically clears on new upload
- Prevents storage bloat by storing only one file

---

---

## License

This project is open-source and available under the [MIT License](LICENSE).
