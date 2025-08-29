# 🧠 Creative Idea Recommendation System

A **smart AI-powered recommendation system** that generates highly relevant, personalized product ideas by combining intelligent retrieval with targeted AI generation. Get only the ideas that truly match your specific needs and goals.

## ✨ Key Features

### 🎯 Smart Relevance Filtering
- **Intelligent Matching**: Only returns ideas that truly match your prompt and tags
- **Multi-Factor Scoring**: Analyzes title, description, and tag relevance 
- **Quality Over Quantity**: Better to get 3 perfect matches than 10 irrelevant ideas
- **No Generic Results**: Filters out unrelated recommendations automatically

### 🤖 Hybrid AI Architecture
- **Retrieval-Based Search**: FAISS + sentence-transformers for semantic similarity
- **Targeted AI Generation**: Mistral-7B via Ollama with strict relevance requirements
- **Smart Fallbacks**: Intelligent rule-based generation when Ollama unavailable
- **MMR Diversity**: Ensures diverse yet relevant recommendations

### 💾 Auto-Learning System
- **Auto-Save Generated Ideas**: AI-created ideas automatically added to database
- **Growing Knowledge Base**: System gets smarter with each use
- **Duplicate Prevention**: Smart filtering prevents duplicate ideas
- **Source Tracking**: Distinguishes between retrieved and AI-generated content

### 🔧 Technical Excellence
- **🧠 Embeddings**: `sentence-transformers/all-MiniLM-L6-v2`
- **🔍 Vector Search**: FAISS IndexFlatIP with numpy fallback
- **🤖 Generation**: Enhanced Ollama + Mistral-7B prompts
- **🌐 API**: FastAPI with Pydantic validation
- **🧪 Testing**: Comprehensive pytest suite with CI compatibility

## 🎯 Real Examples

### Example 1: Money-Generating Ideas
**Query**: `"Ideas that generate money based on current market"`  
**Tags**: `blockchain, logistics`

**Results** (Only relevant matches):
1. **🚚 AI-Powered Last-Mile Delivery Optimizer** - Smart routing generating revenue through subscriptions
2. **⛓️ Blockchain Supply Chain Transparency Platform** - Monetized through verification fees
3. **📊 Logistics Capacity Marketplace** - Revenue through dynamic pricing optimization

### Example 2: Healthcare Solutions  
**Query**: `"AI health solutions for elderly care"`  
**Tags**: `healthcare, elderly, monitoring`

**Results** (Highly targeted):
1. **👴 Elder Care Technology Revenue Model** - Comprehensive monitoring with subscription revenue
2. **🏥 AI Health Monitoring Revenue Stream** - Wearable integration with insurance partnerships
3. **📱 Telemedicine Platform for Rural Areas** - Consultation fees and subscription models

## 🚀 Quick Start Guide

### Option 1: Interactive Python Script (Recommended)
```bash
# Simple and user-friendly
python get_recommendations.py
```

### Option 2: Web Interface
```bash
# Start the API server
python -m uvicorn src.app:create_app --reload --port 8000

# Open web_interface.html in your browser
```

### Option 3: Direct API Usage
```python
import requests

response = requests.post("http://localhost:8000/recommend", json={
    "query": "blockchain ideas for supply chain transparency",
    "user_tags": ["blockchain", "supply-chain", "enterprise"],
    "k": 5,
    "diversify": True
})
```

## 🛠️ Installation & Setup

### Prerequisites
```bash
# Python 3.8+
python --version

# Optional: Install Ollama for enhanced AI generation
# Download from: https://ollama.ai/
# Then run: ollama pull mistral:7b
```

### Installation Steps
```bash
# 1. Clone the repository
git clone <your-repo-url>
cd Idea-Recommendation-model-

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate.ps1  # Windows
# or
source .venv/bin/activate   # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Optional: Enhanced ML capabilities
pip install sentence-transformers faiss-cpu
```

### 🚀 Ready to Use!
```bash
# Interactive recommendations
python get_recommendations.py

# Run demo
python demo.py

# Start API server
python -m uvicorn src.app:create_app --reload --port 8000
```

## 🎯 How to Use

### 💭 Where to Input Your Prompts

1. **🐍 Interactive Script** (Easiest):
   ```bash
   python get_recommendations.py
   ```
   Follow the prompts to enter your idea request and tags.

2. **🌐 Web Interface**:
   - Start the API server (see above)
   - Open `web_interface.html` in your browser
   - Enter your prompt and tags in the web form

