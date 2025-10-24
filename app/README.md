# 🇵🇪 PeruGuide AI - Streamlit Frontend

Interactive web interface for querying Peru travel information using Retrieval-Augmented Generation (RAG).

## 🚀 Features

- **Interactive Query Interface**: Ask questions about Peru in natural language
- **Multiple LLM Models**: Choose from OpenAI, Anthropic, DeepSeek, and more
- **Source Citations**: Every answer includes references to source documents
- **Real-time Performance Metrics**: See retrieval and generation latency
- **Responsive Design**: Works on desktop and mobile devices
- **Example Queries**: Quick-start with pre-defined questions

## 📋 Prerequisites

- Python 3.11+
- Running PeruGuide RAG API (see main README)
- Streamlit

## 🔧 Installation

### 1. Install Dependencies

```bash
pip install streamlit requests
```

Or if using the project requirements:

```bash
pip install -r requirements.txt
```

### 2. Configure API URL

Create `.streamlit/secrets.toml`:

```bash
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml`:

```toml
API_URL = "http://localhost:8000"
```

## 🎯 Running Locally

### Start the API First

```bash
# Terminal 1: Start the API
cd /path/to/peruguide-rag
uvicorn src.api.main:app --reload
```

### Then Start Streamlit

```bash
# Terminal 2: Start Streamlit
cd app
streamlit run streamlit_app.py
```

The app will open at: http://localhost:8501

## 🌐 Deployment

### Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Set the main file path: `app/streamlit_app.py`
5. Add secrets in the Streamlit Cloud dashboard:
   ```toml
   API_URL = "https://your-api-url.com"
   ```

### Hugging Face Spaces

1. Create a new Space at [huggingface.co/spaces](https://huggingface.co/spaces)
2. Select "Streamlit" as the SDK
3. Upload your code
4. Configure secrets in Space settings

### Docker

```bash
# Build
docker build -t peruguide-streamlit -f Dockerfile.streamlit .

# Run
docker run -p 8501:8501 \
  -e API_URL=http://your-api:8000 \
  peruguide-streamlit
```

## 🎨 Customization

### Theme Colors

Edit `app/.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#D91E36"  # Peru flag red
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

### Example Queries

Edit `streamlit_app.py`, line ~140:

```python
example_queries = [
    "¿Cuáles son los platos típicos de Perú?",
    # Add your custom queries here
]
```

## 📊 Features Overview

### Main Interface

- **Query Input**: Large text area for questions
- **Model Selection**: Dropdown to choose LLM provider
- **Advanced Settings**: Configure retrieval parameters
- **Example Queries**: Click to load pre-defined questions

### Results Display

- **Answer Box**: Formatted response with citations
- **Performance Metrics**: 
  - Total latency
  - Retrieval time
  - Generation time
  - Number of sources
- **Source Citations**: Expandable cards with metadata
- **Debug Info**: Full API response (collapsible)

### Sidebar

- **API Health Check**: Real-time status monitoring
- **Component Status**: Individual component health
- **Settings**: Model and retrieval configuration
- **About Section**: App information
- **System Stats**: Document count, models available

## 🔍 Usage Examples

### Basic Query

1. Type your question in the text area
2. Click "🚀 Search"
3. View the answer with sources

### Advanced Configuration

1. Open sidebar settings
2. Select different LLM model
3. Adjust "Documents to retrieve" slider
4. Toggle source metadata

### Using Example Queries

1. Check sidebar "💡 Example Queries"
2. Click any example to load it
3. Click "🚀 Search" to execute

## 🐛 Troubleshooting

### API Connection Failed

**Error**: ❌ API Disconnected

**Solution**:
1. Verify API is running: `curl http://localhost:8000/api/v1/health`
2. Check `API_URL` in secrets.toml
3. Ensure no firewall blocking port 8000

### No Models Available

**Error**: Model selection shows only "openai"

**Solution**:
1. Check API is healthy
2. Verify `/api/v1/models` endpoint works
3. Restart Streamlit app

### Slow Performance

**Symptoms**: Long loading times

**Solutions**:
1. Reduce `top_k` in advanced settings
2. Use faster LLM model (e.g., OpenAI vs HuggingFace)
3. Check API server resources
4. Enable caching in API

## 📱 Screenshots

### Desktop View
![Desktop Interface](../docs/images/streamlit-desktop.png)

### Mobile View
![Mobile Interface](../docs/images/streamlit-mobile.png)

## 🔐 Security

- Never commit `.streamlit/secrets.toml` to git
- Use environment variables for production
- Enable HTTPS in production deployment
- Implement rate limiting on API side

## 📚 Documentation

- [Streamlit Docs](https://docs.streamlit.io)
- [API Documentation](http://localhost:8000/docs)
- [Main Project README](../README.md)

## 🤝 Contributing

See main [CONTRIBUTING.md](../CONTRIBUTING.md)

## 📄 License

See main [LICENSE](../LICENSE)

---

**Made with ❤️ for Peru** 🇵🇪
