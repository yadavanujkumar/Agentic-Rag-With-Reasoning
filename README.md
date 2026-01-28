# Agentic GraphRAG for Financial Fraud Detection

A portfolio-grade **Agentic GraphRAG** application that combines **Knowledge Graph reasoning** with **Vector-based semantic search** to detect financial fraud patterns. Built with **LangGraph**, **Neo4j**, and **GPT-4o**.

---

## 🎯 A. The Selected Domain & Pitch

### Domain: **Financial Fraud Detection**

### Why This Domain Requires Reasoning (Not Just Search)?

Financial fraud detection is the perfect use case for GraphRAG because:

1. **Fraud is About Relationships**: 
   - Fraudsters create networks of accounts, shell companies, and money mules
   - Detecting fraud requires understanding *connections* between entities, not just isolated facts
   - Traditional vector search can't traverse multi-hop relationships

2. **Complex Pattern Detection**:
   - **Circular Money Flows**: Money moving through multiple accounts and returning to origin (A→B→C→A)
   - **Layering**: Obscuring the source of funds through multiple transactions
   - **Structuring**: Breaking large amounts into smaller transactions to avoid detection
   - **Hidden Networks**: Multiple accounts sharing addresses, phone numbers, or owners

3. **Multi-Hop Reasoning**:
   - "Find all accounts indirectly connected to a suspicious entity"
   - "Trace the flow of funds across 3-5 intermediary accounts"
   - "Identify accounts controlled by the same person through shared infrastructure"

4. **Combines Structured + Unstructured Data**:
   - Graph: Transaction relationships, ownership structures, shared infrastructure
   - Vector DB: Fraud detection policies, compliance documents, risk indicators

**Why Graph > Vector DB**: 
- Vector search: "What documents mention money laundering?" ✅
- Graph reasoning: "Show me all paths from Account A to Account B through intermediaries" ✅
- **GraphRAG does both** and combines insights! 🚀

---

## 🧬 B. The Knowledge Graph Schema

### Node Labels

| Node Type | Properties | Description |
|-----------|-----------|-------------|
| **Account** | `account_id`, `account_type`, `balance`, `created_at`, `risk_score` | Bank accounts involved in transactions |
| **Person** | `person_id`, `name`, `ssn`, `date_of_birth`, `risk_level` | Individual account owners |
| **Company** | `company_id`, `name`, `ein`, `industry`, `is_suspicious` | Corporate entities |
| **Transaction** | `transaction_id`, `amount`, `timestamp`, `currency`, `status`, `flagged` | Individual transactions |
| **Address** | `address_id`, `street`, `city`, `state`, `zip_code`, `country` | Physical addresses |
| **PhoneNumber** | `phone_id`, `number`, `country_code`, `verified` | Contact information |

### Edge Types (Relationships)

| Edge Type | From | To | Properties | Description |
|-----------|------|-----|-----------|-------------|
| **OWNS** | Person/Company | Account | `ownership_percentage`, `since` | Ownership relationship |
| **SENT_MONEY** | Account | Account | `transaction_id`, `amount`, `timestamp`, `purpose` | Money transfer |
| **LOCATED_AT** | Person/Company | Address | `address_type`, `since` | Physical location |
| **HAS_PHONE** | Person/Company | PhoneNumber | `phone_type`, `since` | Contact method |
| **ASSOCIATED_WITH** | Person | Person | `relationship_type`, `confidence` | Known associations |

### Graph Schema Visualization

```
┌─────────┐     OWNS      ┌─────────┐
│ Person  │──────────────▶│ Account │
└────┬────┘               └────┬────┘
     │                         │
     │ LOCATED_AT              │ SENT_MONEY
     │                         │
     ▼                         ▼
┌─────────┐               ┌─────────┐
│ Address │               │ Account │
└─────────┘               └─────────┘
     ▲                         
     │                         
     │ LOCATED_AT              
     │                         
┌────┴────┐               
│ Person  │──────────────▶ (Circular flow detection)
└─────────┘     OWNS      
```

---

## 🏗️ C. The Core Agent Code

### Architecture

The system implements a **ReAct Agent** (Reasoning + Acting) with:

1. **LLM Brain**: GPT-4o for reasoning and decision-making
2. **Graph Tool**: `search_graph()` - Converts natural language to Cypher queries
3. **Vector Tool**: `search_docs()` - Semantic search over fraud detection policies
4. **LangGraph Orchestration**: Manages the Thought → Action → Observation loop

### Key Components

#### 1. **Graph Search Tool** (`search_graph`)
```python
@tool
def search_graph(question: str) -> str:
    """
    Search the fraud detection knowledge graph using natural language.
    
    Converts questions to Cypher queries for:
    - Finding paths between entities
    - Detecting circular money flows
    - Identifying shared infrastructure
    - Analyzing ownership patterns
    """
```

**Supported Query Patterns**:
- "Find paths between accounts" → Multi-hop traversal
- "Detect circular flows" → Cycle detection
- "Same owner" → Aggregation queries
- "High risk accounts" → Filtered searches
- "Shared infrastructure" → Pattern matching

#### 2. **Document Search Tool** (`search_docs`)
```python
@tool
def search_docs(question: str) -> str:
    """
    Search fraud detection documentation using semantic similarity.
    
    Uses FAISS vector store for:
    - Fraud detection policies
    - Compliance requirements
    - Risk indicators
    """
```

#### 3. **LangGraph ReAct Agent**
```python
def create_agent_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)  # LLM reasoning
    workflow.add_node("tools", ToolNode([search_graph, search_docs]))
    
    # Implements: Thought → Action → Observation loop
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {"tools": "tools", "end": END}
    )
```

### Usage

See `agent.py` for the complete implementation with:
- Full schema definitions
- Neo4j connection management
- Vector store initialization
- ReAct agent setup
- Example queries

