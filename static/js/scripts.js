// Function to append a message to the chat box
function appendMessage(message, type) {
    console.log(`Appending ${type} message: ${message}`);
    const chatBox = document.getElementById('chat-box');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${type}-message`;
    messageDiv.textContent = message;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to bottom
}

// Function to send a query to the server
function sendQuery() {
    const queryInput = document.getElementById('query-input');
    const query = queryInput.value.trim();
    if (!query) return;
    
    console.log(`Sending query: ${query}`);
    // Append user message
    appendMessage(query, 'user');
    queryInput.value = ''; // Clear input
    
    // Send query to server
    fetch('/query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: query })
    })
    .then(response => {
        console.log('Query response received');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        // Append bot response
        appendMessage(data.answer, 'bot');
        // Remove oldest chat if more than 5 pairs exist
        const chatBox = document.getElementById('chat-box');
        const messages = chatBox.getElementsByClassName('chat-message');
        while (messages.length > 11) { // 5 queries + 5 responses + 1 initial bot message = 11 messages
            chatBox.removeChild(messages[0]);
        }
    })
    .catch(error => {
        console.error(`Query error: ${error}`);
        appendMessage('Error: Could not process query.', 'bot');
    });
}

// Function to reset UI before a new upload
function resetUI() {
    console.log('Resetting UI for new upload');
    const uploadSection = document.querySelector('.upload-section');
    const existingFeedback = uploadSection.querySelector('.error, .message');
    if (existingFeedback) {
        existingFeedback.remove();
    }
    const chatSection = document.getElementById('chat-section');
    chatSection.style.display = 'none';
}

// Function to update feedback (error or message) in the UI
function updateFeedback(html) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    const uploadSection = document.querySelector('.upload-section');
    const existingFeedback = uploadSection.querySelector('.error, .message');
    
    // Remove existing feedback to avoid duplicates
    if (existingFeedback) {
        existingFeedback.remove();
    }
    
    // Insert new error or message
    const errorDiv = doc.querySelector('.error');
    const messageDiv = doc.querySelector('.message');
    if (errorDiv) {
        const newError = document.createElement('div');
        newError.className = 'error';
        newError.textContent = errorDiv.textContent;
        uploadSection.insertBefore(newError, document.getElementById('loading').nextSibling);
    } else if (messageDiv) {
        const newMessage = document.createElement('div');
        newMessage.className = 'message';
        newMessage.textContent = messageDiv.textContent;
        uploadSection.insertBefore(newMessage, document.getElementById('loading').nextSibling);
    }
    
    // Update chat section visibility
    const chatSection = document.getElementById('chat-section');
    const chatSectionInResponse = doc.querySelector('#chat-section');
    chatSection.style.display = chatSectionInResponse.style.display;
}

// Handle file input change to reset UI
document.querySelector('input[type="file"]').addEventListener('change', function() {
    resetUI();
});

// Handle form submission for PDF upload
document.getElementById('upload-form').addEventListener('submit', function(e) {
    e.preventDefault();
    console.log('Submitting PDF upload form');
    resetUI(); // Reset UI before submission
    const loading = document.getElementById('loading');
    const chatSection = document.getElementById('chat-section');
    loading.style.display = 'block'; // Show loading indicator
    
    const formData = new FormData(this);
    fetch('/', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        console.log('Upload response received');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.text();
    })
    .then(html => {
        loading.style.display = 'none'; // Hide loading indicator
        updateFeedback(html); // Update UI with error or message
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const messageDiv = doc.querySelector('.message');
        if (messageDiv && messageDiv.textContent === 'success') {
            window.location = '/?message=success'; // Proceed to show chatbox
        }
    })
    .catch(error => {
        console.error(`Upload error: ${error}`);
        loading.style.display = 'none';
        chatSection.style.display = 'none'; // Ensure chatbox stays hidden
        const uploadSection = document.querySelector('.upload-section');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error';
        errorDiv.textContent = 'Failed: Error uploading file.';
        uploadSection.insertBefore(errorDiv, document.getElementById('loading').nextSibling);
    });
});

// Allow pressing Enter to send query
document.getElementById('query-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendQuery();
    }
});