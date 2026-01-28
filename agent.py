"""
Agentic GraphRAG System for Financial Fraud Detection

This module implements a ReAct agent that combines:
1. Graph-based reasoning using Neo4j (for relationship traversal)
2. Vector-based semantic search (for document retrieval)

Domain: Financial Fraud Detection
Why Graph? - Fraud patterns emerge from RELATIONSHIPS between entities,
not just isolated facts. A graph allows multi-hop reasoning to detect
indirect connections, circular money flows, and hidden networks.
"""

import os
from typing import Annotated, Literal, TypedDict
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from neo4j import GraphDatabase
import faiss
import numpy as np

# Load environment variables
load_dotenv()

# ============================================================================
# DOMAIN: Financial Fraud Detection
# ============================================================================
# Nodes: Account, Transaction, Person, Company, Address, PhoneNumber
# Edges: OWNS, SENT_MONEY_TO, RECEIVED_MONEY_FROM, LOCATED_AT, HAS_PHONE
#
# Why GraphRAG?
# - Detect circular money flows (A->B->C->A)
# - Find hidden relationships between seemingly unrelated accounts
# - Identify money mule networks (multiple accounts controlled by one person)
# - Trace funds across multiple hops
# ============================================================================

# ============================================================================
# KNOWLEDGE GRAPH SCHEMA
# ============================================================================
GRAPH_SCHEMA = {
    "nodes": [
        {
            "label": "Account",
            "properties": ["account_id", "account_type", "balance", "created_at", "risk_score"]
        },
        {
            "label": "Person",
            "properties": ["person_id", "name", "ssn", "date_of_birth", "risk_level"]
        },
        {
            "label": "Company",
            "properties": ["company_id", "name", "ein", "industry", "is_suspicious"]
        },
        {
            "label": "Transaction",
            "properties": ["transaction_id", "amount", "timestamp", "currency", "status", "flagged"]
        },
        {
            "label": "Address",
            "properties": ["address_id", "street", "city", "state", "zip_code", "country"]
        },
        {
            "label": "PhoneNumber",
            "properties": ["phone_id", "number", "country_code", "verified"]
        }
    ],
    "edges": [
        {
            "type": "OWNS",
            "from": "Person/Company",
            "to": "Account",
            "properties": ["ownership_percentage", "since"]
        },
        {
            "type": "SENT_MONEY",
            "from": "Account",
            "to": "Account",
            "properties": ["transaction_id", "amount", "timestamp", "purpose"]
        },
        {
            "type": "LOCATED_AT",
            "from": "Person/Company",
            "to": "Address",
            "properties": ["address_type", "since"]
        },
        {
            "type": "HAS_PHONE",
            "from": "Person/Company",
            "to": "PhoneNumber",
            "properties": ["phone_type", "since"]
        },
        {
            "type": "ASSOCIATED_WITH",
            "from": "Person",
            "to": "Person",
            "properties": ["relationship_type", "confidence"]
        }
    ]
}

# ============================================================================
# Neo4j Connection
# ============================================================================
class Neo4jConnection:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def query(self, cypher: str, parameters: dict = None):
        """Execute a Cypher query and return results"""
        with self.driver.session() as session:
            result = session.run(cypher, parameters or {})
            return [record.data() for record in result]

# Initialize Neo4j connection
neo4j_conn = Neo4jConnection(
    uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    user=os.getenv("NEO4J_USERNAME", "neo4j"),
    password=os.getenv("NEO4J_PASSWORD", "")
)

