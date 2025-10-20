# Mortgage Agents System Architecture

**Version:** v1.2.0  
**Last Updated:** October 20, 2025  
**Based on:** Actual Production Codebase

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              USER / CLIENT INTERFACE                                 │
│                        (LangGraph Studio UI / REST API)                              │
└────────────────────────────────────┬────────────────────────────────────────────────┘
                                     │
                                     │ HTTP/WebSocket
                                     │
┌────────────────────────────────────▼────────────────────────────────────────────────┐
│                          LANGGRAPH DEV SERVER (Port 2024)                            │
│                          app/graph.py → app.create_mortgage_workflow()               │
└────────────────────────────────────┬────────────────────────────────────────────────┘
                                     │
                                     │
┌────────────────────────────────────▼────────────────────────────────────────────────┐
│                         MORTGAGE WORKFLOW (Multi-Agent Router)                       │
│                         app/agents/mortgage_workflow.py                              │
│                                                                                      │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │  ROUTING NODE (LLM-Powered Classification)                                   │  │
│  │  • Analyzes user message using LLM with structured output                    │  │
│  │  • Classifies intent → Routes to specialist agent                            │  │
│  │  • Safety checks: document upload detection, context routing                 │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                      │
│                               Routes to ↓                                            │
│                                                                                      │
│  ┌────────────┬────────────┬────────────┬────────────┬────────────────────────┐    │
│  │ Mortgage   │ Application│ Document   │ Appraisal  │ Underwriting           │    │
│  │ Advisor    │ Agent      │ Agent      │ Agent      │ Agent                  │    │
│  │ Agent      │            │            │            │                        │    │
│  └────────────┴────────────┴────────────┴────────────┴────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────────────────┘
                                     │
                     ┌───────────────┼───────────────┬──────────────────┐
                     │               │               │                  │
                     ▼               ▼               ▼                  ▼
         ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐
         │ LlamaStack   │ │ SQLite DB    │ │ Credit Check │ │ Neo4j MCP        │
         │ LLM Server   │ │ (App Data)   │ │ MCP Server   │ │ Server           │
         │              │ │              │ │              │ │ (Business Rules) │
         └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────┘