3. **🔌 API Calls**:
   ```python
   import requests
   
   # Make a request
   response = requests.post("http://localhost:8000/recommend", json={
       "query": "Your idea request here",
       "user_tags": ["tag1", "tag2"],  # Optional but recommended
       "k": 5,  # Number of results
       "diversify": True
   })
   
   ideas = response.json()
   ```

### 📊 Where to See Your Results

**Your recommendations appear in:**
- **📱 Console Output**: Formatted text with scores and descriptions
- **🌐 Web Interface**: Beautiful cards with full details
- **📁 API Response**: Complete JSON with metadata
- **💾 Database**: Auto-saved AI-generated ideas in `data/idea.json`

### 🎯 Pro Tips for Better Results

1. **Be Specific**: Instead of "AI ideas", try "AI solutions for small business accounting"
2. **Use Relevant Tags**: Include tags like "blockchain", "healthcare", "revenue", "b2b"
3. **Include Intent**: Mention if you want "money-generating", "cost-saving", or "efficiency" ideas
4. **Specify Domain**: Add context like "current market", "emerging trends", or "enterprise"

**Example Good Prompts:**
- ✅ "Blockchain solutions for supply chain transparency that generate revenue"
- ✅ "AI-powered healthcare tools for elderly monitoring and care"
- ✅ "Current market opportunities in logistics automation for SMBs"

**Example Poor Prompts:**
- ❌ "Give me some ideas"
- ❌ "Technology stuff"
- ❌ "Business things"
## 🧠 System Architecture

### 🔄 How It Works

```
User Input → Relevance Filter → Hybrid Processing → Smart Ranking → Results
    ↓             ↓                    ↓              ↓           ↓
"blockchain    Check tags &     Retrieval +     MMR Diversity   Only relevant
logistics      keywords         AI Generation    + Scoring      ideas returned
money ideas"   matching         
```

### 🎯 Smart Relevance System

The system uses a **multi-factor relevance scoring** to ensure you only get ideas that truly match:

1. **📝 Title Matching (40%)**: Keywords from your prompt in idea titles
2. **📄 Description Matching (30%)**: Semantic relevance in descriptions  
3. **🏷️ Tag Matching (30%)**: Alignment with your specified tags
4. **🎯 Semantic Bonuses**: Extra scoring for money/tech/domain alignment

**Minimum Relevance Threshold**: 0.3 (30%) - Ideas below this are filtered out

### 🤖 AI Generation Modes

1. **🔥 Ollama + Mistral-7B** (When available):
   - Full AI creativity with strict relevance prompts
   - User tags integrated into generation prompts
   - High-quality, contextual ideas

2. **🧠 Smart Fallback** (When Ollama unavailable):
   - Rule-based targeted generation
   - Tag-specific idea templates
   - Context-aware monetization strategies

### 💾 Auto-Learning Database

- **📈 Growing Knowledge**: AI-generated ideas automatically saved to `data/idea.json`
- **🔄 Duplicate Prevention**: Smart filtering prevents redundant entries
- **📊 Source Tracking**: Clear distinction between retrieved vs generated ideas
- **🎯 Future Relevance**: Saved ideas improve future recommendations

## 🔧 Configuration & Customization

### Key Settings (`src/config.py`)

```python
# Retrieval settings
RETRIEVAL_K = 10          # Ideas to retrieve from database
ALPHA = 0.7               # Weight for similarity scores  
GAMMA = 0.3               # Weight for metadata boosts

# Generation settings
OLLAMA_MODEL = "mistral"  # LLM model for generation
EMBED_MODEL = "all-MiniLM-L6-v2"  # Embedding model

# Relevance filtering
MIN_RELEVANCE_SCORE = 0.3  # Minimum relevance threshold
```

### 🎛️ Customize for Your Needs

**For More Creative Ideas**: Increase generation count, adjust MMR lambda
**For Stricter Relevance**: Increase `MIN_RELEVANCE_SCORE` to 0.4 or 0.5
**For Faster Performance**: Use numpy fallback instead of FAISS
**For Domain-Specific**: Add custom keywords to fallback generation

