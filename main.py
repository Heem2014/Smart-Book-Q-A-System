"""
main.py - Smart Book Q&A Crew (All-in-One)

Agents, tasks, crew, and entry point in a single file.

Three agents work in sequence:
  1. Document Retriever - searches the vector store for relevant chunks
  2. Answer Writer     - writes a clear answer from the chunks
  3. Quality Checker   - verifies the answer is correct

Before running, make sure you have:
  1. Added your PDF or TXT files to the 'docs/' folder
  2. Run 'python rag_setup.py' to build the vector store
  3. Created a .env file with your GOOGLE_API_KEY

Usage:
    python main.py                # Command-line interface
    streamlit run main.py         # Web interface with Streamlit
"""

import os
import streamlit as st

# Set up API keys BEFORE importing CrewAI (critical for LiteLLM)
def setup_api_keys():
    """Set up API keys from environment or Streamlit secrets."""
    # Try environment variables first
    groq_key = os.getenv("GROQ_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    # If not in env, try Streamlit secrets (for Streamlit Cloud)
    if not groq_key:
        try:
            groq_key = st.secrets.get("GROQ_API_KEY", None)
        except Exception:
            groq_key = None
    
    if not gemini_key:
        try:
            gemini_key = st.secrets.get("GEMINI_API_KEY", None)
        except Exception:
            gemini_key = None
    
    # Set in os.environ so CrewAI/LiteLLM can find them
    if groq_key:
        os.environ["GROQ_API_KEY"] = groq_key
    if gemini_key:
        os.environ["GEMINI_API_KEY"] = gemini_key
        os.environ["GOOGLE_API_KEY"] = gemini_key
    
    return groq_key is not None

# Initialize API keys before any CrewAI imports
api_keys_ready = setup_api_keys()

# Load dotenv only if available (not needed on Streamlit Cloud)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed (e.g., on Streamlit Cloud)
    # This is fine - we're using st.secrets instead
    pass

from crewai import Agent, Task, Crew, Process
from rag_tool import rag_search_tool
from rag_setup import build_vector_store_with_progress
import tempfile
import shutil


# ============================================================
#  AGENTS
# ============================================================

# Agent 1: Document Retriever
# Searches the vector store and finds relevant text chunks.
retriever_agent = Agent(
    role="Document Retriever",
    goal="Search the vector store and return the most relevant chunks for the question",
    backstory=(
        "You are an expert librarian who knows exactly where to find information. "
        "Your job is to search through the document database and pull out the "
        "most relevant paragraphs that will help answer the user's question. "
        "Always use your RAG Search Tool to find information."
    ),
    tools=[rag_search_tool],
    llm="groq/llama-3.3-70b-versatile",
    verbose=True
)

# Agent 2: Answer Writer
# Reads the chunks from Agent 1 and writes a clear answer.
writer_agent = Agent(
    role="Answer Writer",
    goal="Read the retrieved chunks and write a clear, accurate answer in simple language",
    backstory=(
        "You are a friendly teacher who explains things clearly. "
        "You take information from documents and turn it into easy-to-understand "
        "answers. You ONLY use information from the provided source chunks - "
        "you never make things up or add outside knowledge."
    ),
    llm="groq/llama-3.3-70b-versatile",
    verbose=True
)

# Agent 3: Quality Checker
# Compares the answer against the source chunks.
checker_agent = Agent(
    role="Quality Checker",
    goal="Check the answer against the source chunks and confirm it is correct and complete",
    backstory=(
        "You are a careful fact-checker. Your job is to compare the written answer "
        "against the original source text and make sure every fact is accurate. "
        "If something is wrong or missing, you flag it clearly."
    ),
    llm="groq/llama-3.3-70b-versatile",
    verbose=True
)


# ============================================================
#  TASKS
# ============================================================

def create_tasks(question: str):
    """Create the three tasks for the crew based on the user's question."""

    retrieve_task = Task(
        description=(
            f"Search the document database for information about: '{question}'\n"
            "Use the RAG Search Tool to find the top 3 most relevant chunks.\n"
            "Return the chunks exactly as found - do not modify them."
        ),
        expected_output="A list of the top 3 matching text chunks from the document.",
        agent=retriever_agent
    )

    write_task = Task(
        description=(
            f"Using ONLY the retrieved chunks from the previous task, "
            f"write a clear answer to this question: '{question}'\n\n"
            "Rules:\n"
            "- Write 3-5 sentences in simple language\n"
            "- Only use facts from the source chunks\n"
            "- Do not add information that is not in the chunks"
        ),
        expected_output="A 3-5 sentence answer in simple, clear language.",
        agent=writer_agent
    )

    check_task = Task(
        description=(
            "Compare the answer from the previous task against the original "
            "source chunks. Check every fact in the answer.\n\n"
            "Your output must include:\n"
            "1. The final verified answer\n"
            "2. A verdict: 'Verified' or 'Needs Correction'\n"
            "3. Which source chunk(s) support the answer"
        ),
        expected_output=(
            "The verified answer with a status: "
            "'Verified - all facts match' or 'Needs Correction - [reason]'."
        ),
        agent=checker_agent
    )

    return [retrieve_task, write_task, check_task]


# ============================================================
#  CREW
# ============================================================

def run_crew(question: str):
    """Run the full crew to answer a question about the uploaded document."""

    tasks = create_tasks(question)

    crew = Crew(
        agents=[task.agent for task in tasks],
        tasks=tasks,
        process=Process.sequential,
        verbose=True
    )

    result = crew.kickoff()
    return result


# ============================================================
#  STREAMLIT UI
# ============================================================

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
            # Save the uploaded file
            file_path = os.path.join("docs", uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        
        return True
    return False


def build_vector_store_ui():
    """UI component for building the vector store."""
    st.subheader("📚 Build Knowledge Base")
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Upload PDF or TXT documents",
        type=['pdf', 'txt'],
        accept_multiple_files=True,
        help="Upload documents you want to ask questions about"
    )
    
    if uploaded_files:
        if handle_file_upload(uploaded_files):
            st.success(f"✅ Uploaded {len(uploaded_files)} file(s)")
            
            # Show uploaded files
            st.write("**Uploaded files:**")
            for file in uploaded_files:
                st.write(f"- {file.name}")
            
            # Button to build vector store
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
    
    # Show current status
    if st.session_state.vector_store_built:
        st.info("✅ Vector store is ready! You can now ask questions.")
    else:
        st.warning("⚠️ Please upload documents and build the vector store first.")


def chat_interface():
    """Main chat interface for asking questions."""
    st.subheader("💬 Ask Questions About Your Documents")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Check if vector store exists
        if not st.session_state.vector_store_built:
            error_msg = "Please upload documents and build the vector store first!"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            with st.chat_message("assistant"):
                st.error(error_msg)
            return
        
        # Get response from crew
        with st.chat_message("assistant"):
            with st.spinner("The crew is working on your question..."):
                try:
                    result = run_crew(prompt)
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
    
    # Check if already configured from environment/secrets
    if st.session_state.api_key_configured:
        st.success("✅ API key configured from environment/secrets")
        return True
    
    # Allow user to input API key directly
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
                # Set the API key in environment
                os.environ["GROQ_API_KEY"] = api_key_input.strip()
                st.session_state.user_api_key = api_key_input.strip()
                st.session_state.api_key_configured = True
                
                # Show success and rerun to reload with new key
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
    
    # Show instructions if no key is configured
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
    
    # Page configuration
    st.set_page_config(
        page_title="Smart Book Q&A Crew",
        page_icon="📚",
        layout="wide"
    )
    
    # Title and description
    st.title("📚 Smart Book Q&A Crew")
    st.markdown("""
    **Ask questions about your uploaded documents using AI agents!**
    
    This app uses three specialized AI agents to provide accurate answers:
    1. **Document Retriever** - Finds relevant information in your documents
    2. **Answer Writer** - Creates clear, accurate answers
    3. **Quality Checker** - Verifies the answers are correct
    """)
    
    # Sidebar
    with st.sidebar:
        st.header("🛠️ Controls")
        
        # API Key Configuration Section
        api_ready = api_key_configuration()
        
        st.divider()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            clear_chat()
        
        # Reset vector store button
        if st.button("🔄 Reset Vector Store"):
            if os.path.exists("chroma_db"):
                shutil.rmtree("chroma_db")
                st.session_state.vector_store_built = False
                st.success("Vector store reset! Please rebuild.")
                st.rerun()
        
        st.divider()
        
        # Show stats
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
    
    # Check if API key is configured before showing main content
    if not api_keys_ready and not st.session_state.api_key_configured:
        st.warning("⚠️ Please configure your API key in the sidebar to continue.")
        st.stop()
    
    # Main content area with tabs
    tab1, tab2 = st.tabs(["💬 Chat", "📚 Knowledge Base"])
    
    with tab1:
        chat_interface()
    
    with tab2:
        build_vector_store_ui()


# ============================================================
#  ENTRY POINT
# ============================================================

if __name__ == "__main__":
    # Check if running with Streamlit
    import sys
    if "streamlit" in sys.modules:
        main()
    else:
        # Original command-line interface
        print("=" * 50)
        print("  Smart Book Q&A Crew")
        print("  Ask any question about your uploaded documents")
        print("=" * 50)
        print()
        print("Type 'quit' to exit.")
        print()

        while True:
            question = input("Your question: ").strip()

            if question.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            if not question:
                print("Please type a question.\n")
                continue

            print("\nThe crew is working on your question...\n")

            result = run_crew(question)

            print()
            print("=" * 50)
            print("  FINAL ANSWER:")
            print("=" * 50)
            print(result)
            print("=" * 50)
            print()