```

---

## 🤖 Agent Architecture (Detailed View)

### Agent Structure (All 5 Agents Follow This Pattern)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              SPECIALIZED AGENT                                       │
│                         (e.g., UnderwritingAgent)                                    │
│                                                                                      │
│  ┌────────────────────────────────────────────────────────────────────────────┐    │
│  │  AGENT INITIALIZATION (agent.py)                                           │    │
│  │  • LLM: get_llm() → LlamaStack connection                                  │    │
│  │  • System Prompt: load_agent_prompt() → prompts.yaml                       │    │
│  │  • Tools: Dynamically loaded from 3 sources:                               │    │
│  │    1. Core operational tools (agent-specific)                              │    │
│  │    2. MCP credit tools: get_mcp_credit_tools()                             │    │
│  │    3. MCP Neo4j tools: get_neo4j_mcp_tools()                               │    │
│  │  • Pattern: create_react_agent(llm, tools, prompt)                         │    │
│  └────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                      │
│  ┌────────────────────────────────────────────────────────────────────────────┐    │
│  │  TOOLS AVAILABLE TO AGENT                                                  │    │
│  │                                                                             │    │
│  │  [1] Core Operational Tools (agent/tools/*.py)                             │    │
│  │      • Agent-specific business logic                                       │    │
│  │      • NO hardcoded thresholds or rules                                    │    │
│  │      • Example: analyze_credit_risk, calculate_debt_to_income              │    │
│  │                                                                             │    │
│  │  [2] Shared Application Data Tools (agents/shared/application_data_tools.py)│   │
│  │      • get_stored_application_data(application_id)                         │    │
│  │      • find_application_by_name(applicant_name)                            │    │
│  │      • list_stored_applications(status_filter)                             │    │
│  │                                                                             │    │
│  │  [3] Credit Check MCP Tools (dynamically loaded)                           │    │
│  │      • credit_score(ssn, first_name, last_name, date_of_birth)             │    │
│  │      • verify_identity(ssn, first_name, last_name, date_of_birth)          │    │
│  │      • credit_report(ssn, first_name, last_name, date_of_birth)            │    │
│  │                                                                             │    │
│  │  [4] Neo4j MCP Tools (dynamically loaded)                                  │    │
│  │      • get_neo4j_schema()                                                  │    │
│  │      • read_neo4j_cypher(query)                                            │    │
│  │      • write_neo4j_cypher(query)                                           │    │
│  └────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                      │
│  ┌────────────────────────────────────────────────────────────────────────────┐    │
│  │  AGENT EXECUTION (ReAct Pattern)                                           │    │
│  │  1. Receives user message                                                  │    │
│  │  2. LLM analyzes message + available tools                                 │    │
│  │  3. Selects tool(s) to call based on prompt instructions                   │    │
│  │  4. Executes tool(s) and receives results                                  │    │
│  │  5. Formats results according to output templates in prompts.yaml          │    │
│  │  6. Returns structured response to user                                    │    │
│  └────────────────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Agent Roster & Responsibilities

### 1. **Mortgage Advisor Agent**
```
┌─────────────────────────────────────────────────────────────────┐
│ MORTGAGE ADVISOR AGENT                                          │
│ app/agents/mortgage_advisor_agent/                              │
├─────────────────────────────────────────────────────────────────┤
│ PURPOSE: General Q&A, loan recommendations, guidance            │
│                                                                 │
│ CORE TOOLS (3):                                                 │
│  • explain_loan_programs(loan_type)                            │
│  • recommend_loan_program(application_data)                    │
│  • check_qualification_requirements(loan_program)              │
│                                                                 │
│ MCP TOOLS:                                                      │
│  • Credit Check MCP: credit_score, verify_identity             │
│  • Neo4j MCP: get_neo4j_schema, read_neo4j_cypher              │
│                                                                 │
│ USE CASES:                                                      │
│  ✓ "What loan programs are available?"                         │
│  ✓ "What credit score do I need for FHA?"                      │
│  ✓ "Recommend a loan program for me"                           │
└─────────────────────────────────────────────────────────────────┘
```

### 2. **Application Agent**
```
┌─────────────────────────────────────────────────────────────────┐
│ APPLICATION AGENT                                               │
│ app/agents/application_agent/                                   │
├─────────────────────────────────────────────────────────────────┤
│ PURPOSE: Application intake, URLA generation, status tracking   │
│                                                                 │
│ CORE TOOLS (5):                                                 │
│  • receive_mortgage_application(application_data)              │
│  • generate_urla_1003_form(application_id)                     │
│  • track_application_status(application_id)                    │
│  • check_application_completeness(application_data)            │
│  • perform_initial_qualification(application_data)             │
│                                                                 │
│ MCP TOOLS:                                                      │
│  • Credit Check MCP: credit_score, verify_identity             │
│  • Neo4j MCP: get_neo4j_schema, read_neo4j_cypher              │
│                                                                 │
│ SPECIAL FEATURES:                                               │
│  ✓ Automatic URLA Form 1003 generation after application       │
│  ✓ Real application ID generation (APP_YYYYMMDD_HHMMSS_XXX)    │
│                                                                 │
│ USE CASES:                                                      │
│  ✓ "I want to apply for a mortgage"                            │
│  ✓ "What is the status of my application?"                     │
│  ✓ "Generate URLA form for my application"                     │
└─────────────────────────────────────────────────────────────────┘
```

### 3. **Document Agent**
```
┌─────────────────────────────────────────────────────────────────┐
│ DOCUMENT AGENT                                                  │
│ app/agents/document_agent/                                      │
├─────────────────────────────────────────────────────────────────┤
│ PURPOSE: Document processing, validation, extraction            │
│                                                                 │
│ CORE TOOLS (5):                                                 │
│  • process_uploaded_document(application_data, document_type)  │
│  • extract_document_data(document_content, document_type)      │
│  • verify_document_completeness(application_id)                │
│  • validate_urla_form(urla_data)                               │
│  • get_document_status(application_id)                         │
│                                                                 │
│ MCP TOOLS:                                                      │
│  • Credit Check MCP: credit_score, verify_identity             │
│  • Neo4j MCP: get_neo4j_schema, read_neo4j_cypher              │
│                                                                 │
│ FILE PROCESSING:                                                │
│  ✓ PDF extraction via PyPDF2                                   │
│  ✓ Image OCR via pytesseract                                   │
│  ✓ Multimodal content handling                                 │
│  ✓ File entry cleaning for LLM compatibility                   │
│                                                                 │
│ USE CASES:                                                      │
│  ✓ "Here are my W-2, pay stub, and bank statement"             │
│  ✓ "Process these documents for application APP_12345"         │
│  ✓ "What documents are missing?"                               │
└─────────────────────────────────────────────────────────────────┘
```

### 4. **Appraisal Agent**
```
┌─────────────────────────────────────────────────────────────────┐
│ APPRAISAL AGENT                                                 │
│ app/agents/appraisal_agent/                                     │
├─────────────────────────────────────────────────────────────────┤
│ PURPOSE: Property valuation, market analysis, comparables       │
│                                                                 │
│ CORE TOOLS (5):                                                 │
│  • analyze_property_value(property_data)                       │
│  • find_comparable_sales(property_address, radius)             │
│  • assess_property_condition(property_data)                    │
│  • evaluate_market_conditions(location)                        │
│  • review_appraisal_report(appraisal_data)                     │
│                                                                 │
│ MCP TOOLS:                                                      │
│  • Credit Check MCP: credit_score, verify_identity             │
│  • Neo4j MCP: get_neo4j_schema, read_neo4j_cypher              │
│                                                                 │
│ USE CASES:                                                      │
│  ✓ "What is my property worth?"                                │
│  ✓ "Find comparable sales near me"                             │
│  ✓ "Evaluate market conditions in Austin, TX"                  │
└─────────────────────────────────────────────────────────────────┘
```

### 5. **Underwriting Agent** (Most MCP-Intensive)
```
┌─────────────────────────────────────────────────────────────────┐
│ UNDERWRITING AGENT                                              │
│ app/agents/underwriting_agent/                                  │
├─────────────────────────────────────────────────────────────────┤
│ PURPOSE: Credit risk analysis, underwriting decisions           │
│                                                                 │
│ CORE TOOLS (5):                                                 │
│  • analyze_credit_risk(application_data)                       │
│  • calculate_debt_to_income(application_data)                  │
│  • evaluate_income_sources(application_data)                   │
│  • run_aus_check(application_data)                             │
│  • make_underwriting_decision(application_data)                │
│                                                                 │
│ MCP TOOLS (CRITICAL):                                           │
│  • Credit Check MCP: credit_score, verify_identity, report     │
│  • Neo4j MCP: get_neo4j_schema, read_neo4j_cypher              │
│                                                                 │
│ AUTOMATIC WORKFLOW:                                             │
│  1. Get application data (SSN, name, DOB)                      │
│  2. Call credit_score() + verify_identity()                    │
│  3. Query Neo4j for business rules (DTI limits, credit reqs)   │
│  4. Run operational tools (DTI calc, credit risk analysis)     │
│  5. Make final decision based on rules + data                  │
│                                                                 │
│ KEY POLICIES:                                                   │
│  ✓ AUTOMATIC credit check (no user prompt needed)              │
│  ✓ ABSOLUTE identity verification requirement                  │
│  ✓ PRIORITY: Verified credit score over self-reported          │
│  ✓ DENY if identity verification fails                         │
│                                                                 │
│ USE CASES:                                                      │
│  ✓ "Please proceed with underwriting for APP_12345"            │
│  ✓ "Review my application for approval"                        │
│  ✓ "What is my DTI ratio?"                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔌 External Services & MCP Servers