---

## 💎 D. The "Golden Query"

### Complex Question #1: Hidden Money Mule Network

**Query:**
```
"Find all indirect connections between accounts that might indicate a money mule 
network. Look for accounts sharing common infrastructure like addresses or phone 
numbers. Then trace any money flows between these connected accounts and explain 
what makes these patterns suspicious according to fraud detection best practices."
```

**Why This Demonstrates Reasoning:**
1. **Multi-tool coordination**: Uses both `search_graph` AND `search_docs`
2. **Multi-hop traversal**: Finds indirect connections (not just direct)
3. **Pattern matching**: Identifies shared infrastructure
4. **Transaction analysis**: Traces money flows
5. **Knowledge synthesis**: Combines graph results with policy documents
6. **Explanation**: Provides reasoning based on fraud detection principles

### Other Golden Queries

**Query #2: Circular Money Flow Detection**
```
"Identify any circular money flows where funds move through multiple accounts 
and return to the origin. What are the red flags for this type of activity?"
```
- Combines: Cycle detection + policy lookup
- Demonstrates: Graph algorithms + semantic search

**Query #3: Risk Assessment with Context**
```
"Which accounts have the highest risk scores and what patterns of transactions 
do they exhibit? Also explain what makes these patterns suspicious according to 
fraud detection best practices."
```
- Combines: Aggregation + relationship analysis + documentation
- Demonstrates: Multi-source reasoning

**Query #4: Ownership Analysis**
```
"Find all persons who control multiple accounts. Are there any suspicious 
transaction patterns between these accounts that might indicate structuring 
or layering?"
```
- Combines: Ownership traversal + transaction analysis + fraud concepts
- Demonstrates: Complex pattern matching with domain knowledge

---

## 🚀 Setup & Installation

### Prerequisites

- Python 3.10+
- Neo4j 5.x (running locally or via Docker)
- OpenAI API key (or Google Gemini API key)

### 1. Clone the Repository

```bash
git clone https://github.com/yadavanujkumar/Agentic-Rag-With-Reasoning.git
cd Agentic-Rag-With-Reasoning
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start Neo4j

**Option A: Docker**
```bash
docker run \
    --name neo4j \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/password123 \
    neo4j:latest
```

**Option B: Local Installation**
- Download from [neo4j.com](https://neo4j.com/download/)
- Start the service
- Access browser at `http://localhost:7474`

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```bash
OPENAI_API_KEY=sk-your-key-here
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password123
```

### 5. Load Sample Data

```bash
python load_data.py
```

This creates:
- 6 Persons
- 2 Companies  
- 8 Accounts
- 4 Addresses
- 4 Phone Numbers
- **Multiple suspicious patterns** (circular flows, shared infrastructure, etc.)

### 6. Run the Agent

```bash
python agent.py
```

Or use programmatically:
```python
from agent import run_agent

answer = run_agent(
    "Find all indirect connections between accounts that might indicate a money mule network."
)
print(answer)
```

---

## 📊 Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Orchestration** | LangGraph | Agent workflow management |
| **LLM** | GPT-4o (OpenAI) | Reasoning and decision-making |
| **Graph DB** | Neo4j | Relationship storage and traversal |
| **Vector Store** | FAISS | Semantic document search |
| **Embeddings** | OpenAI Embeddings | Text vectorization |
| **Language** | Python 3.10+ | Core implementation |

---

## 🎓 Key Concepts

### What is GraphRAG?

**GraphRAG** = Graph Database + Retrieval-Augmented Generation

It combines:
1. **Graph databases** (Neo4j) for structured relationship reasoning
2. **Vector stores** (FAISS) for unstructured semantic search  
3. **LLMs** (GPT-4o) for natural language understanding and generation
4. **Agents** (LangGraph) for autonomous reasoning and tool use

### Why LangGraph?

- **State Management**: Tracks conversation history and tool results
- **Conditional Routing**: Decides when to use tools vs. provide answers
- **ReAct Pattern**: Implements Thought → Action → Observation loop
- **Composability**: Easy to add new tools and capabilities

### The ReAct Pattern

```
1. THOUGHT: "I need to find accounts with circular money flows"
2. ACTION: Call search_graph("circular money flows")
3. OBSERVATION: "Found 3 accounts in a circular pattern"
4. THOUGHT: "Now I need to understand why this is suspicious"
5. ACTION: Call search_docs("circular money flow red flags")
6. OBSERVATION: "Circular flows indicate layering and money laundering"
7. FINAL ANSWER: Synthesize both insights
```

---

## 🔒 Security Considerations

- Never commit `.env` files with real credentials
- Use environment variables for all sensitive configuration
- Implement proper authentication for production deployments
- Validate and sanitize all Cypher queries to prevent injection
- Use Neo4j's built-in security features (RBAC, encryption)

---

## 📈 Future Enhancements

- [ ] Add LLM-based Cypher query generation (vs. pattern matching)
- [ ] Implement real-time fraud detection alerts
- [ ] Add visualization dashboard for graph exploration
- [ ] Integrate with real banking APIs
- [ ] Add support for multiple LLM providers (Gemini, Claude)
- [ ] Implement advanced graph algorithms (PageRank, community detection)
- [ ] Add explainability features for fraud decisions

---

## 📝 License

MIT License - See [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

- Built with [LangChain](https://github.com/langchain-ai/langchain) and [LangGraph](https://github.com/langchain-ai/langgraph)
- Graph database powered by [Neo4j](https://neo4j.com/)
- LLM capabilities from [OpenAI](https://openai.com/)

---

## 📧 Contact

For questions or contributions, please open an issue on GitHub.

---

**Made with ❤️ for AI Engineers building portfolio-grade applications**