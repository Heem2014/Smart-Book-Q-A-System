# Smart Book Q&A Crew - Streamlit Interface

## Overview
This application provides a web-based interface for asking questions about your documents using AI agents. It features three specialized agents that work together to provide accurate, verified answers.

## Features
- 📚 **Document Upload**: Upload PDF and TXT files through the web interface
- 🔨 **Vector Store Builder**: Build and manage your knowledge base with progress tracking
- 💬 **Interactive Chat**: Ask questions in a conversational interface
- ✅ **Quality Assurance**: Three-agent system ensures accurate answers
- 🗑️ **Easy Management**: Clear chat history and reset vector store options

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure you have a `.env` file with your API keys:
```
GROQ_API_KEY=your_groq_api_key_here
```

## Deployment to Streamlit Cloud

### Prerequisites
1. Push your code to GitHub
2. Have a GROQ API key (get one at https://console.groq.com/)

### Deployment Steps

1. **Create required files** (already included):
   - `requirements.txt` - Python dependencies
   - `packages.txt` - System dependencies (contains `build-essential`)

2. **Connect to Streamlit Cloud**:
   - Go to https://streamlit.io/cloud
   - Click "New app"
   - Connect your GitHub repository
   - Select the main branch and `main.py` as the main file

3. **Add API Keys**:
   - In your Streamlit Cloud dashboard, click on your app
   - Go to **Settings** → **Secrets**
   - Add your API keys in this format:
   ```toml
   GROQ_API_KEY = "your_actual_groq_api_key_here"
   GEMINI_API_KEY = "your_gemini_key_here"
   ```
   - Click Save

4. **Deploy**:
   - Streamlit Cloud will automatically deploy your app
   - The first deployment may take 5-10 minutes

### Important Notes
- ⚠️ **NEVER commit API keys to GitHub** - use Streamlit Cloud secrets
- The `.gitignore` file prevents accidental commits of sensitive data
- `packages.txt` is required for compiled dependencies like CrewAI

## Usage

### Running the Streamlit App
```bash
streamlit run main.py
```

The app will open in your browser at `http://localhost:8501`

### How to Use

1. **Upload Documents** (Knowledge Base Tab):
   - Go to the "📚 Knowledge Base" tab
   - Upload PDF or TXT files
   - Click "🔨 Build Vector Store"
   - Wait for the process to complete

2. **Ask Questions** (Chat Tab):
   - Go to the "💬 Chat" tab
   - Type your question in the chat input
   - The AI crew will process your question and provide an answer
   - View the conversation history

3. **Manage Your Session**:
   - Use the sidebar to clear chat history
   - Reset the vector store if needed
   - View statistics about your documents

## Architecture

The application uses three AI agents:

1. **Document Retriever**: Searches the vector store for relevant information
2. **Answer Writer**: Creates clear, accurate answers from retrieved chunks
3. **Quality Checker**: Verifies answers against source documents

## File Structure

- `main.py` - Main application with Streamlit UI and CrewAI logic
- `rag_setup.py` - Document indexing and vector store creation
- `rag_tool.py` - Custom CrewAI tool for searching the vector store
- `docs/` - Folder containing uploaded documents
- `chroma_db/` - Vector database storage

## Command-Line Mode

You can still use the original command-line interface:
```bash
python main.py
```

## Troubleshooting

- **No vector store found**: Upload documents and build the vector store first
- **API key errors**: Check your `.env` file has the correct GROQ_API_KEY
- **Import errors**: Run `pip install -r requirements.txt` again
- **Port already in use**: Streamlit will automatically use the next available port

## Tips

- Upload relevant documents for better answers
- Be specific in your questions
- The system works best with well-structured documents
- Clear chat history periodically for a fresh start