## 🧪 Testing & Validation

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Test specific functionality  
pytest tests/test_recommender.py -v
```

## 🚨 Troubleshooting

### Common Issues & Solutions

**❌ "No relevant ideas found"**
- ✅ Make your query more specific
- ✅ Add relevant tags that match your domain
- ✅ Lower the relevance threshold in config (if needed)
- ✅ Check that your tags match existing ideas in the database

**❌ "Ollama CLI not found"**
- ✅ Install Ollama from https://ollama.ai/
- ✅ Run `ollama pull mistral:7b`
- ✅ Restart your terminal/PowerShell
- ✅ System works with intelligent fallback generation anyway

**❌ "FAISS installation fails"**
- ✅ System automatically falls back to numpy-based search
- ✅ Install manually: `pip install faiss-cpu`
- ✅ Performance impact is minimal for small datasets

**❌ "Import errors"**
- ✅ Ensure all dependencies installed: `pip install -r requirements.txt`
- ✅ Check Python version >= 3.8
- ✅ Activate virtual environment

### Performance Tips

1. **🔥 For Best Results**: Install Ollama + Mistral for creative AI generation
2. **⚡ For Speed**: Use FAISS instead of numpy fallback
3. **🎯 For Relevance**: Be specific with prompts and use relevant tags
4. **💾 For Efficiency**: Let the system learn - generated ideas improve future results

## 📁 Project Structure

```
Idea-Recommendation-model-/
├── 📄 README.md                    # This comprehensive guide
├── 📄 requirements.txt             # Python dependencies
├── 🐍 get_recommendations.py       # Interactive user script
├── 🌐 web_interface.html          # Browser-based interface
├── 🧪 demo.py                     # System demonstration
├── 📁 src/                        # Core system code
│   ├── 🧠 app.py                  # Main recommendation logic + API
│   ├── ⚙️ config.py               # Configuration & models
│   ├── 🔧 utils.py                # ML utilities & algorithms
│   └── 📊 data_processing.py      # Data handling & auto-save
├── 📁 data/                       # Knowledge base
│   └── 💡 idea.json               # Seed ideas (auto-updated)
└── 📁 tests/                      # Test suite
    ├── 🧪 test_recommender.py     # Integration tests
    └── 🧪 test_recommender_mock.py # Mock-based tests
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-improvement`
3. **Add tests** for new functionality
4. **Ensure all tests pass**: `pytest`
5. **Submit pull request**

### Development Guidelines

- **🎯 Relevance First**: Any new features should maintain or improve idea relevance
- **🧪 Test Coverage**: Add tests for new functionality
- **📝 Documentation**: Update README for significant changes
- **🔧 Backward Compatibility**: Maintain API compatibility

## 🎖️ Acknowledgments

- **🤗 sentence-transformers**: For semantic text embeddings
- **⚡ FAISS**: For efficient similarity search
- **🦙 Ollama**: For local LLM inference
- **🚀 FastAPI**: For robust API framework
- **🧠 Mistral-7B**: For creative idea generation

## 🆕 Recent Updates (v2.0)

- ✅ **Smart Relevance Filtering**: Only relevant ideas returned
- ✅ **Enhanced AI Prompts**: Targeted generation with user tags
- ✅ **Auto-Save System**: Generated ideas automatically stored
- ✅ **Improved Fallbacks**: Better rule-based generation
- ✅ **Quality Controls**: Minimum relevance thresholds
- ✅ **User-Friendly Interfaces**: Multiple ways to interact
- ✅ **GitHub Ready**: Clean structure and documentation

---

**🎯 Built for**: Entrepreneurs, product managers, researchers, and innovators seeking AI-powered creative ideation with guaranteed relevance.

**💡 Perfect for**: Revenue generation ideas, market opportunity analysis, technology innovation, and domain-specific brainstorming.

**🚀 Ready to deploy**: Clean, tested, and production-ready codebase!

## 📄 License

This project is open-source and available under the MIT License.

## 🙏 Acknowledgments

- **sentence-transformers**: For semantic embeddings
- **FAISS**: For efficient similarity search
- **Ollama**: For local LLM inference
- **FastAPI**: For the web framework
- **Mistral-7B**: For creative idea generation

## 🆕 Latest Updates

- ✅ **Auto-Save Feature**: AI-generated ideas automatically saved to `data/idea.json`
- ✅ **User-Friendly Interfaces**: Added `get_recommendations.py` script and `web_interface.html`
- ✅ **Enhanced Documentation**: Comprehensive README with clear usage instructions
- ✅ **GitHub Ready**: Cleaned up unnecessary files and added proper `.gitignore`

---

**Built for**: Innovation teams, product managers, researchers, and anyone seeking AI-powered creative ideation.

**Ready to deploy**: This repository is clean and ready for GitHub upload!

**Perfect for**: Brainstorming sessions, product discovery, market research, and creative problem-solving.
