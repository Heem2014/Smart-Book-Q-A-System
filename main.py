"""
main.py - Smart Book Q&A System (LangChain version for Python 3.14)

Uses LangChain directly instead of CrewAI for Python 3.14 compatibility.

Before running, make sure you have:
  1. Added your PDF or TXT files to the 'docs/' folder
  2. Run 'python rag_setup.py' to build the vector store  
  3. Set GROQ_API_KEY in environment or Streamlit secrets

Usage:
    streamlit run main.py
"""

import os
import streamlit as st

# Set up API keys BEFORE any imports
def setup_api_keys():
    """Set up API keys from environment or Streamlit secrets."""
    groq_key = os.getenv("GROQ_API_KEY")
    
    if not groq_key:
        try:
            groq_key = st.secrets.get("GROQ_API_KEY", None)
        except Exception:
            groq_key = None
    
    if groq_key:
        os.environ["GROQ_API_KEY"] = groq_key
    
    return groq_key is not None

api_keys_ready = setup_api_keys()

# Load dotenv only if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from rag_tool import rag_search_tool
from rag_setup import build_vector_store_with_progress
import shutil


def initialize_session_state():
    """Initialize session state variables."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'vector_store_built' not in st.session_state:
        st.session_state.vector_store_built = os.path.exists("chroma_db")
    if 'api_key_configured' not in st.session_state:
        st.session_state.api_key_configured = api_keys_ready
    if 'user_api_key' not in st.session_state:
        st.session_state.user_api_key = ""


def handle_file_upload(uploaded_files):
    """Handle uploaded files and save them to docs folder."""
    if uploaded_files:
        os.makedirs("docs", exist_ok=True)
        
        for uploaded_file in uploaded_files:
            file_path = os.path.join("docs", uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        
        return True
    return False


def build_vector_store_ui():
    """UI component for building the vector store."""
    st.subheader("📚 Build Knowledge Base")
    
    uploaded_files = st.file_uploader(
        "Upload PDF or TXT documents",
        type=['pdf', 'txt'],
        accept_multiple_files=True,
        help="Upload documents you want to ask questions about"
    )
    
    if uploaded_files:
        if handle_file_upload(uploaded_files):
            st.success(f"✅ Uploaded {len(uploaded_files)} file(s)")
            
            st.write("**Uploaded files:**")
            for file in uploaded_files:
                st.write(f"- {file.name}")
            
            if st.button("🔨 Build Vector Store", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def update_progress(progress, message):
                    progress_bar.progress(progress)
                    status_text.text(message)
                
                with st.spinner("Building vector store..."):
                    result, message = build_vector_store_with_progress(
                        docs_folder="docs",
                        progress_callback=update_progress
                    )
                
                if result:
                    st.success(message)
                    st.session_state.vector_store_built = True
                    st.rerun()
                else:
                    st.error(message)
    
    if st.session_state.vector_store_built:
        st.info("✅ Vector store is ready! You can now ask questions.")
    else:
        st.warning("⚠️ Please upload documents and build the vector store first.")


@st.cache_resource
def get_llm():
    """Get the Groq LLM (cached to avoid reloading)."""
    return ChatGroq(
        model_name="llama-3.3-70b-versatile",
        temperature=0.7,
        groq_api_key=os.environ.get("GROQ_API_KEY")
    )


def answer_question(question: str) -> str:
    """Answer a question using RAG with LangChain."""
    try:
        # Get relevant context from RAG tool
        context = rag_search_tool(question)
        
        # Create prompt
        prompt = f"""Based on the following information from the documents, please answer the question.

Question: {question}

Relevant Information:
{context}

Please provide a clear, concise answer based ONLY on the information above. If the information doesn't contain the answer, say so clearly."""

        # Get answer from LLM
        llm = get_llm()
        response = llm.invoke(prompt)
        
        return response.content
        
    except Exception as e:
        return f"Error answering question: {str(e)}"


