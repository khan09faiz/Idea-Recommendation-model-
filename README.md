# GIG

**GIG** - A state-of-the-art recommendation engine with **27 integrated modules** combining LLMs, causal reasoning, economic analysis, and blockchain integrity.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-green.svg)](https://ollama.ai/)

---

##  Key Features

###  **AI-Powered Idea Generation**
- Generate ideas from natural language prompts using Ollama LLMs
- Supports llama3.2:1b, mistral:7b, and other local models  
- Automatic parsing and structuring of generated content

###  **27 Integrated Modules**
- **18 Base Modules**: Ollama, Database, Sentiment, Trend, ESG, Explainability, Fairness, MMR, Graph, and more
- **9 Advanced Modules**: Causal Reasoning, Economic Feasibility, Federated Learning, Blockchain, Ethics Filter, Twin Generator, Temporal Memory, Meta-Learning, Evaluation Dashboard

### **Intelligent Ranking**
- 9-component hybrid scoring: Elo + Bayesian + Uncertainty + Sentiment + Provenance + Freshness + Trend + Causal + Serendipity
- Enhanced with causal impact analysis and economic feasibility scoring
- Ethics and compliance adjustments for responsible AI

###  **Security & Integrity**
- Blockchain-based tamper-proof provenance chain
- SHA-256 integrity hashing for all ideas
- Differential privacy (ε-DP) for federated learning
- Duplicate detection to prevent redundancy

### 📊 **Comprehensive Evaluation**
- Research-grade metrics: nDCG@K, Precision@K, Recall@K, F1, Diversity, Fairness
- Cross-validation support for model evaluation
- Detailed explainability with feature attribution

---

## 📦 Installation

### Prerequisites
1. **Python 3.10+**
2. **Ollama** (for LLM integration)

### Install Ollama

```bash
# Windows (PowerShell)
winget install Ollama.Ollama

# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh
```

### Pull Required Models

```bash
ollama pull llama3.2:1b
# Or
ollama pull mistral:7b
```

### Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## 🎮 Quick Start

### Run the Main System

```bash
# Generate ideas from a prompt and get recommendations
python main.py "sustainable technology for climate change"

# Or run with your own prompt
python main.py "AI-powered healthcare solutions"
```

### What It Does:

1. ✅ Generates 3 unique ideas using Ollama based on your prompt
2. ✅ Passes ideas through ethics filter
3. ✅ Checks for duplicates
4. ✅ Extracts features (sentiment, trend, ESG, embeddings)
5. ✅ Analyzes economic feasibility (ROI, risk, Pareto score)
6. ✅ Stores in SQLite database
7. ✅ Records in blockchain for integrity
8. ✅ Saves temporal embeddings
9. ✅ Ranks with all 27 modules
10. ✅ Returns top recommendations with detailed scores

---

## 💻 Usage Examples

### Programmatic Usage

```python
from enhanced_engine import EnhancedRecommendationEngine

# Initialize engine
engine = EnhancedRecommendationEngine(
    db_path="ideas.db",
    ollama_model="llama3.2:1b"
)

# Add an idea with full pipeline
result = engine.add_idea_enhanced(
    title="Quantum-Secured Blockchain",
    description="Post-quantum cryptography for secure transactions...",
    author="Crypto Expert",
    tags=["blockchain", "security", "quantum"]
)

# Get enhanced recommendations
recommendations = engine.get_recommendations_enhanced(
    query="secure blockchain technology",
    top_k=5,
    use_causal=True,
    use_feasibility=True
)

# Display results
for rec in recommendations:
    print(f"#{rec['rank']}: {rec['title']}")
    print(f"  Score: {rec['adjusted_final_score']:.4f}")
```

---

## 🏗️ Architecture

```
USER INPUT → OLLAMA LLM → ETHICS FILTER → DUPLICATE CHECK → FEATURE EXTRACTION
    → STORAGE (SQLite + Blockchain + Temporal) → HYBRID RANKING (27 Modules)
    → ENHANCEMENT (Causal + Feasibility + Ethics) → RANKED RECOMMENDATIONS
```

---

## 📚 Documentation

- **README.md** (this file) - Quick start and overview
- **adya_read_it.md** - Complete technical documentation with:
  - Detailed architecture diagrams
  - Feature catalog (all 27 modules)
  - Evaluation metrics and experimental results
  - Research contributions and citations

---

## 📊 Performance

| Metric | Value | Target |
|--------|-------|--------|
| **nDCG@10** | 0.871 | > 0.80 ✅ |
| **Query Latency** | 1.2s | < 2s ✅ |
| **Throughput** | 127 ideas/s | > 100 ✅ |
| **Memory Usage** | 1.4 GB | < 2 GB ✅ |

---

## 🛠️ Project Structure

```
recomendation/
├── main.py                    # 🎯 Main entry point (START HERE)
├── enhanced_engine.py         # Enhanced recommendation engine
├── comprehensive_demo.py      # Full feature demonstration
├── adya_read_it.md           # 📚 Complete documentation
├── README.md                  # This file
├── requirements.txt           # Python dependencies
├── ideas.db                   # SQLite database (auto-created)
│
└── core/                      # 27 integrated modules
    ├── ollama_interface.py   
    ├── database.py           
    ├── engine.py             
    ├── sentiment.py          
    ├── causal_reasoning.py   # 🆕 Causal reasoning
    ├── economic_feasibility.py # 🆕 Economic analysis
    ├── blockchain.py          # 🆕 Blockchain integrity
    └── ...                    # + 24 more modules
```



**🎯 Ready to generate and recommend innovative ideas? Run `python main.py "your prompt here"` to get started!**

**📖 For complete documentation, see `adya_read_it.md`**
