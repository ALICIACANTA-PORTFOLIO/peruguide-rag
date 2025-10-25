"""
PeruGuide AI - Streamlit Frontend
Interactive web interface for Peru travel information using RAG
"""

import os
import streamlit as st
import requests
import time
from typing import Optional, Dict, Any
import json

# Page configuration
st.set_page_config(
    page_title="PeruGuide AI - Your Peru Travel Assistant",
    page_icon="🇵🇪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #D91E36;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .source-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #D91E36;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .answer-box {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# API Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")


def check_api_health() -> Dict[str, Any]:
    """Check if API is healthy."""
    try:
        response = requests.get(f"{API_URL}/api/v1/health", timeout=5)
        if response.status_code == 200:
            return response.json()
        return {"status": "unhealthy", "error": "API returned non-200 status"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


def get_available_models() -> list[str]:
    """Get list of available LLM models."""
    try:
        response = requests.get(f"{API_URL}/api/v1/models", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("models", ["openai"])
        return ["openai"]
    except Exception as e:
        st.error(f"Failed to fetch models: {e}")
        return ["openai"]


def query_rag(
    query: str,
    llm_model: str = "openai",
    top_k: int = 3,
    include_metadata: bool = True
) -> Optional[Dict[str, Any]]:
    """Query the RAG API."""
    try:
        payload = {
            "query": query,
            "llm_model": llm_model,
            "top_k": top_k,
            "include_metadata": include_metadata
        }
        
        response = requests.post(
            f"{API_URL}/api/v1/query",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Request failed: {e}")
        return None


# Main App
def main():
    # Header
    st.markdown('<h1 class="main-header">🇵🇪 PeruGuide AI</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Your Intelligent Peru Travel Assistant powered by RAG</p>',
        unsafe_allow_html=True
    )
    
    # Sidebar
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/c/cf/Flag_of_Peru.svg", width=100)
        st.title("⚙️ Settings")
        
        # API Health Check
        st.subheader("API Status")
        health = check_api_health()
        
        if health.get("status") == "healthy":
            st.success("✅ API Connected")
            st.caption(f"Version: {health.get('version', 'N/A')}")
            
            # Component status
            with st.expander("Component Details"):
                components = health.get("components", {})
                for component, status in components.items():
                    if status == "healthy" or status.isdigit():
                        st.text(f"✅ {component}: {status}")
                    else:
                        st.text(f"❌ {component}: {status}")
        else:
            st.error("❌ API Disconnected")
            st.caption(f"Error: {health.get('error', 'Unknown')}")
            st.info(f"Make sure API is running at: {API_URL}")
        
        st.divider()
        
        # Model Selection
        st.subheader("🤖 LLM Model")
        available_models = get_available_models()
        selected_model = st.selectbox(
            "Choose LLM Provider:",
            available_models,
            index=0 if "openai" in available_models else 0,
            help="Select which AI model to use for generating answers"
        )
        
        # Advanced Settings
        st.subheader("🔧 Advanced")
        top_k = st.slider(
            "Documents to retrieve:",
            min_value=1,
            max_value=10,
            value=3,
            help="Number of relevant documents to use for context"
        )
        
        include_metadata = st.checkbox(
            "Include source metadata",
            value=True,
            help="Show detailed information about sources"
        )
        
        st.divider()
        
        # Example Queries
        st.subheader("💡 Example Queries")
        example_queries = [
            "¿Cuáles son los platos típicos de Perú?",
            "¿Qué puedo visitar en Cusco?",
            "¿Cuál es la historia de Machu Picchu?",
            "¿Qué clima tiene la selva peruana?",
            "¿Cuáles son las festividades importantes en Perú?"
        ]
        
        for i, example in enumerate(example_queries, 1):
            if st.button(f"📌 {example[:40]}...", key=f"example_{i}"):
                st.session_state.example_query = example
    
    # Main Content Area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🔍 Ask about Peru")
        
        # Query Input
        default_query = st.session_state.get("example_query", "")
        query = st.text_area(
            "Your question:",
            value=default_query,
            height=100,
            placeholder="Ask me anything about Peru: culture, tourism, gastronomy, history...",
            help="Type your question in Spanish or English"
        )
        
        # Clear example query after use
        if "example_query" in st.session_state:
            del st.session_state.example_query
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
        
        with col_btn1:
            search_button = st.button("🚀 Search", type="primary", use_container_width=True)
        
        with col_btn2:
            clear_button = st.button("🗑️ Clear", use_container_width=True)
        
        if clear_button:
            st.rerun()
        
        # Process Query
        if search_button and query.strip():
            with st.spinner("🔎 Searching through Peru knowledge base..."):
                start_time = time.time()
                
                result = query_rag(
                    query=query,
                    llm_model=selected_model,
                    top_k=top_k,
                    include_metadata=include_metadata
                )
                
                elapsed_time = time.time() - start_time
            
            if result:
                # Display Answer
                st.markdown("### 💬 Answer")
                st.markdown(f'<div class="answer-box">{result["answer"]}</div>', unsafe_allow_html=True)
                
                # Metrics
                st.markdown("### 📊 Performance Metrics")
                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                
                with metric_col1:
                    st.metric(
                        "Total Time",
                        f"{result.get('latency_ms', elapsed_time*1000):.0f} ms"
                    )
                
                with metric_col2:
                    st.metric(
                        "Retrieval",
                        f"{result.get('retrieval_latency_ms', 0):.0f} ms"
                    )
                
                with metric_col3:
                    st.metric(
                        "Generation",
                        f"{result.get('generation_latency_ms', 0):.0f} ms"
                    )
                
                with metric_col4:
                    st.metric(
                        "Sources Used",
                        len(result.get("sources", []))
                    )
                
                # Sources
                st.markdown("### 📚 Sources")
                sources = result.get("sources", [])
                metadata_list = result.get("metadata", [])
                
                if sources:
                    for i, source in enumerate(sources, 1):
                        with st.expander(f"📄 Source {i}: {source}", expanded=False):
                            if metadata_list and i <= len(metadata_list):
                                meta = metadata_list[i-1]
                                
                                meta_col1, meta_col2 = st.columns(2)
                                
                                with meta_col1:
                                    if "department" in meta:
                                        st.text(f"📍 Department: {meta['department']}")
                                    if "category" in meta:
                                        st.text(f"🏷️ Category: {meta['category']}")
                                
                                with meta_col2:
                                    if "content" in meta:
                                        st.text(f"📝 Content preview:")
                                        st.caption(meta["content"][:200] + "...")
                                
                                # Show full metadata
                                with st.expander("🔍 Full Metadata"):
                                    st.json(meta)
                            else:
                                st.info("No metadata available for this source")
                else:
                    st.info("No sources found")
                
                # Debug Info (collapsible)
                with st.expander("🔧 Debug Information"):
                    st.json(result)
        
        elif search_button:
            st.warning("⚠️ Please enter a question")
    
    with col2:
        st.subheader("ℹ️ About PeruGuide AI")
        st.info("""
        **PeruGuide AI** uses advanced Retrieval-Augmented Generation (RAG) to provide accurate, 
        sourced information about Peru.
        
        **Features:**
        - 🤖 Multiple AI models
        - 📚 Comprehensive Peru knowledge base
        - 🔍 Source citations
        - ⚡ Fast retrieval
        - 🌐 Multilingual support
        """)
        
        st.subheader("🎯 Topics Covered")
        topics = [
            "🍽️ Gastronomy & Cuisine",
            "🏛️ History & Culture",
            "🗺️ Tourism & Destinations",
            "🎭 Festivals & Celebrations",
            "🌄 Geography & Nature",
            "🎨 Art & Handicrafts"
        ]
        
        for topic in topics:
            st.text(topic)
        
        st.divider()
        
        st.subheader("📈 System Stats")
        if health.get("status") == "healthy":
            components = health.get("components", {})
            num_vectors = components.get("num_vectors", "0")
            
            st.metric("Documents Indexed", num_vectors)
            st.metric("LLM Models", len(available_models))
            st.metric("API Version", health.get("version", "N/A"))


if __name__ == "__main__":
    main()