def chat_interface():
    """Main chat interface for asking questions."""
    st.subheader("💬 Ask Questions About Your Documents")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask a question about your documents..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        if not st.session_state.vector_store_built:
            error_msg = "Please upload documents and build the vector store first!"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            with st.chat_message("assistant"):
                st.error(error_msg)
            return
        
        with st.chat_message("assistant"):
            with st.spinner("Searching documents and generating answer..."):
                try:
                    result = answer_question(prompt)
                    st.markdown(result)
                    st.session_state.messages.append({"role": "assistant", "content": str(result)})
                except Exception as e:
                    error_msg = f"Error getting response: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})


def clear_chat():
    """Clear the chat history."""
    st.session_state.messages = []
    st.rerun()


def api_key_configuration():
    """Sidebar component for API key configuration."""
    st.subheader("🔑 API Key Configuration")
    
    if st.session_state.api_key_configured:
        st.success("✅ API key configured")
        return True
    
    st.markdown("**Enter your GROQ API Key:**")
    st.markdown("*Get one at [https://console.groq.com/keys](https://console.groq.com/keys)*")
    
    api_key_input = st.text_input(
        "GROQ API Key",
        value=st.session_state.user_api_key,
        type="password",
        placeholder="gsk_...",
        help="Your GROQ API key will be stored in session (not saved permanently)"
    )
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("💾 Save & Use", use_container_width=True):
            if api_key_input and api_key_input.strip():
                os.environ["GROQ_API_KEY"] = api_key_input.strip()
                st.session_state.user_api_key = api_key_input.strip()
                st.session_state.api_key_configured = True
                
                st.success("✅ API key saved!")
                st.info("🔄 Refreshing app with new API key...")
                st.rerun()
            else:
                st.error("❌ Please enter a valid API key")
    
    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.user_api_key = ""
            st.session_state.api_key_configured = False
            if "GROQ_API_KEY" in os.environ:
                del os.environ["GROQ_API_KEY"]
            st.warning("⚠️ API key cleared. Please enter a new one.")
            st.rerun()
    
    if not st.session_state.api_key_configured:
        st.markdown("---")
        st.markdown("""
        **ℹ️ How to get a GROQ API Key:**
        
        1. Visit [https://console.groq.com/keys](https://console.groq.com/keys)
        2. Sign up or log in
        3. Create a new API key
        4. Copy and paste it above
        
        **For Streamlit Cloud deployment:**
        - Add `GROQ_API_KEY` to your app's Secrets settings instead
        """)
    
    return st.session_state.api_key_configured


def main():
    """Main Streamlit app."""
    initialize_session_state()
    
    st.set_page_config(
        page_title="Smart Book Q&A System",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("📚 Smart Book Q&A System")
    st.markdown("""
    **Ask questions about your uploaded documents!**
    
    This app uses RAG (Retrieval-Augmented Generation) to find relevant information 
    in your documents and generate accurate answers.
    """)
    
    with st.sidebar:
        st.header("🛠️ Controls")
        
        api_ready = api_key_configuration()
        
        st.divider()
        
        if st.button("🗑️ Clear Chat History"):
            clear_chat()
        
        if st.button("🔄 Reset Vector Store"):
            if os.path.exists("chroma_db"):
                shutil.rmtree("chroma_db")
                st.session_state.vector_store_built = False
                st.success("Vector store reset! Please rebuild.")
                st.rerun()
        
        st.divider()
        
        st.subheader("📊 Statistics")
        if os.path.exists("docs"):
            doc_count = len([f for f in os.listdir("docs") if f.endswith(('.pdf', '.txt'))])
            st.write(f"**Documents:** {doc_count}")
        
        if st.session_state.vector_store_built:
            st.write("**Status:** ✅ Ready")
        else:
            st.write("**Status:** ⚠️ Not Ready")
        
        st.divider()
        st.write("**Chat Messages:**", len(st.session_state.messages))
    
    if not api_keys_ready and not st.session_state.api_key_configured:
        st.warning("⚠️ Please configure your API key in the sidebar to continue.")
        st.stop()
    
    tab1, tab2 = st.tabs(["💬 Chat", "📚 Knowledge Base"])
    
    with tab1:
        chat_interface()
    
    with tab2:
        build_vector_store_ui()


if __name__ == "__main__":
    main()
