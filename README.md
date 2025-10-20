# AURA 🌟



AURA is an AI assistant that was developed during the hackathon Desafio Unisoma 2025. It was designed to be used by a NGO specialized in Heulosophy, and designed to connect users to knowledge through an intelligent and intuitive conversational interface. Inspired by Walter Benjamin's philosophical concept of "aura," the project seeks to restore the presence and authenticity of knowledge even when mediated by technology. It should be used in the Portuguese language.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)
![LangChain](https://img.shields.io/badge/langchain-latest-orange.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-412991.svg)

## 📋 Table of Contents

- [Features](#-features)
- [Technologies](#-technologies)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Functionality](#-functionality)

## ✨ Features

- 🤖 **RAG Chatbot (Retrieval-Augmented Generation)** - Contextualized responses based on documents
- 📚 **Document Processing** - Support for PDF and TXT files
- 💬 **Conversation History** - Maintains context between messages
- 🎨 **Modern Interface** - Responsive design with dynamic animations
- 📤 **Document Upload** - Add new files to the knowledge base
- 🔍 **Semantic Search** - Find relevant information using embeddings
- 🌐 **Multi-page** - Smooth navigation between sections

## 🛠 Technologies

### Backend
- **Flask** - Python web framework
- **LangChain** - Framework for LLM applications
- **OpenAI API** - GPT-4 for response generation
- **PyPDF2** - PDF text extraction
- **PDFPlumber** - Advanced PDF processing
- **python-dotenv** - Environment variable management

### Frontend
- **HTML5/CSS3** - Structure and styling
- **JavaScript ES6+** - Interactivity
- **Font Awesome** - Icons
- **Google Fonts** - Custom typography

### AI/ML
- **OpenAI Embeddings** - Text vectorization
- **InMemoryVectorStore** - Vector storage
- **RecursiveCharacterTextSplitter** - Document chunking

## 📦 Prerequisites

- Python 3.8 or higher
- OpenAI API Key
- pip (Python package manager)

## 🚀 Installation

1. **Clone the repository**
```bash
git clone https://github.com/giovannimicaroni/aurachatbot.git
cd aurachatbot
```

2. **Create a virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

## 📁 Project Structure
```
aura/
│
├── app.py                 # Main Flask application
├── chatbot.py            # RAG Chatbot logic
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (not versioned)
│
├── static/               # Static files
│   ├── css/
│   │   ├── styles.css   # Main page styles
│   │   └── chat.css     # Chat page styles
│   ├── js/
│   │   ├── main.js      # Main page scripts
│   │   └── chat.js      # Chat page scripts
│   └── images/
│       └── logo.png
│
├── templates/            # HTML templates
│   ├── index.html       # Main page
│   └── chat.html        # Dedicated chat page
│
└── arquivos_ong/        # Knowledge base
    ├── document1.pdf
    ├── document2.txt
    └── ...
```

## ⚙ Configuration

1. **Create a `.env` file in the project root**
```env
OPENAI_API_KEY=your_api_key_here
```

2. **Add your documents**
   
   Place PDF or TXT files in the `arquivos_ong/` folder before starting the application.

## 🎯 Usage

1. **Start the server**
```bash
python app.py
```

2. **Access the application**
   
   Open your browser and navigate to:
```
http://localhost:5001
```

3. **Interact with AURA**
   - Use the search bar on the home page
   - Or click the floating chat button
   - Or directly access `/chat` for the dedicated chat page


## 🎨 Functionality

### Main Page
- **Home** - Quick search with redirect to chat
- **About AURA** - Information about the project and philosophy
- **Explore** - Available features
- **Tips** - Guide for better assistant usage

### Chat
- **Contextual Conversation** - Maintains history of up to 10 interactions
- **Typing Indicator** - Visual feedback during processing
- **File Upload** - Add documents dynamically
- **Clear History** - Restart the conversation when needed

### Document Processing
- **Intelligent Chunking** - Optimized document splitting
- **Semantic Embeddings** - Similarity-based search
- **Batch Processing** - Efficient batch processing
- **Metadata Tracking** - Source tracking



> Aura was developed for non comercial purposes and its further using is not responsibility of the creators.
