# Mortgage Application and Processing System

**Production-ready LangGraph-based multi-agent system for intelligent mortgage processing**

[![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)](https://github.com/yourusername/mortgage-agents)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green.svg)](https://langchain-ai.github.io/langgraph/)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## 🚀 Overview

An enterprise-grade agentic AI system that automates the complete mortgage application workflow from initial inquiry to final underwriting decision. Built on **LangGraph** with intelligent routing, **Model Context Protocol (MCP)** integration, and **Neo4j-powered business rules**.

### Key Features

- ✅ **5 Specialized Agents** with intelligent LLM-powered routing
- ✅ **Zero Hardcoded Rules** - All business logic in Neo4j (1,313+ nodes)
- ✅ **MCP Integration** - Credit check & business rules via MCP servers
- ✅ **Automatic URLA 1003** - Industry-standard form generation
- ✅ **Real-time Credit Checks** - Identity verification with confidence scoring
- ✅ **Document Processing** - PDF extraction & OCR support
- ✅ **Production Ready** - Error handling, logging, caching, observability

---

## 🏗️ Architecture

### System Design

```
                    ┌─────────────────────────────────────────┐
                    │   USER INPUT (Mortgage System Chat)     │
                    └──────────────────┬──────────────────────┘
                                       │
                                       ▼
        ┌──────────────────────────────────────────────────────────────┐
        │         LangGraph Multi-Agent Router (graph.py)              │
        │         Structured Output Classification                     │
        └──────────────────────┬──────────────────────────────────────┘
                               │
                               │ Calls LlamaStack for classification
                               ▼
                    ┌──────────────────────┐
                    │   LlamaStack LLM     │◄──────────────────────┐
                    │   Chat Completions   │                       │
                    │   API                │                       │
                    │                      │                       │
                    │ Llama 4 Scout 17B    │                       │
                    │ (W4A16 Quantized)    │                       │
                    │ OpenAI Compatible    │                       │
                    └──────────┬───────────┘                       │
                               │                                   │
                               │ Returns RouteClassification       │
                               ▼                                   │
        ┌──────────────────────────────────────────────────────┐  │
        │              Router routes to agent                  │  │
        └──────┬──────────┬──────────┬──────────┬──────────┬──┘  │
               │          │          │          │          │     │
               ▼          ▼          ▼          ▼          ▼     │
        ┌──────────┐┌──────────┐┌─────────┐┌─────────┐┌──────────┐
        │Mortgage  ││Application││Document ││Appraisal││Underwriting│
        │Advisor   ││  Agent    ││  Agent  ││  Agent  ││  Agent   ││
        │(ReAct)   ││ (ReAct)   ││ (ReAct) ││ (ReAct) ││ (ReAct)  ││
        └────┬─────┘└─────┬─────┘└────┬────┘└────┬────┘└─────┬────┘│
             │            │           │          │           │     │
             └────────────┴───────────┴──────────┴───────────┘     │
                             │                                   │
                             │ ALL agents call LlamaStack        │
                             │ (reasoning, tool selection,       │
                             │  response formatting)             │
                             └───────────────────────────────────┘
                                            │
             ┌──────────────────────────────┼──────────────────────┐
             │                              │                      │
             │  Agents call tools:          │                      │
             │                              │                      │
             ▼                              ▼                      ▼
    ┌──────────────┐              ┌──────────────┐      ┌──────────────┐
    │  Credit MCP  │              │  Neo4j MCP   │      │  SQLite DB   │
    │   Server     │              │   Server     │      │              │
    │              │              │              │      │ Applications │
    │ Tools:       │              │ Tools:       │      │ URLA Forms   │
    │ • credit_    │              │ • read_neo4j │      │ Documents    │
    │   score()    │              │   _cypher()  │      │              │
    │ • verify_    │              │ • write_neo4j│      │ (Direct @tool│
    │   identity() │              │   _cypher()  │      │  access, no  │
    │ • credit_    │              │ • get_neo4j_ │      │  MCP)        │
    │   report()   │              │   schema()   │      │              │
    └──────────────┘              └──────┬───────┘      └──────────────┘
                                         │
                                         ▼
                                ┌──────────────┐
                                │   Neo4j DB   │
                                │              │
                                │ 1,313+ nodes │
                                │ Business     │
                                │ Rules        │
                                └──────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│ HOW ReAct AGENTS WORK (create_react_agent pattern):                 │
│                                                                      │
│ Agent = LLM + Tools + Prompt                                         │
│                                                                      │
│ The LLM operates in a LOOP:                                          │
│                                                                      │
│ 1. Agent → LlamaStack Chat Completions API                           │
│    Input: system_prompt + user_message + available_tools            │
│    Output: tool_call OR final_answer                                 │
│                                                                      │
│ 2. IF tool_call returned:                                            │
│    a) Execute tool (MCP server or direct function)                   │
│    b) Get observation (tool result)                                  │
│    c) Agent → LlamaStack again (with tool result added to context)   │
│    d) LLM decides: call another tool OR give final answer            │
│    e) REPEAT until LLM returns final answer (no more tool_calls)     │
│                                                                      │
│ 3. IF final_answer returned: Loop stops, return to user              │
│                                                                      │
│ Router → LlamaStack: 1x (classify intent via structured output)     │
│ Agent → LlamaStack: 3-10x (ReAct loop until task complete)          │
│                                                                      │
│ Per the LangGraph docs: "The LLM operates in a loop. In each        │
│ iteration, it selects a tool to invoke, provides input, receives    │
│ the result (observation), and uses that observation to inform the   │
│ next action. The loop continues until a stopping condition is met." │
└──────────────────────────────────────────────────────────────────────┘

Data Flow (Detailed):
━━━━━━━━━━━━━━━━━━━━
1. User input → Router (LangGraph structured output)

2. Router → LlamaStack Chat Completions API
   Request: {messages: [system, user], tools: [], response_format: RouteClassification}
   Response: {agent: "underwriting_agent"}

3. Router → Routes to UnderwritingAgent (ReAct agent)

4. ReAct Agent LOOP begins:
   
   Iteration 1:
   ├─ Agent → LlamaStack Chat Completions API
   │  Request: {messages: [system_prompt, user_message], tools: [all agent tools]}
   │  Response: {tool_calls: [{name: "get_stored_application_data", args: {...}}]}
   │
   ├─ Agent executes tool: get_stored_application_data()
   │  Result: "Application data: SSN=123-45-6789, Name=John Doe..."
   │
   ├─ Observation added to message history
   
   Iteration 2:
   ├─ Agent → LlamaStack Chat Completions API
   │  Request: {messages: [previous + tool_result], tools: [all agent tools]}
   │  Response: {tool_calls: [{name: "credit_score", args: {ssn: "123-45-6789"}}]}
   │
   ├─ Agent executes MCP tool: credit_score() via Credit MCP Server
   │  Result: "Credit Score: 728"
   │
   ├─ Observation added to message history
   
   Iteration 3:
   ├─ Agent → LlamaStack Chat Completions API
   │  Request: {messages: [previous + tool_result], tools: [all agent tools]}
   │  Response: {tool_calls: [{name: "read_neo4j_cypher", args: {query: "MATCH..."}}]}
   │
   ├─ Agent executes MCP tool: read_neo4j_cypher() via Neo4j MCP Server
   │  Result: "DTI limit: 43%"
   │
   ├─ Observation added to message history
   
   Iteration 4:
   ├─ Agent → LlamaStack Chat Completions API
   │  Request: {messages: [previous + tool_result], tools: [all agent tools]}
   │  Response: {content: "UNDERWRITING DECISION: APPROVED...", tool_calls: null}
   │
   └─ No more tool_calls → Loop stops

5. Agent → User (final response)

Key Components (Per LangGraph Docs):
─────────────────────────────────────
• Agent = LLM + Tools + Prompt (from create_react_agent)
• LangGraph: Framework providing create_react_agent (implements ReAct loop)
• LlamaStack: LLM provider via OpenAI-compatible chat completions API
  - Called by router for classification (1x per request)
  - Called by agents in loop (3-10x per request until task complete)
• ReAct Pattern: Reasoning + Acting loop
  - LLM decides action → executes tool → LLM sees result → decides next action
  - Continues until LLM returns final answer (no more tool_calls)
• Tools (3 types):
  1. MCP tools: Credit checks (Credit MCP), Business rules (Neo4j MCP)
  2. Direct tools: SQLite access via @tool decorator (no MCP)
  3. Operational tools: Pure logic (DTI calculation, risk analysis)
```

### Technology Stack

| Component | Technology | Purpose | Access Method |
|-----------|-----------|---------|---------------|
| **Framework** | LangGraph 0.2+ | Multi-agent orchestration, ReAct pattern | N/A |
| **LLM** | LlamaStack (Llama 4 Scout 17B) | OpenAI-compatible chat completions API | Direct HTTP calls |
| **MCP Integration** | FastMCP + LangChain Adapters | External service integration | MCP Protocol |
| **Business Rules** | Neo4j (1,313+ nodes) | DTI limits, credit requirements, loan programs | **Via Neo4j MCP** |
| **Application Data** | SQLite | Applications, URLA forms, documents | **Direct @tool calls** |
| **File Processing** | PyPDF2, pytesseract | PDF extraction, OCR | Direct Python libs |
| **Deployment** | OpenShift/RHOAI | Container orchestration | N/A |

---

## 🤖 LLM Integration - LlamaStack

### Overview

All agents in this system use **LlamaStack's OpenAI-compatible Chat Completions API** with the **Llama 4 Scout 17B** model pre-registered on the LlamaStack API server.

### Configuration

```yaml
# app/utils/config.yaml
llm:
  base_url: "https://lss-lss.apps.prod.rhoai.rh-aiservices-bu.com/v1/openai/v1"
  api_key: "not-needed"  # LlamaStack doesn't require API key
  default_model: "llama-4-scout-17b-16e-w4a16"

langgraph:
  model: "llama-4-scout-17b-16e-w4a16"
  temperature: 0.7
  max_tokens: 2000
```

### Model Details

| Property | Value |
|----------|-------|
| **Model Name** | `llama-4-scout-17b-16e-w4a16` |
| **Parameters** | 17 Billion |
| **Quantization** | W4A16 (4-bit weights, 16-bit activations) |
| **API Endpoint** | `https://lss-lss.apps.prod.rhoai.rh-aiservices-bu.com/v1/openai/v1` |
| **Protocol** | OpenAI-compatible REST API |
| **Temperature** | 0.7 (balanced creativity) |
| **Max Tokens** | 2000 per response |
| **Context Window** | Extended (supports long conversations) |

### How It's Used

```python
# From app/utils/llm_factory.py
from langchain_openai import ChatOpenAI

def get_llm():
    """Get centralized LLM instance for all agents."""
    config = AppConfig.load()
    
    return ChatOpenAI(
        base_url=config.llm.base_url,
        api_key=config.llm.api_key,
        model=config.llm.default_model,
        temperature=0.7,
        max_tokens=2000
    )

# All agents use this factory
# From underwriting_agent/agent.py
llm = get_llm()  # Returns LlamaStack-backed ChatOpenAI instance
agent = create_react_agent(model=llm, tools=tools, prompt=system_prompt)
```

### LlamaStack Features Used

1. **Chat Completions API**: All agent conversations and reasoning
2. **Function Calling**: Tool execution via OpenAI function calling format
3. **Structured Output**: Router classification with Pydantic models
4. **Streaming** (optional): Real-time token streaming for responses

### Key Benefits

- ✅ **OpenAI Compatible**: Drop-in replacement for OpenAI API
- ✅ **No API Key Required**: Simplified authentication
- ✅ **Self-Hosted**: Full control over model deployment
- ✅ **Quantized Model**: W4A16 quantization for efficient inference
- ✅ **Extended Context**: Supports long conversation histories

### Example API Call

```python
# What happens under the hood when an agent executes
import requests

response = requests.post(
    "https://lss-lss.apps.prod.rhoai.rh-aiservices-bu.com/v1/openai/v1/chat/completions",
    json={
        "model": "llama-4-scout-17b-16e-w4a16",
        "messages": [
            {"role": "system", "content": "You are an underwriting agent..."},
            {"role": "user", "content": "Calculate DTI for..."}
        ],
        "tools": [...],  # Available tools for function calling
        "temperature": 0.7,
        "max_tokens": 2000
    }
)
```

### Model Registration

The model `llama-4-scout-17b-16e-w4a16` is pre-registered with the LlamaStack API server running on OpenShift/RHOAI:

```bash
# Model registered using LlamaStack CLI (already done)
llamastack models register \
  --name llama-4-scout-17b-16e-w4a16 \
  --provider meta \
  --quantization w4a16 \
  --parameters 17b
```

> **Note**: The model is already registered and available at the configured endpoint. No additional setup needed for development.

---

## 🤖 The 5 Specialized Agents

### 1. **Mortgage Advisor Agent**
**Purpose:** Loan recommendations, qualification guidance, program comparison

**Tools:**
- 3 Core tools: `explain_loan_programs`, `recommend_loan_program`, `check_qualification_requirements`
- Credit MCP tools: Dynamic credit data access
- Neo4j MCP tools: Business rules queries

**Use Cases:**
- "What loan programs am I eligible for?"
- "What credit score do I need for an FHA loan?"
- "Compare conventional vs. FHA for my situation"

---

### 2. **Application Agent**
**Purpose:** Application intake, data validation, URLA 1003 generation

**Tools:**
- 5 Core tools: `receive_mortgage_application`, `generate_urla_1003_form`, `track_application_status`, `check_application_completeness`, `perform_initial_qualification`
- Shared application data tools
- MCP tools for validation

**Special Features:**
- ✅ Automatic URLA Form 1003 generation after submission
- ✅ Real application IDs: `APP_YYYYMMDD_HHMMSS_XXX`
- ✅ SQLite persistence

**Use Cases:**
- "I want to apply for a mortgage"
- "Check status of application APP_20241020_123456"
- "Generate URLA form for my application"

---

### 3. **Document Agent**
**Purpose:** Document processing, validation, extraction

**Tools:**
- 5 Core tools: `process_uploaded_document`, `extract_document_data`, `verify_document_completeness`, `validate_urla_form`, `get_document_status`
- File processing: PDF (PyPDF2), Images (pytesseract OCR)
- Neo4j validation rules

**Supported Documents:**
- W-2 forms, pay stubs, bank statements
- Tax returns, ID documents
- PDF and image formats

**Use Cases:**
- "Here's my W-2 and pay stubs" [file uploads]
- "Process these documents for APP_12345"
- "What documents are still missing?"

---

### 4. **Appraisal Agent**
**Purpose:** Property valuation, market analysis, comparables

**Tools:**
- 5 Core tools: `analyze_property_value`, `find_comparable_sales`, `assess_property_condition`, `evaluate_market_conditions`, `review_appraisal_report`
- Neo4j property rules

**Use Cases:**
- "What's my property worth?"
- "Find comparable sales in my area"
- "Analyze market conditions for Austin, TX"

---

### 5. **Underwriting Agent** ⚡ Most Complex
**Purpose:** Credit risk analysis, underwriting decisions, final approval

**Tools:**
- 5 Core tools: `analyze_credit_risk`, `calculate_debt_to_income`, `evaluate_income_sources`, `run_aus_check`, `make_underwriting_decision`
- Credit MCP: `credit_score`, `verify_identity`, `credit_report`
- Neo4j MCP: Business rules queries
- Shared application data tools

**Automatic Workflow:**
```
1. get_stored_application_data() → Retrieve SSN, name, DOB
2. credit_score() + verify_identity() → Real credit bureau data
3. get_neo4j_schema() + read_neo4j_cypher() → Query DTI limits, credit requirements
4. calculate_debt_to_income() → Pure math calculation
5. analyze_credit_risk() → Risk assessment
6. make_underwriting_decision() → Final decision
```

**Critical Policies (Prompt-Enforced):**
- ⚠️ **Identity verification failure = AUTOMATIC DENIAL** (no exceptions)
- ⚠️ **MCP credit score > Self-reported score** (data source priority)
- ⚠️ **Automatic credit check** (no user prompt needed)
- ⚠️ **Structured decision output** (consistent formatting)

**Use Cases:**
- "Please proceed with underwriting for APP_12345"
- "Calculate my DTI ratio"
- "Analyze credit risk for this application"

---

## 🔌 MCP Integration Architecture

### What is MCP?

**Model Context Protocol (MCP)** is a standardized protocol for connecting AI models to external data sources and tools. Our system uses MCP to separate operational logic from business rules and external services.

### MCP Server #1: Credit Check
```yaml
URL: https://credit-check-mcp-rh12026.apps.prod.rhoai.rh-aiservices-bu.com/mcp
Transport: streamable_http
Framework: FastMCP
```

**Tools Exposed:**
- `credit_score(ssn, first_name, last_name, date_of_birth)` → Real credit bureau data
- `verify_identity(...)` → Identity verification (85-95% confidence)
- `credit_report(...)` → Full credit history

**Features:**
- ✅ Module-level caching (~500ms latency reduction)
- ✅ Async/sync context handling
- ✅ Graceful degradation if unavailable

### MCP Server #2: Neo4j Business Rules
```yaml
URL: https://mcp-mortgage-business-rules-route-rh12026.apps.prod...
Transport: streamable_http
Database: Neo4j with 1,313+ business rule nodes
```

**Tools Exposed:**
- `get_neo4j_schema()` → Dynamic schema discovery
- `read_neo4j_cypher(query)` → Query DTI limits, credit requirements, LTV ratios
- `write_neo4j_cypher(query)` → Update business rules

**Node Types (30+):**
- `BusinessRule`: DTI limits, LTV ratios, reserve requirements
- `CreditScoreRange`: Score categories (Excellent, Good, Fair, Poor)
- `UnderwritingRule`: Approval criteria, compensating factors
- `LoanProgram`: FHA, VA, Conventional, USDA, Jumbo
- `ComplianceRule`: Regulatory requirements
- And 25+ more...

**Why This Matters:**
```diff
- ❌ Hardcoded: if dti < 43% then "approved"
+ ✅ Data-Driven: MATCH (n:BusinessRule {rule_type: 'DTI'}) WHERE n.loan_program = 'conventional' RETURN n.max_ratio
```

---

## 🔄 Complete E2E Workflow Example

```
1. USER → "I want to apply for a mortgage..."
   ├─ ROUTER → LLM classification → APPLICATION_AGENT
   └─ APPLICATION_AGENT executes:
      ├─ receive_mortgage_application() → Stores in SQLite
      ├─ generate_urla_1003_form() → Auto-generates URLA
      └─ Returns: APP_20251020_012656_MIK

2. USER → "Here's my W-2..." [uploads PDF]
   ├─ ROUTER → Detects "UPLOADED DOCUMENTS" → DOCUMENT_AGENT
   └─ DOCUMENT_AGENT executes:
      ├─ extract_document_data() → PyPDF2 extraction
      ├─ process_uploaded_document() → Validates against Neo4j rules
      └─ Updates status: DOCUMENT_COLLECTION → CREDIT_REVIEW

3. USER → "Please proceed with underwriting for APP_20251020_012656_MIK"
   ├─ ROUTER → Routes to UNDERWRITING_AGENT
   └─ UNDERWRITING_AGENT (AUTOMATIC WORKFLOW):
      ├─ get_stored_application_data() → Retrieves SSN, name, DOB
      ├─ credit_score() → Credit MCP returns 728
      ├─ verify_identity() → Credit MCP returns "Verified: True, Confidence: 85%"
      ├─ get_neo4j_schema() → Neo4j MCP returns schema
      ├─ read_neo4j_cypher() → Query DTI limits: 43% for conventional
      ├─ calculate_debt_to_income() → DTI = 28.2%
      ├─ analyze_credit_risk() → Risk = Low
      └─ make_underwriting_decision() → APPROVED with conditions

RESULT:
═══════════════════════════════════════════
UNDERWRITING DECISION: APPROVED
═══════════════════════════════════════════

Application: APP_20251020_012656_MIK
Borrower: Mike Johnson
Loan Amount: $320,000.00

🔐 IDENTITY VERIFICATION: ✅ Verified (confidence: 85%)

KEY FACTORS:
✅ Credit Score: 728 (Good) - Source: Credit MCP
✅ DTI Ratio: 28.2% (Good)
✅ Down Payment: $80,000.00 (20%)

ESTIMATED RATE: 4.5% - 5.0%
CONDITIONS: Verify income stability, standard income documentation
NEXT STEPS: Prepare loan documents and proceed to closing.
```

---

## 🎯 Design Philosophy & Best Practices

### 1. **Zero Hardcoded Business Rules**

**Problem:** Hardcoded rules require code deployment to change.

**Solution:** All business logic in Neo4j.

```python
# ❌ BAD: Hardcoded
def calculate_dti(income, debts):
    dti = debts / income
    if dti < 0.43:  # ← This is hardcoded!
        return "approved"
    return "denied"

# ✅ GOOD: Data-driven
@tool
def calculate_debt_to_income(application_data: dict) -> str:
    """Calculates DTI only (pure math). 
    Agent queries Neo4j for actual limits."""
    dti = (debts / income * 100)  # Just math
    return f"DTI: {dti:.2f}%"
```

### 2. **Prompt Engineering > Code**

**80% of agent behavior is controlled via `prompts.yaml`**

```yaml
# From underwriting_agent/prompts.yaml
system_prompt: |
  ⚠️⚠️⚠️ ABSOLUTE RULE: NEVER OUTPUT TOOL SYNTAX ⚠️⚠️⚠️
  
  FORBIDDEN:
  ❌ read_neo4j_cypher(query="...")
  ❌ [read_neo4j_cypher(query="...")]
  
  CORRECT:
  ✅ Just CALL the tool silently
  ✅ Then report the RESULTS to the user
  
  Identity verification failure = AUTOMATIC DENIAL (no exceptions)
  Always use MCP credit score over self-reported score
```

### 3. **Tool Layering Strategy**

```python
# From underwriting_agent/agent.py
# Tool order matters - LLMs favor earlier tools
tools = (
    shared_application_tools +      # Access stored data first
    neo4j_mcp_tools +                # Business rules second
    core_operational_tools +         # Calculations third
    credit_mcp_tools                 # External services last
)
```

### 4. **Shared Application Data Tools**

**DRY Principle:** All agents access same data via shared tools.

```python
# Shared across all agents
@tool
def get_stored_application_data(application_id: str) -> str:
    """Any agent can retrieve stored application data
    without re-asking the user."""
```

### 5. **Context-Aware Routing**

```python
# Router analyzes conversation history
if previous_agent == "ApplicationAgent" and user_providing_answer:
    route_back_to_application_agent()  # Maintain context
```

---

## 💻 Getting Started

### Prerequisites

- **Python 3.11+** - Check version: `python --version`
- **Neo4j Desktop** - For business rules database
- **Virtual Environment** - For dependency isolation

### Installation

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd mortgage-agents

# 2. Create and activate virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment (optional)
# Edit app/utils/config.yaml to customize:
# - MCP server URLs
# - Neo4j connection details
# - LLM endpoints
```

### Running the System

#### Development Mode (LangGraph Studio)

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Start LangGraph dev server
cd app
langgraph dev
```

The development server will start on `http://localhost:2024` and automatically open LangGraph Studio in your browser.

#### Production Mode (Container)

```bash
# Build container image
./build.sh

# Deploy to OpenShift (requires oc CLI)
cd deploy
./deploy.sh
```

### Configuration

#### MCP Servers

Edit `app/utils/config.yaml`:

```yaml
mcp:
  credit_check:
    url: "https://credit-check-mcp-rh12026.apps.prod.rhoai.rh-aiservices-bu.com/mcp"
    enabled: true
  
  mortgage_rules:
    url: "https://mcp-mortgage-business-rules-route-rh12026.apps.prod.rhoai.rh-aiservices-bu.com/mcp/"
    enabled: true
```

#### Neo4j Connection

```yaml
neo4j:
  uri: "bolt://localhost:7687"
  username: "neo4j"
  password: "your-password"
  database: "mortgage"
```

#### LLM Endpoint

```yaml
llm:
  base_url: "https://lss-lss.apps.prod.rhoai.rh-aiservices-bu.com/v1/openai/v1"
  default_model: "llama-4-scout-17b-16e-w4a16"
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| "Required package 'langgraph-api' is not installed" | Ensure Python 3.11+, activate venv, reinstall: `pip install -r requirements.txt` |
| MCP tools not loading | Check MCP server URLs in config.yaml, verify servers are running |
| Neo4j connection error | Verify Neo4j Desktop is running, check credentials in config.yaml |
| "No module named 'utils'" | Ensure you're in the `app/` directory when running `langgraph dev` |

## 📁 Project Structure

```
mortgage-agents/
├── app/
│   ├── graph.py                      # LangGraph entry point
│   ├── agents/
│   │   ├── mortgage_workflow.py      # Multi-agent router
│   │   ├── application_agent/        # Application intake & URLA
│   │   │   ├── agent.py
│   │   │   ├── prompts.yaml
│   │   │   └── tools/
│   │   ├── document_agent/           # Document processing
│   │   ├── underwriting_agent/       # Underwriting decisions
│   │   ├── mortgage_advisor_agent/   # Loan guidance
│   │   ├── appraisal_agent/          # Property valuation
│   │   └── shared/
│   │       ├── mcp_tools_loader.py   # Credit MCP integration
│   │       ├── neo4j_mcp_loader.py   # Neo4j MCP integration
│   │       └── application_data_tools.py  # Shared data access
│   └── utils/
│       ├── config.yaml               # Configuration
│       ├── database.py               # SQLite operations
│       └── integrations/
│           └── file_uploads.py       # PDF/OCR processing
├── mcp/
│   └── servers/
│       └── credit-check/             # Credit MCP server implementation
├── docs/
│   └── ARCHITECTURE_DIAGRAM.md       # Detailed architecture docs
├── requirements.txt                  # Python dependencies
└── README.md                         # This file
```

---

## 🎯 Quick Demo Examples

### Try These Prompts in LangGraph Studio:

**1. General Inquiry (Routes to Mortgage Advisor)**
```
"I'm a first-time buyer with a 680 credit score and $75,000 income. 
What loan options do I have?"
```

**2. Application Submission (Routes to Application Agent)**
```
"I want to apply for a mortgage. I'm Sarah Johnson, my income is $8,500/month, 
I'm looking at a $450,000 home with 15% down."
```

**3. Document Upload (Routes to Document Agent)**
```
[Upload PDF]
"Hi, I just uploaded my W-2 and pay stubs. Can you process these 
for my mortgage application?"
```

**4. Underwriting Request (Routes to Underwriting Agent)**
```
"Please proceed with underwriting for application APP_20241020_123456. 
The applicant has a 728 credit score, $8,500/month income, and 20% down payment."
```

**5. Multi-Step Workflow**
```
"I need help with my entire mortgage process. I want loan recommendations, 
need to submit my application, and want to understand the underwriting requirements."
```

> 💡 **Tip**: The system automatically routes your request to the appropriate specialist agent based on your intent!

---

## 🔍 Key Capabilities

### ✅ Intelligent Routing
- LLM analyzes user intent
- Routes to specialist agent
- Maintains conversation context
- Handles multi-step workflows

### ✅ Real-time Credit Checks
- Automatic identity verification
- Live credit score retrieval
- Confidence scoring (85-95%)
- Source priority (MCP > self-reported)

### ✅ Data-Driven Decisions
- Zero hardcoded business rules
- Neo4j graph database (1,313+ nodes)
- Dynamic schema discovery
- Real-time rule updates

### ✅ Document Intelligence
- PDF text extraction (PyPDF2)
- OCR for images (pytesseract)
- Multi-document validation
- Cross-document verification

### ✅ Production Features
- Error handling & logging
- Module-level caching
- Graceful degradation
- OpenShift deployment

---

## 📚 Documentation

- **[Architecture Diagram](docs/ARCHITECTURE_DIAGRAM.md)** - Detailed system architecture
- **[MCP Integration](docs/MCP_SERVER_SPEC.md)** - MCP server specifications
- **[Demo Prompts](tests/demo/demo_prompts.md)** - Comprehensive demo scenarios
- **[Input Processing](docs/INPUT_PROCESSING_SPEC.md)** - File processing details

---

## 🤝 Contributing

### Development Workflow

1. Create feature branch
2. Make changes with tests
3. Update prompts.yaml if needed
4. Test with `langgraph dev`
5. Submit pull request

### Adding a New Tool

```python
# In agent/tools/new_tool.py
from langchain_core.tools import tool

@tool
def new_tool(application_data: dict) -> str:
    """Tool description for LLM."""
    # Pure operational logic only
    # NO business rules or thresholds
    return result

# Add to agent/tools/__init__.py
from .new_tool import new_tool

def get_core_tools():
    return [new_tool, ...]
```

### Adding Business Rules

```cypher
// Add to Neo4j via Neo4j MCP or Browser
CREATE (rule:BusinessRule {
  rule_type: 'DTI',
  loan_program: 'conventional',
  max_ratio: 43.0,
  description: 'Maximum DTI for conventional loans'
})
```

---

## 🚀 Deployment

### OpenShift/RHOAI Deployment

```bash
# Build and push container
./build.sh

# Deploy to OpenShift
cd deploy
oc apply -f deployment.yaml
oc apply -f service.yaml
oc apply -f route.yaml
```

### Environment Variables

```bash
# Required
NEO4J_URI=bolt://neo4j:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password

# Optional
MCP_CREDIT_CHECK_URL=https://credit-check-mcp.example.com/mcp
MCP_MORTGAGE_RULES_URL=https://neo4j-mcp.example.com/mcp
LLM_BASE_URL=https://llm-api.example.com/v1
```

---

## 📊 Metrics & Observability

- **LangSmith Integration**: Trace agent execution and tool calls
- **Logging**: Structured logging with agent context
- **Caching**: Module-level MCP tool caching (~500ms improvement)
- **Error Handling**: Graceful degradation when MCP servers unavailable

---

## 📝 License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

---

## 🙏 Acknowledgments

Built with:
- [LangGraph](https://langchain-ai.github.io/langgraph/) - Multi-agent orchestration
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [Neo4j](https://neo4j.com/) - Graph database for business rules
- [LlamaStack](https://github.com/meta-llama/llama-stack) - LLM inference

---

**Version 1.2.0** | Last Updated: October 20, 2025