### Credit Check MCP Server
```
┌─────────────────────────────────────────────────────────────────┐
│ CREDIT CHECK MCP SERVER                                         │
│ Deployment: OpenShift (streamable-http transport)               │
│ URL: https://credit-check-mcp-rh12026.apps.prod.rhoai...        │
├─────────────────────────────────────────────────────────────────┤
│ COMPONENTS:                                                     │
│  • Flask API (port 8081): Mock credit bureau                   │
│  • FastMCP Server (port 8000): MCP protocol handler            │
│                                                                 │
│ TOOLS EXPOSED:                                                  │
│  1. credit_score(ssn, first_name, last_name, date_of_birth)    │
│     → Returns: credit_score, status, bureau                    │
│                                                                 │
│  2. verify_identity(ssn, first_name, last_name, date_of_birth) │
│     → Returns: verified (bool), confidence (%), match_details  │
│                                                                 │
│  3. credit_report(ssn, first_name, last_name, date_of_birth)   │
│     → Returns: full credit report with accounts, inquiries     │
│                                                                 │
│ INTEGRATION:                                                    │
│  • Loaded via: app/agents/shared/mcp_tools_loader.py           │
│  • Transport: streamable_http                                  │
│  • Caching: Module-level cache for performance                 │
│  • Config: app/utils/config.yaml → mcp.credit_check            │
└─────────────────────────────────────────────────────────────────┘
```

### Neo4j MCP Server (Business Rules)
```
┌─────────────────────────────────────────────────────────────────┐
│ NEO4J MCP SERVER                                                │
│ Deployment: OpenShift (streamable-http transport)               │
│ URL: https://mcp-mortgage-business-rules-route-rh12026...       │
├─────────────────────────────────────────────────────────────────┤
│ DATABASE CONTENT:                                               │
│  • 1,313+ nodes with business rules                            │
│  • Node Types:                                                 │
│    - BusinessRule (11): DTI, credit, LTV thresholds            │
│    - CreditScoreRange (10): Score categories & requirements    │
│    - UnderwritingRule (16): Approval criteria                  │
│    - ComplianceRule (14): Regulatory requirements              │
│    - LoanProgram (5): FHA, VA, Conventional, etc.              │
│    - And 20+ more node types...                                │
│                                                                 │
│ TOOLS EXPOSED:                                                  │
│  1. get_neo4j_schema()                                         │
│     → Returns: All nodes, relationships, properties            │
│                                                                 │
│  2. read_neo4j_cypher(query)                                   │
│     → Executes: Read-only Cypher queries                       │
│     → Returns: Query results as JSON                           │
│                                                                 │
│  3. write_neo4j_cypher(query)                                  │
│     → Executes: Write Cypher queries                           │
│     → Returns: Write confirmation                              │
│                                                                 │
│ INTEGRATION:                                                    │
│  • Loaded via: app/agents/shared/neo4j_mcp_loader.py           │
│  • Transport: streamable_http                                  │
│  • Caching: Module-level cache for performance                 │
│  • Config: app/utils/config.yaml → mcp.mortgage_rules          │
│                                                                 │
│ EXAMPLE QUERIES:                                                │
│  • "What credit score is required for FHA?"                    │
│    → MATCH (n:BusinessRule) WHERE n.category = 'credit' ...    │
│                                                                 │
│  • "What is the maximum DTI for conventional loans?"           │
│    → MATCH (n:BusinessRule {rule_type: 'DTI'}) ...             │
└─────────────────────────────────────────────────────────────────┘
```

