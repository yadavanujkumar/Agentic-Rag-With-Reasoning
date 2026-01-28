# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies (1 minute)
```bash
pip install -r requirements.txt
```

### Step 2: Start Neo4j (1 minute)
```bash
# Using Docker (recommended)
docker run --name neo4j \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/password123 \
    neo4j:latest

# Or download from https://neo4j.com/download/
```

### Step 3: Configure Environment (30 seconds)
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Step 4: Load Sample Data (1 minute)
```bash
python load_data.py
```

### Step 5: Run the Agent (30 seconds)
```bash
python example_usage.py
```

---

## 📖 What You Get

✅ **Complete GraphRAG System**
- LangGraph-based ReAct agent
- Neo4j knowledge graph with 30+ nodes
- FAISS vector store with fraud detection docs
- 4 pre-built "golden queries" demonstrating reasoning

✅ **Sample Fraud Patterns**
- Circular money flows (A→B→C→A)
- Multiple accounts owned by same person
- Shared infrastructure (addresses, phones)
- High-risk transactions and entities

✅ **Production-Ready Code**
- Error handling and logging
- Environment-based configuration
- Type hints and documentation
- Modular, extensible architecture

---

## 🎯 Try These Queries

### Query 1: Find Hidden Networks
```
"Find all indirect connections between accounts that might indicate 
a money mule network."
```

### Query 2: Detect Circular Flows
```
"Identify any circular money flows where funds move through multiple 
accounts and return to the origin."
```

### Query 3: Risk Analysis
```
"Which accounts have the highest risk scores and what patterns of 
transactions do they exhibit?"
```

### Query 4: Ownership Patterns
```
"Find all persons who control multiple accounts and analyze transaction 
patterns between them."
```

---

## 🔧 Troubleshooting

### "Connection refused" error
- Make sure Neo4j is running: `docker ps` or check Neo4j Browser at http://localhost:7474

### "Authentication failed" error  
- Check NEO4J_PASSWORD in .env matches your Neo4j password
- Default password in Docker command above is: `password123`

### "OpenAI API error"
- Verify OPENAI_API_KEY is set in .env
- Check your API key is valid at https://platform.openai.com/api-keys

### "No results found in database"
- Run `python load_data.py` to load sample data
- Verify data loaded: Open Neo4j Browser and run `MATCH (n) RETURN count(n)`

---

## 📚 Learn More

- **Full Documentation**: See [README.md](README.md)
- **Code Walkthrough**: See comments in [agent.py](agent.py)
- **Data Schema**: See [load_data.py](load_data.py)

---

## 🎓 Understanding the Code

### The Agent Loop
1. **User asks question** → LLM receives it
2. **LLM thinks** → "I need graph data for this"
3. **LLM acts** → Calls `search_graph` tool
4. **Tool executes** → Runs Cypher query on Neo4j
5. **LLM observes** → Receives graph results
6. **LLM thinks** → "I need policy context"
7. **LLM acts** → Calls `search_docs` tool
8. **Tool executes** → Runs vector search on FAISS
9. **LLM observes** → Receives relevant docs
10. **LLM answers** → Synthesizes insights from both sources

This is the **ReAct pattern**: Reasoning + Acting in a loop!

---

## 🌟 Next Steps

1. **Experiment**: Try your own fraud detection questions
2. **Extend**: Add new node types or relationship types
3. **Scale**: Load real transaction data
4. **Deploy**: Add a web UI or API endpoint
5. **Optimize**: Implement LLM-based Cypher generation

---

**Questions?** Open an issue on GitHub!