# ============================================================================
# Vector Store for Document Search
# ============================================================================
class SimpleVectorStore:
    """Simple FAISS-based vector store for document retrieval"""
    
    def __init__(self, embedding_model):
        self.embedding_model = embedding_model
        self.documents = []
        self.index = None
    
    def add_documents(self, docs: list[str]):
        """Add documents to the vector store"""
        self.documents.extend(docs)
        embeddings = self.embedding_model.embed_documents(docs)
        embeddings_array = np.array(embeddings).astype('float32')
        
        if self.index is None:
            dimension = embeddings_array.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
        
        self.index.add(embeddings_array)
    
    def search(self, query: str, k: int = 3):
        """Search for similar documents"""
        if self.index is None or len(self.documents) == 0:
            return []
        
        query_embedding = self.embedding_model.embed_query(query)
        query_vector = np.array([query_embedding]).astype('float32')
        
        distances, indices = self.index.search(query_vector, min(k, len(self.documents)))
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.documents):
                results.append({
                    "content": self.documents[idx],
                    "score": float(distance)
                })
        return results

# Initialize embeddings and vector store
embeddings = OpenAIEmbeddings()
vector_store = SimpleVectorStore(embeddings)

# Sample fraud detection documents
FRAUD_DOCS = [
    "Money laundering often involves layering transactions across multiple accounts to obscure the source of funds.",
    "Structuring is the practice of splitting large transactions into smaller amounts to avoid reporting thresholds.",
    "Circular money flows where funds move through multiple accounts and return to the origin are highly suspicious.",
    "Multiple accounts sharing the same address or phone number may indicate a money mule network.",
    "Sudden large transactions from dormant accounts are red flags for account takeover fraud.",
    "Companies in high-risk industries (e.g., shell companies, cryptocurrency exchanges) require enhanced due diligence.",
    "Transactions to sanctioned countries or entities must be flagged and investigated immediately.",
    "Know Your Customer (KYC) violations include failing to verify customer identity or beneficial ownership.",
]

vector_store.add_documents(FRAUD_DOCS)

# ============================================================================
# TOOLS FOR THE AGENT
# ============================================================================

@tool
def search_graph(question: str) -> str:
    """
    Search the fraud detection knowledge graph.
    
    This tool uses pattern matching to convert common fraud detection questions 
    into Cypher queries for Neo4j. Supported query patterns include:
    - Finding connections and paths between entities
    - Detecting circular money flows
    - Identifying shared infrastructure (addresses, phones)
    - Analyzing ownership patterns
    - Finding high-risk accounts
    
    Args:
        question: Question about the graph (e.g., "find circular money flows")
    
    Returns:
        Results from the graph database
    """
    # In a production system, you would use an LLM to convert the question to Cypher
    # For this demo, we'll use pattern matching for common query types
    
    question_lower = question.lower()
    
    try:
        # Pattern 1: Find path between two accounts
        if "path" in question_lower or "connection" in question_lower:
            # Example: Find paths between accounts (limited to 3 hops for performance)
            cypher = """
            MATCH path = (a1:Account)-[*1..3]-(a2:Account)
            WHERE a1.account_id <> a2.account_id
            WITH a1, a2, path
            LIMIT 100
            RETURN a1.account_id as source, a2.account_id as target, 
                   length(path) as hops, 
                   [rel in relationships(path) | type(rel)] as relationship_types
            LIMIT 10
            """
        
        # Pattern 2: Find circular money flows
        elif "circular" in question_lower or "cycle" in question_lower:
            cypher = """
            MATCH path = (a:Account)-[:SENT_MONEY*3..4]->(a)
            WITH a, path, relationships(path) as rels
            LIMIT 10
            RETURN a.account_id as account, 
                   [n in nodes(path) | n.account_id] as cycle_path,
                   reduce(total = 0, r in rels | total + r.amount) as total_amount
            LIMIT 5
            """
        
        # Pattern 3: Find accounts owned by same person
        elif "same person" in question_lower or "same owner" in question_lower:
            cypher = """
            MATCH (p:Person)-[:OWNS]->(a:Account)
            WITH p, collect(a.account_id) as accounts
            WHERE size(accounts) > 1
            RETURN p.name as person, p.person_id as person_id, 
                   accounts, size(accounts) as account_count
            ORDER BY account_count DESC
            LIMIT 10
            """
        
        # Pattern 4: Find high-risk accounts
        elif "high risk" in question_lower or "suspicious" in question_lower:
            cypher = """
            MATCH (a:Account)
            WHERE a.risk_score > 0.7
            OPTIONAL MATCH (a)-[:SENT_MONEY]->(target:Account)
            RETURN a.account_id as account, a.risk_score as risk_score, 
                   a.balance as balance, count(target) as outgoing_transactions
            ORDER BY risk_score DESC
            LIMIT 10
            """
        
        # Pattern 5: Find shared infrastructure (addresses/phones)
        elif "shared" in question_lower or "common" in question_lower:
            cypher = """
            MATCH (p1:Person)-[:LOCATED_AT]->(addr:Address)<-[:LOCATED_AT]-(p2:Person)
            WHERE p1.person_id < p2.person_id
            RETURN p1.name as person1, p2.name as person2, 
                   addr.street as shared_address, addr.city as city
            LIMIT 10
            """
        
        # Default: Return graph statistics
        else:
            cypher = """
            MATCH (n)
            WITH labels(n) as label, count(*) as count
            RETURN label[0] as node_type, count
            ORDER BY count DESC
            """
        
        results = neo4j_conn.query(cypher)
        
        if not results:
            return "No results found in the graph database. The database may be empty or the query didn't match any patterns."
        
        return f"Found {len(results)} results:\n{results}"
    
    except Exception as e:
        return f"Error querying graph database: {str(e)}\nNote: Ensure Neo4j is running and populated with data."