### LlamaStack LLM Server
```
┌─────────────────────────────────────────────────────────────────┐
│ LLAMASTACK LLM SERVER                                           │
│ Deployment: OpenShift (OpenAI-compatible API)                   │
│ URL: https://lss-lss.apps.prod.rhoai.rh-aiservices-bu.com/v1   │
├─────────────────────────────────────────────────────────────────┤
│ MODEL: llama-4-scout-17b-16e-w4a16                              │
│  • Parameters: 17B                                              │
│  • Quantization: W4A16 (4-bit weights, 16-bit activations)     │
│  • Context Window: Extended                                     │
│  • Temperature: 0.7 (balanced creativity)                       │
│  • Max Tokens: 2000 per response                                │
│                                                                 │
│ INTEGRATION:                                                    │
│  • Loaded via: app/utils/llm_factory.py → get_llm()            │
│  • Protocol: OpenAI-compatible REST API                         │
│  • Config: app/utils/config.yaml → llm                          │
│  • No API key required                                          │
│                                                                 │
│ USAGE:                                                          │
│  • All agent LLM calls                                          │
│  • Router classification                                        │
│  • Tool selection (ReAct pattern)                               │
│  • Structured output generation                                 │
└─────────────────────────────────────────────────────────────────┘
```

### SQLite Database
```
┌─────────────────────────────────────────────────────────────────┐
│ SQLITE DATABASE (Application Data Store)                        │
│ Path: data/chat_sessions.db                                     │
├─────────────────────────────────────────────────────────────────┤
│ TABLES:                                                         │
│  • mortgage_applications: Core application data                │
│  • urla_forms: Generated URLA 1003 forms                       │
│  • documents: Document metadata & status                        │
│  • chat_sessions: Conversation history                          │
│                                                                 │
│ ACCESS PATTERN:                                                 │
│  • Direct access via app/utils/database.py                     │
│  • Exposed to agents via shared tools:                         │
│    - get_stored_application_data(application_id)               │
│    - find_application_by_name(applicant_name)                  │
│    - list_stored_applications(status_filter)                   │
│                                                                 │
│ DATA FLOW:                                                      │
│  1. Application Agent: Writes new applications                 │
│  2. Document Agent: Updates document status                    │
│  3. Underwriting Agent: Reads application data                 │
│  4. All Agents: Query via shared tools                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 End-to-End Flow: Application to Approval

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         COMPLETE E2E MORTGAGE FLOW                                   │
└─────────────────────────────────────────────────────────────────────────────────────┘

USER: "I want to apply for a mortgage..."
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: ROUTING                                                 │
│ Router analyzes message → Routes to APPLICATION AGENT           │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: APPLICATION INTAKE                                      │
│ APPLICATION AGENT executes:                                     │
│  1. receive_mortgage_application(application_data)              │
│     → Stores in SQLite                                          │
│     → Returns: APP_20251020_012656_MIK                          │
│                                                                 │
│  2. generate_urla_1003_form(application_id)                     │
│     → Generates URLA Form 1003                                  │
│     → Stores in SQLite                                          │
│     → Returns: URLA_20251020_012656_414B                        │
│                                                                 │
│ STATUS: SUBMITTED → Ready for document collection               │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
USER: "Here are my W-2, pay stub, and bank statement" [uploads PDFs]
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: ROUTING (Document Detection)                            │
│ Router detects "UPLOADED DOCUMENTS" → Routes to DOCUMENT AGENT  │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: DOCUMENT PROCESSING                                     │
│ DOCUMENT AGENT executes:                                        │
│  For each document:                                             │
│    1. extract_document_data(document_content, document_type)    │
│       → PDF extraction via PyPDF2                               │
│       → Income: $102,000, Balance: $74,755.48                   │
│                                                                 │
│    2. process_uploaded_document(application_data, doc_type)     │
│       → Validates document                                      │
│       → Updates application status                              │
│                                                                 │
│ STATUS: DOCUMENT_COLLECTION → CREDIT_REVIEW                     │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
USER: "Please proceed with underwriting for APP_20251020_012656_MIK"
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: ROUTING                                                 │
│ Router analyzes "underwriting" → Routes to UNDERWRITING AGENT   │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: UNDERWRITING ANALYSIS (AUTOMATIC)                       │
│ UNDERWRITING AGENT executes:                                    │
│                                                                 │
│  1. get_stored_application_data(application_id)                 │
│     → Retrieves: SSN=987-65-1321, Name=Mike Johnson, DOB=...   │
│                                                                 │
│  2. credit_score(ssn, first_name, last_name, dob)               │
│     ↓ Credit Check MCP (OpenShift)                              │
│     → Returns: Credit Score = 728                               │
│                                                                 │
│  3. verify_identity(ssn, first_name, last_name, dob)            │
│     ↓ Credit Check MCP (OpenShift)                              │
│     → Returns: Verified = True, Confidence = 85%                │
│                                                                 │
│  4. get_neo4j_schema()                                          │
│     ↓ Neo4j MCP (OpenShift)                                     │
│     → Returns: Schema with BusinessRule nodes                   │
│                                                                 │
│  5. read_neo4j_cypher("MATCH (n:BusinessRule) RETURN n")        │
│     ↓ Neo4j MCP (OpenShift)                                     │
│     → Returns: Credit score 680-739 = "Good"                    │
│                Down payment 20%+ = "Excellent"                  │
│                DTI thresholds, approval criteria                │
│                                                                 │
│  6. calculate_debt_to_income(application_data)                  │
│     → Calculates: DTI = 28.2% (Good)                            │
│                                                                 │
│  7. analyze_credit_risk(application_data)                       │
│     → Analyzes: Risk level = Low                                │
│                                                                 │
│  8. make_underwriting_decision(application_data)                │
│     → Decision: APPROVED                                        │
│     → Conditions: Verify income stability, review credit report │
│                                                                 │
│ OUTPUT (Formatted):                                             │
│ ══════════════════════════════════════════════                  │
│ UNDERWRITING DECISION: APPROVED                                 │
│ ══════════════════════════════════════════════                  │
│                                                                 │
│ Application: APP_20251020_012656_MIK                            │
│ Borrower: Mike Johnson                                          │
│ Loan Amount: $320,000.00                                        │
│                                                                 │
│ 🔐 IDENTITY VERIFICATION: ✅ Verified (confidence: 85%)          │
│                                                                 │
│ KEY FACTORS:                                                    │
│ ✅ Credit Score: 728 (Good) - Source: Credit MCP                │
│ ✅ DTI Ratio: 28.2% (Good)                                      │
│ ✅ Down Payment: $80,000.00 (20%)                               │
│                                                                 │
│ 🚨 NO DISCREPANCY: No issues found.                             │
│                                                                 │
│ ESTIMATED RATE: 4.5% - 5.0%                                     │
│ CONDITIONS:                                                     │
│ • Verify income and employment stability                        │
│ • Review credit report for any issues                           │
│                                                                 │
│ NEXT STEPS: Prepare loan documents and proceed to closing.     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Technology Stack

### Core Framework
```
LangGraph v0.2+
├── Agent Pattern: create_react_agent (ReAct: Reasoning + Acting)
├── State Management: Built-in state graph with checkpointing
├── Routing: LLM-powered structured output classification
└── Tools: Dynamic loading from multiple sources

LangChain Core
├── LLM Integration: OpenAI-compatible interface
├── Tool Abstraction: BaseTool for uniform tool interface
└── Message Types: HumanMessage, AIMessage, SystemMessage
```

### MCP Integration
```
LangChain MCP Adapters
├── MultiServerMCPClient: Connects to multiple MCP servers
├── Transport: streamable_http (HTTP-based)
├── Tool Discovery: Automatic tool loading from MCP servers
└── Caching: Module-level caching for performance

FastMCP (MCP Server Implementation)
├── Server Framework: FastMCP for Python MCP servers
├── Transport: streamable_http via Uvicorn
├── Tools: Decorator-based tool definition (@mcp.tool)
└── Deployment: OpenShift with Route exposure
```

### LLM & AI
```
LlamaStack (Llama 4 Scout 17B)
├── Model: llama-4-scout-17b-16e-w4a16
├── API: OpenAI-compatible REST API
├── Deployment: OpenShift RHOAI
└── Features: Extended context, structured output

Prompt Engineering
├── YAML-based prompts (prompts.yaml)
├── Anti-describing instructions (prevent tool syntax leak)
├── Output format templates (consistent formatting)
└── Policy enforcement (identity verification, credit checks)
```

### Data & Storage
```
SQLite
├── Purpose: Application data, URLA forms, documents
├── Schema: 4+ tables with relationships
├── Access: Direct via app/utils/database.py
└── Tools: Exposed via shared application data tools