@tool
def search_docs(question: str) -> str:
    """
    Search fraud detection documentation using semantic similarity.
    
    Use this for factual questions about:
    - Fraud detection policies and procedures
    - Compliance requirements
    - Risk indicators and red flags
    
    Args:
        question: Natural language question about fraud detection
    
    Returns:
        Relevant documentation excerpts
    """
    try:
        results = vector_store.search(question, k=3)
        
        if not results:
            return "No relevant documents found."
        
        output = "Relevant fraud detection information:\n\n"
        for i, result in enumerate(results, 1):
            output += f"{i}. {result['content']} (similarity score: {result['score']:.2f})\n"
        
        return output
    
    except Exception as e:
        return f"Error searching documents: {str(e)}"


# ============================================================================
# AGENT STATE & GRAPH
# ============================================================================

class AgentState(TypedDict):
    """State for the ReAct agent"""
    messages: list
    next: str


def should_continue(state: AgentState) -> Literal["tools", END]:
    """Determine whether to continue or end the agent loop"""
    messages = state["messages"]
    last_message = messages[-1]
    
    # If the last message has tool calls, continue to tools
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    
    # Otherwise, end
    return END


def call_model(state: AgentState):
    """Call the LLM with the current state"""
    messages = state["messages"]
    
    # Initialize the LLM
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Bind tools to the LLM
    tools = [search_graph, search_docs]
    llm_with_tools = llm.bind_tools(tools)
    
    # Add system message for ReAct prompting
    system_message = SystemMessage(content="""You are an expert fraud detection analyst with access to:
1. A knowledge graph (use search_graph) - for finding relationships, connections, and patterns
2. Documentation database (use search_docs) - for fraud detection policies and procedures

When answering questions:
- THINK step-by-step about what information you need
- Use search_graph for questions about relationships, connections, paths, or patterns
- Use search_docs for questions about policies, procedures, or general fraud indicators
- Combine insights from both sources when appropriate
- Always explain your reasoning

Follow the ReAct pattern:
1. Thought: Analyze what information you need
2. Action: Choose and execute the right tool
3. Observation: Examine the results
4. Repeat if needed, then provide your final answer
""")
    
    if len(messages) == 1:  # First call
        messages = [system_message] + messages
    
    response = llm_with_tools.invoke(messages)
    
    return {"messages": [response]}