Neo4j
├── Purpose: Business rules, loan programs, compliance
├── Deployment: Local (bolt://localhost:7687)
├── MCP Exposure: Via Neo4j MCP Server on OpenShift
├── Schema: 1,313+ nodes, 30+ node types
└── Access: Via Neo4j MCP tools (read_neo4j_cypher, etc.)
```

### File Processing
```
Document Handling
├── PDF: PyPDF2 for text extraction
├── Images: pytesseract for OCR
├── Multimodal: LangGraph Studio file upload support
└── Cleaning: clean_file_entries_from_messages() for LLM compat
```

### Deployment
```
OpenShift (RHOAI)
├── Main App: mortgage-agents (Port 2024)
├── LLM Server: LlamaStack (lss-lss)
├── Credit Check MCP: credit-check-mcp-rh12026
├── Neo4j MCP: mcp-mortgage-business-rules-route-rh12026
└── Routing: OpenShift Routes for external HTTPS access

Container Registry
├── Registry: quay.io/rbrhssa
├── Images:
│   ├── mortgage-agents:v1.2.0 (main app)
│   └── mcp-credit:v3.13-mcp-server-v4 (credit check)
└── Build Tool: Podman (build.sh script)
```

---

## 📁 Project Structure

```
mortgage-agents/
│
├── app/
│   ├── graph.py                          # LangGraph entry point
│   │
│   ├── agents/
│   │   ├── mortgage_workflow.py          # Multi-agent router
│   │   │
│   │   ├── application_agent/
│   │   │   ├── agent.py                  # Agent initialization
│   │   │   ├── prompts.yaml              # System prompt + templates
│   │   │   └── tools/                    # Core operational tools
│   │   │       ├── receive_mortgage_application.py
│   │   │       ├── generate_urla_1003_form.py
│   │   │       ├── track_application_status.py
│   │   │       ├── check_application_completeness.py
│   │   │       └── perform_initial_qualification.py
│   │   │
│   │   ├── document_agent/
│   │   │   ├── agent.py
│   │   │   ├── prompts.yaml
│   │   │   └── tools/
│   │   │       ├── process_uploaded_document.py
│   │   │       ├── extract_document_data.py
│   │   │       ├── verify_document_completeness.py
│   │   │       ├── validate_urla_form.py
│   │   │       └── get_document_status.py
│   │   │
│   │   ├── underwriting_agent/
│   │   │   ├── agent.py
│   │   │   ├── prompts.yaml
│   │   │   └── tools/
│   │   │       ├── analyze_credit_risk.py
│   │   │       ├── calculate_debt_to_income.py
│   │   │       ├── evaluate_income_sources.py
│   │   │       ├── run_aus_check.py
│   │   │       └── make_underwriting_decision.py
│   │   │
│   │   ├── mortgage_advisor_agent/
│   │   │   ├── agent.py
│   │   │   ├── prompts.yaml
│   │   │   └── tools/
│   │   │       ├── explain_loan_programs.py
│   │   │       ├── recommend_loan_program.py
│   │   │       └── check_qualification_requirements.py
│   │   │
│   │   ├── appraisal_agent/
│   │   │   ├── agent.py
│   │   │   ├── prompts.yaml
│   │   │   └── tools/
│   │   │       ├── analyze_property_value.py
│   │   │       ├── find_comparable_sales.py
│   │   │       ├── assess_property_condition.py
│   │   │       ├── evaluate_market_conditions.py
│   │   │       └── review_appraisal_report.py
│   │   │
│   │   └── shared/
│   │       ├── mcp_tools_loader.py       # Credit Check MCP loader
│   │       ├── neo4j_mcp_loader.py       # Neo4j MCP loader
│   │       ├── application_data_tools.py # Shared SQLite tools
│   │       └── prompt_loader.py          # YAML prompt loader
│   │
│   └── utils/
│       ├── config.yaml                   # Centralized configuration
│       ├── config.py                     # Config loader
│       ├── llm_factory.py                # get_llm() factory
│       ├── database.py                   # SQLite operations
│       └── integrations/
│           └── file_uploads.py           # PDF/image processing
│
├── mcp/
│   └── servers/
│       └── credit-check/
│           ├── mcp_server.py             # FastMCP server
│           ├── mock_credit_api.py        # Flask mock credit bureau
│           └── start-mcp-server.sh       # Container startup script
│
├── mcp/deployment/
│   ├── kubernetes/
│   │   └── Containerfile.credit-api      # Credit MCP Dockerfile
│   └── openshift/
│       └── credit-check-deployment.yaml  # K8s Deployment + Service + Route
│
├── data/
│   └── chat_sessions.db                  # SQLite database
│
├── docs/
│   └── ARCHITECTURE_DIAGRAM.md           # This file!
│
├── Containerfile                          # Main app Dockerfile
├── build.sh                               # Podman build/push script
├── requirements.txt                       # Python dependencies
└── README.md                              # Project documentation
```

---

## 🔐 Security & Best Practices

### Identity Verification
```
ABSOLUTE REQUIREMENT (Underwriting Agent):
- verify_identity() MUST be called before approval
- If identity verification fails → AUTOMATIC DENIAL
- No exceptions, no conditional approvals
- Confidence threshold: Configurable (default: 60%)
- Policy enforced via prompt engineering
```

### Data Source Priority
```
CREDIT SCORE PRIORITY:
1. Credit MCP (credit_score tool)     ← HIGHEST PRIORITY
2. Self-reported (from application)    ← BACKUP ONLY

POLICY:
- Always call credit_score() first
- If discrepancy > 10 points → FLAG for review
- Report both scores in decision
- Never rely solely on self-reported scores
```

### Prompt Engineering (Anti-Describing)
```
PROBLEM: LLM outputs tool syntax instead of executing
BAD OUTPUT: "[read_neo4j_cypher(query='...')]"
CORRECT: Tool executes silently, results reported

SOLUTION:
- Strong anti-describing instructions in prompts.yaml
- Examples of forbidden vs. correct outputs
- "NEVER OUTPUT TOOL SYNTAX" in bold/emoji
- Multiple enforcement layers across all agents
```

### MCP Caching
```
PERFORMANCE OPTIMIZATION:
- Module-level caching of MCP tools
- Avoids re-initialization on every agent call
- Reduces latency by ~500ms per request
- Cache cleared on module reload

IMPLEMENTATION:
# app/agents/shared/mcp_tools_loader.py
_mcp_client: Optional[MultiServerMCPClient] = None
_mcp_tools_cache: Optional[List[BaseTool]] = None
```

---

## 🚀 Deployment Architecture

### Development Environment
```
Local Machine
├── LangGraph Dev Server: localhost:2024 (main app)
├── Neo4j Desktop: localhost:7687 (business rules)
├── Credit MCP (optional): localhost:8000
└── LlamaStack: Remote (OpenShift)
```

### Production Environment (OpenShift)
```
OpenShift Cluster (apps.prod.rhoai.rh-aiservices-bu.com)
│
├── Namespace: rh12026
│
├── Main Application
│   ├── Deployment: mortgage-agents
│   ├── Image: quay.io/rbrhssa/mortgage-agents:v1.2.0
│   ├── Port: 2024
│   ├── Route: mortgage-agents-rh12026.apps.prod...
│   └── Resources:
│       ├── CPU: 1-2 cores
│       ├── Memory: 2-4 GB
│       └── Storage: PVC for SQLite database
│
├── Credit Check MCP
│   ├── Deployment: credit-check-mcp
│   ├── Image: quay.io/rbrhssa/mcp-credit:v3.13-mcp-server-v4
│   ├── Port: 8000 (MCP), 8081 (Flask API)
│   ├── Route: credit-check-mcp-rh12026.apps.prod...
│   └── Resources:
│       ├── CPU: 500m-1 core
│       └── Memory: 512MB-1GB
│
├── Neo4j MCP
│   ├── Deployment: mcp-mortgage-business-rules
│   ├── Route: mcp-mortgage-business-rules-route-rh12026...
│   └── Backend: Neo4j Desktop (external)
│
└── LlamaStack LLM
    ├── Service: lss-lss
    ├── Route: lss-lss.apps.prod...
    └── Model: llama-4-scout-17b-16e-w4a16
```

---

## 📊 Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                              DATA SOURCES & FLOW                                  │
└──────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│  USER INPUT     │
│  (LangGraph UI) │
└────────┬────────┘
         │
         │ 1. User message + files
         ▼
┌──────────────────────────────────────────┐
│  LANGGRAPH WORKFLOW                      │
│  (Routing + Agent Execution)             │
└─┬──────────────────────────────────────┬─┘
  │                                      │
  │ 2a. Router classifies                │ 2b. Agent executes tools
  │     → Selects agent                  │     → Calls external services
  ▼                                      ▼
┌─────────────────┐          ┌────────────────────────────────┐
│ SPECIALIZED     │          │ EXTERNAL SERVICES              │
│ AGENT           │          │                                │
│ (with tools)    │          │ ┌──────────────────────────┐   │
└─────────────────┘          │ │ Credit Check MCP         │   │
                             │ │ • credit_score()         │   │
                             │ │ • verify_identity()      │   │
                             │ │ • credit_report()        │   │
                             │ └──────────────────────────┘   │
                             │                                │
                             │ ┌──────────────────────────┐   │
                             │ │ Neo4j MCP                │   │
                             │ │ • get_neo4j_schema()     │   │
                             │ │ • read_neo4j_cypher()    │   │
                             │ │ • write_neo4j_cypher()   │   │
                             │ └──────────────────────────┘   │
                             │                                │
                             │ ┌──────────────────────────┐   │
                             │ │ SQLite Database          │   │
                             │ │ • Applications           │   │
                             │ │ • URLA Forms             │   │
                             │ │ • Documents              │   │
                             │ └──────────────────────────┘   │
                             └────────────────────────────────┘
         │
         │ 3. Tool results returned to agent
         ▼
┌──────────────────────────────────────────┐
│  AGENT RESPONSE FORMATTING               │
│  (Based on prompts.yaml templates)       │
└─────────────────┬────────────────────────┘
                  │
                  │ 4. Formatted response
                  ▼
         ┌─────────────────┐
         │  USER OUTPUT    │
         │  (LangGraph UI) │
         └─────────────────┘
```

---

## 🎯 Key Design Decisions

### 1. **MCP Pattern Over Hardcoded Integrations**
- **Why:** Flexibility, maintainability, standard protocol
- **How:** LangChain MCP Adapters with MultiServerMCPClient
- **Benefit:** Add new services without code changes

### 2. **ReAct Agent Pattern**
- **Why:** LLM decides when/how to use tools dynamically
- **How:** LangGraph's create_react_agent with tool lists
- **Benefit:** Adaptive behavior, no hardcoded workflows

### 3. **YAML-Based Prompts**
- **Why:** Easier to iterate, version control, non-technical editing
- **How:** prompts.yaml loaded at agent initialization
- **Benefit:** Prompt engineering without code deployment

### 4. **Shared Application Data Tools**
- **Why:** DRY principle, consistent data access
- **How:** app/agents/shared/application_data_tools.py
- **Benefit:** Single source of truth for SQLite operations

### 5. **Automatic URLA Generation**
- **Why:** Reduce manual work, ensure compliance
- **How:** Prompt instructs agent to call generate_urla_1003_form after receive_mortgage_application
- **Benefit:** Consistent workflow, no user action needed

### 6. **Identity Verification as Absolute Requirement**
- **Why:** Fraud prevention, regulatory compliance
- **How:** Prompt policy + DENY if verification fails
- **Benefit:** Automated compliance enforcement

### 7. **Module-Level MCP Caching**
- **Why:** Performance optimization (avoid re-initialization)
- **How:** Global variables for client + tools cache
- **Benefit:** ~500ms latency reduction per request

### 8. **Streamable-HTTP MCP Transport**
- **Why:** Simplicity, standard HTTP (vs. SSE complexity)
- **How:** FastMCP with Uvicorn, exposed via OpenShift Route
- **Benefit:** Easy deployment, debugging, monitoring

---

## 🔍 Debugging & Monitoring

### Logging
```python
# All agents log tool loading:
logger.info(f"✓ Loaded {len(credit_mcp_tools)} credit MCP tools: {[t.name for t in credit_mcp_tools]}")
logger.info(f"✓ Loaded {len(neo4j_mcp_tools)} Neo4j MCP tools: {[t.name for t in neo4j_mcp_tools]}")

# MCP loaders log connection status:
logger.info("Returning {len(tools)} cached MCP tools")
logger.warning("⚠️  No credit MCP tools loaded - MCP server may be unavailable")
```

### Health Checks
```
Credit Check MCP:
GET /health → Flask API health

Neo4j MCP:
GET /mcp → MCP server health

Main App:
GET / → LangGraph health
```

### Common Issues
```
ISSUE: MCP tools not loading
CHECK:
  1. MCP server URL in config.yaml
  2. MCP server deployment status (oc get pods)
  3. MCP server logs (oc logs <pod-name>)
  4. Network connectivity (can agents reach MCP URL?)

ISSUE: Agent outputs tool syntax instead of executing
CHECK:
  1. Prompts.yaml has anti-describing instructions
  2. Agent initialization includes tools
  3. LLM is receiving tools correctly

ISSUE: Identity verification failing
CHECK:
  1. Mock data in mock_credit_api.py matches test SSN/DOB
  2. Date format: Both YYYY-MM-DD and MM/DD/YYYY supported
  3. Credit Check MCP is running and accessible
```

---

## 📈 Version History

### v1.2.0 (Current - October 20, 2025)
- ✅ Fixed ApplicationAgent fake `APP_1234` issue
- ✅ Automatic URLA Form 1003 generation
- ✅ Identity verification displayed prominently with confidence %
- ✅ Credit Check MCP deployed as streamable-http (removed ToolHive)
- ✅ Neo4j MCP business rules integration confirmed working
- ✅ Cleaned all "ToolHive" references from codebase
- ✅ Module-level MCP caching for performance
- ✅ Fixed `get_stored_application_data` tool schema validation

### v1.1.0 (October 19, 2025)
- Credit Check MCP deployed on OpenShift
- Neo4j MCP integration for business rules
- Prompt engineering improvements (anti-describing)
- Multimodal file upload support

### v1.0.0 (October 2025)
- Initial multi-agent mortgage system
- 5 specialized agents (Advisor, Application, Document, Appraisal, Underwriting)
- LangGraph routing workflow
- SQLite persistence

---

## 🎓 Learning Resources

### LangGraph
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [ReAct Agent Pattern](https://langchain-ai.github.io/langgraph/tutorials/introduction/#routing)
- [Multi-Agent Systems](https://langchain-ai.github.io/langgraph/tutorials/multi-agent/)

### Model Context Protocol (MCP)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)
- [LangChain MCP Adapters](https://github.com/langchain-ai/langchain-mcp)

### Neo4j
- [Neo4j Cypher Query Language](https://neo4j.com/docs/cypher-manual/current/)
- [Neo4j MCP Server](https://github.com/neo4j/neo4j-mcp)

---

## 📝 Notes

1. **No Hardcoded Business Rules:** All thresholds, limits, and approval criteria are stored in Neo4j and queried at runtime via Neo4j MCP.

2. **MCP as Plugin Architecture:** New services (e.g., appraisal API, title search) can be added as MCP servers without modifying agent code.

3. **Prompt Engineering is Critical:** 80% of agent behavior is controlled by prompts.yaml. Test prompt changes thoroughly.

4. **Caching Improves Performance:** MCP tool caching reduces latency. Consider Redis for distributed caching in production.

5. **Identity Verification is Non-Negotiable:** The system enforces identity verification at the prompt level. This is a deliberate design choice for fraud prevention.

6. **Streamable-HTTP is Preferred:** Simpler than SSE, easier to debug, standard HTTP tooling works.

---

**END OF ARCHITECTURE DIAGRAM**

*This document is auto-generated from the production codebase and reflects the actual implementation as of v1.2.0.*