# ============================================================================
# BUILD THE LANGGRAPH
# ============================================================================

def create_agent_graph():
    """Create the LangGraph agent"""
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode([search_graph, search_docs]))
    
    # Add edges
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END
        }
    )
    workflow.add_edge("tools", "agent")
    
    # Compile the graph
    app = workflow.compile()
    
    return app


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def run_agent(question: str, verbose: bool = True):
    """
    Run the agent with a question.
    
    Args:
        question: The question to ask the agent
        verbose: Whether to print intermediate steps
    
    Returns:
        The final answer from the agent
    """
    app = create_agent_graph()
    
    initial_state = {
        "messages": [HumanMessage(content=question)]
    }
    
    if verbose:
        print(f"\n{'='*80}")
        print(f"Question: {question}")
        print(f"{'='*80}\n")
    
    final_state = None
    for step_num, state in enumerate(app.stream(initial_state), 1):
        if verbose:
            print(f"\n--- Step {step_num} ---")
            for key, value in state.items():
                print(f"{key}: {value}")
        final_state = state
    
    # Extract final answer - get the last AIMessage content
    if final_state:
        for key in final_state:
            if "messages" in final_state[key]:
                messages = final_state[key]["messages"]
                # Get last AIMessage that doesn't have tool calls
                for msg in reversed(messages):
                    if isinstance(msg, AIMessage):
                        if not msg.tool_calls and msg.content:
                            return msg.content
    
    return "No answer generated"


# ============================================================================
# GOLDEN QUERIES - Examples demonstrating reasoning capabilities
# ============================================================================

GOLDEN_QUERIES = [
    {
        "query": "Find all indirect connections between accounts that might indicate a money mule network. Look for accounts sharing common infrastructure like addresses or phone numbers.",
        "why": "Demonstrates multi-hop graph traversal and pattern matching"
    },
    {
        "query": "Identify any circular money flows where funds move through multiple accounts and return to the origin. What are the red flags for this type of activity?",
        "why": "Combines graph cycle detection with policy knowledge"
    },
    {
        "query": "Which accounts have the highest risk scores and what patterns of transactions do they exhibit? Also explain what makes these patterns suspicious according to fraud detection best practices.",
        "why": "Integrates graph queries with document search for comprehensive analysis"
    },
    {
        "query": "Find all persons who control multiple accounts. Are there any suspicious transaction patterns between these accounts that might indicate structuring or layering?",
        "why": "Requires relationship traversal, aggregation, and connecting to fraud concepts"
    }
]


if __name__ == "__main__":
    # Example usage
    print("\n" + "="*80)
    print("AGENTIC GRAPHRAG FOR FINANCIAL FRAUD DETECTION")
    print("="*80)
    
    print("\nDomain: Financial Fraud Detection")
    print("\nWhy GraphRAG?")
    print("- Fraud is about RELATIONSHIPS, not isolated facts")
    print("- Need to trace money flows across multiple hops")
    print("- Identify hidden networks through shared infrastructure")
    print("- Detect circular patterns and unusual connections")
    
    print("\n" + "="*80)
    print("KNOWLEDGE GRAPH SCHEMA")
    print("="*80)
    print("\nNodes:", [node["label"] for node in GRAPH_SCHEMA["nodes"]])
    print("Edges:", [edge["type"] for edge in GRAPH_SCHEMA["edges"]])
    
    print("\n" + "="*80)
    print("GOLDEN QUERIES")
    print("="*80)
    for i, gq in enumerate(GOLDEN_QUERIES, 1):
        print(f"\n{i}. {gq['query']}")
        print(f"   Why: {gq['why']}")
    
    print("\n" + "="*80)
    print("\nTo run the agent, use:")
    print('  answer = run_agent("Your question here")')
    print("\nNote: Requires Neo4j running and OPENAI_API_KEY set in .env")
    print("="*80 + "\n")
