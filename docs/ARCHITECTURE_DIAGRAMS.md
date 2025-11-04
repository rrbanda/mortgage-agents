# Mortgage Agent System - Architecture Diagrams

## 🏗️ Overview

This document contains visual diagrams explaining the refactored mortgage agent system architecture, focusing on the separation of operational tools and business rules.

---

## 1️⃣ System Architecture Overview

```mermaid
graph TB
    subgraph "User Layer"
        User[👤 User/Customer]
    end
    
    subgraph "Routing Layer"
        Router[🎯 Intelligent Router<br/>LLM-Powered Classification]
    end
    
    subgraph "Agent Layer - 5 Specialized Agents"
        AA[📝 ApplicationAgent<br/>5 operational + 2 business rules]
        MA[💼 MortgageAdvisorAgent<br/>3 operational + 3 business rules]
        DA[📄 DocumentAgent<br/>5 operational + 1 business rules]
        AP[🏠 AppraisalAgent<br/>6 operational + 1 business rules]
        UA[🔍 UnderwritingAgent<br/>8 operational + 3 business rules]
    end
    
    subgraph "External Services"
        SMTP[📧 SMTP Email Service<br/>Gmail for Notifications]
    end
    
    subgraph "Business Rules Layer"
        BR[📚 Shared Business Rules<br/>app/agents/shared/rules/]
        BR1[get_application_intake_rules]
        BR2[get_loan_program_requirements]
        BR3[get_document_requirements]
        BR4[get_qualification_criteria]
        BR5[get_underwriting_rules]
        BR6[get_aus_rules]
        BR7[get_income_calculation_rules]
        BR8[get_property_appraisal_rules]
        
        BR --> BR1
        BR --> BR2
        BR --> BR3
        BR --> BR4
        BR --> BR5
        BR --> BR6
        BR --> BR7
        BR --> BR8
    end
    
    subgraph "Data Layer"
        Neo4j[(🗄️ Neo4j<br/>Graph Database)]
        MCP[🔌 MCP Server<br/>Model Context Protocol]
    end
    
    User -->|Request| Router
    Router -->|Route| AA
    Router -->|Route| MA
    Router -->|Route| DA
    Router -->|Route| AP
    Router -->|Route| UA
    
    AA -.->|Operational<br/>Direct Cypher| Neo4j
    MA -.->|Operational<br/>Direct Cypher| Neo4j
    DA -.->|Operational<br/>Direct Cypher| Neo4j
    AP -.->|Operational<br/>Direct Cypher| Neo4j
    UA -.->|Operational<br/>Direct Cypher| Neo4j
    
    AA -->|Business Rules<br/>Via MCP| BR
    MA -->|Business Rules<br/>Via MCP| BR
    DA -->|Business Rules<br/>Via MCP| BR
    AP -->|Business Rules<br/>Via MCP| BR
    UA -->|Business Rules<br/>Via MCP| BR
    
    BR -->|Query Rules<br/>Via MCP| MCP
    MCP -->|Cypher Queries| Neo4j
    
    style Router fill:#4A90E2,stroke:#2E5C8A,stroke-width:2px,color:#fff
    style AA fill:#50C878,stroke:#2E7D4E,stroke-width:2px,color:#fff
    style MA fill:#50C878,stroke:#2E7D4E,stroke-width:2px,color:#fff
    style DA fill:#50C878,stroke:#2E7D4E,stroke-width:2px,color:#fff
    style AP fill:#50C878,stroke:#2E7D4E,stroke-width:2px,color:#fff
    style UA fill:#50C878,stroke:#2E7D4E,stroke-width:2px,color:#fff
    style BR fill:#FF6B6B,stroke:#C93838,stroke-width:2px,color:#fff
    style Neo4j fill:#9B59B6,stroke:#6C3483,stroke-width:2px,color:#fff
    style MCP fill:#F39C12,stroke:#B8770A,stroke-width:2px,color:#fff
```

**Key Principles:**
-  Each agent has operational tools (direct Neo4j access)
-  Each agent has scoped business rules tools (via MCP)
-  Business rules are centralized in `shared/rules/`
-  Clean separation of concerns

---

## 2️⃣ External Services Integration

```mermaid
graph TB
    subgraph "Mortgage Agent System"
        Agents[5 Specialized Agents]
    end
    
    subgraph "External Services"
        Email[📧 SMTP Email<br/>Gmail Notifications]
        CreditMCP[🔌 Credit Check MCP<br/>Identity & Scores]
        Neo4jMCP[🔌 Neo4j MCP<br/>Business Rules]
        LLM[🤖 LlamaStack LLM<br/>Llama 4 Scout 17B]
    end
    
    Agents -->|Appraisal notifications| Email
    Agents -->|Credit verification| CreditMCP
    Agents -->|Business rules| Neo4jMCP
    Agents -->|Reasoning & tool selection| LLM
    
    style Email fill:#FF6B6B,stroke:#C93838,stroke-width:2px,color:#fff
    style CreditMCP fill:#50C878,stroke:#2E7D4E,stroke-width:2px,color:#fff
    style Neo4jMCP fill:#9B59B6,stroke:#6C3483,stroke-width:2px,color:#fff
    style LLM fill:#F39C12,stroke:#B8770A,stroke-width:2px,color:#fff
```

**Integrated Services:**
- 📧 **SMTP Email:** Gmail-based notifications for appraisal scheduling
- 🔌 **Credit Check MCP:** Real-time credit scores and identity verification
- 🔌 **Neo4j MCP:** Dynamic business rules without hardcoding
- 🤖 **LlamaStack LLM:** Agent reasoning and decision making

---

## 3️⃣ Tool Architecture - Operational vs Business Rules

```mermaid
graph TB
    subgraph "ApplicationAgent - 7 Total Tools"
        direction TB
        subgraph "Operational Tools (5)"
            AA1[receive_mortgage_application]
            AA2[retrieve_stored_application]
            AA3[check_application_completeness]
            AA4[perform_initial_qualification]
            AA5[generate_urla_form]
        end
        subgraph "Business Rules (2 - Scoped)"
            AAR1[get_application_intake_rules]
            AAR2[get_loan_program_requirements]
        end
    end
    
    subgraph "MortgageAdvisorAgent - 6 Total Tools"
        direction TB
        subgraph "Operational Tools (3)"
            MA1[explain_loan_programs]
            MA2[recommend_loan_program]
            MA3[check_qualification_requirements]
        end
        subgraph "Business Rules (3 - Scoped)"
            MAR1[get_loan_program_requirements]
            MAR2[get_qualification_criteria]
            MAR3[get_underwriting_rules]
        end
    end
    
    subgraph "DocumentAgent - 6 Total Tools"
        direction TB
        subgraph "Operational Tools (5)"
            DA1[process_uploaded_document]
            DA2[extract_document_data]
            DA3[get_document_status]
            DA4[verify_document_completeness]
            DA5[validate_urla_form]
        end
        subgraph "Business Rules (1 - Scoped)"
            DAR1[get_document_requirements]
        end
    end
    
    subgraph "AppraisalAgent - 7 Total Tools"
        direction TB
        subgraph "Operational Tools (6)"
            AP1[schedule_appraisal]
            AP2[analyze_property_value]
            AP3[find_comparable_sales]
            AP4[assess_property_condition]
            AP5[review_appraisal_report]
            AP6[evaluate_market_conditions]
        end
        subgraph "Business Rules (1 - Scoped)"
            APR1[get_property_appraisal_rules]
        end
    end
    
    subgraph "UnderwritingAgent - 11 Total Tools"
        direction TB
        subgraph "Operational Tools (8)"
            UA1[analyze_credit_risk]
            UA2[calculate_debt_to_income]
            UA3[evaluate_income_sources]
            UA4[run_aus_check]
            UA5[make_underwriting_decision]
            UA6[get_credit_score - MCP]
            UA7[verify_identity - MCP]
            UA8[get_credit_report - MCP]
        end
        subgraph "Business Rules (3 - Scoped)"
            UAR1[get_underwriting_rules]
            UAR2[get_aus_rules]
            UAR3[get_income_calculation_rules]
        end
    end
    
    style AA1 fill:#E8F5E9,stroke:#4CAF50,stroke-width:2px
    style AA2 fill:#E8F5E9,stroke:#4CAF50,stroke-width:2px
    style AA3 fill:#E8F5E9,stroke:#4CAF50,stroke-width:2px
    style AA4 fill:#E8F5E9,stroke:#4CAF50,stroke-width:2px
    style AA5 fill:#E8F5E9,stroke:#4CAF50,stroke-width:2px
    style AAR1 fill:#FFEBEE,stroke:#F44336,stroke-width:2px
    style AAR2 fill:#FFEBEE,stroke:#F44336,stroke-width:2px
```

**Color Legend:**
- 🟢 **Green:** Operational Tools (NO hardcoded business rules)
- 🔴 **Red:** Business Rules Tools (from shared/rules/, via MCP)

---

## 4️⃣ Tool Statistics Summary

```mermaid
pie title Agent Tool Distribution (37 Total Tools)
    "ApplicationAgent : 7" : 7
    "MortgageAdvisorAgent : 6" : 6
    "DocumentAgent : 6" : 6
    "AppraisalAgent : 7" : 7
    "UnderwritingAgent : 11" : 11
```

```mermaid
pie title Tool Type Distribution
    "Operational Tools : 27" : 27
    "Business Rules Tools : 10" : 10
```

**Statistics:**
- **5 Agents** (all production-ready)
- **37 Total Tools** across all agents
- **27 Operational Tools** (NO hardcoded business rules)
- **10 Business Rules Tools** (scoped to agent needs)
- **NEW:** Email notification service integrated

---

## 5️⃣ Business Rules Access Pattern

```mermaid
sequenceDiagram
    participant User
    participant Agent as MortgageAdvisorAgent
    participant OpTool as Operational Tool<br/>explain_loan_programs
    participant BRTool as Business Rules Tool<br/>get_loan_program_requirements
    participant MCP as MCP Server
    participant Neo4j as Neo4j Database
    
    User->>Agent: "What are FHA loan requirements?"
    
    Note over Agent: Agent decides which tools to use
    
    Agent->>OpTool: Call operational tool<br/>(provides general info)
    OpTool-->>Agent: "FHA is a government-backed loan...<br/>(NO specific requirements)"
    
    Agent->>BRTool: Call business rules tool<br/>(get actual requirements)
    BRTool->>MCP: Query requirements via MCP
    MCP->>Neo4j: Cypher: MATCH (rule:LoanProgramRequirement)<br/>WHERE rule.program = 'FHA'
    Neo4j-->>MCP: Return: credit_score_min=580,<br/>down_payment=3.5%, DTI_max=43%
    MCP-->>BRTool: Structured business rules data
    BRTool-->>Agent: Requirements: 580 credit, 3.5% down
    
    Agent->>User: "FHA loans are government-backed<br/>Requirements: 580+ credit score,<br/>3.5% down payment, 43% DTI max"
    
    Note over Agent,Neo4j:  Clean separation: operational info + business rules
```

**Key Points:**
- Operational tools: General information, calculations, status checks
- Business rules tools: Actual thresholds, requirements, limits
- MCP: Protocol for accessing business rules from Neo4j
- Agent orchestrates: Combines operational and business rules as needed

---

## 6️⃣ Request Flow Through System

```mermaid
flowchart TD
    Start([👤 User Request]) --> Router{🎯 Intelligent Router<br/>LLM Classification}
    
    Router -->|Application related| AppAgent[📝 ApplicationAgent]
    Router -->|Guidance needed| AdvisorAgent[💼 MortgageAdvisorAgent]
    Router -->|Document upload| DocAgent[📄 DocumentAgent]
    Router -->|Property valuation| AppraisalAgent[🏠 AppraisalAgent]
    Router -->|Credit analysis| UnderwritingAgent[🔍 UnderwritingAgent]
    
    AppAgent --> AppProcess{Need<br/>Business Rules?}
    AdvisorAgent --> AdvisorProcess{Need<br/>Business Rules?}
    DocAgent --> DocProcess{Need<br/>Business Rules?}
    AppraisalAgent --> AppraisalProcess{Need<br/>Business Rules?}
    UnderwritingAgent --> UnderwritingProcess{Need<br/>Business Rules?}
    
    AppProcess -->|Yes| AppBR[Call scoped<br/>business rules tools]
    AppProcess -->|No| AppOp[Call operational<br/>tools only]
    
    AdvisorProcess -->|Yes| AdvisorBR[Call scoped<br/>business rules tools]
    AdvisorProcess -->|No| AdvisorOp[Call operational<br/>tools only]
    
    DocProcess -->|Yes| DocBR[Call scoped<br/>business rules tools]
    DocProcess -->|No| DocOp[Call operational<br/>tools only]
    
    AppraisalProcess -->|Yes| AppraisalBR[Call scoped<br/>business rules tools]
    AppraisalProcess -->|No| AppraisalOp[Call operational<br/>tools only]
    
    UnderwritingProcess -->|Yes| UnderwritingBR[Call scoped<br/>business rules tools]
    UnderwritingProcess -->|No| UnderwritingOp[Call operational<br/>tools only]
    
    AppBR --> SharedRules[(📚 shared/rules/)]
    AdvisorBR --> SharedRules
    DocBR --> SharedRules
    AppraisalBR --> SharedRules
    UnderwritingBR --> SharedRules
    
    SharedRules --> MCP[🔌 MCP Server]
    MCP --> Neo4j[(🗄️ Neo4j)]
    
    AppOp --> Neo4jDirect[(🗄️ Neo4j<br/>Direct Cypher)]
    AdvisorOp --> Neo4jDirect
    DocOp --> Neo4jDirect
    AppraisalOp --> Neo4jDirect
    UnderwritingOp --> Neo4jDirect
    
    AppBR --> Response([ Response to User])
    AppOp --> Response
    AdvisorBR --> Response
    AdvisorOp --> Response
    DocBR --> Response
    DocOp --> Response
    AppraisalBR --> Response
    AppraisalOp --> Response
    UnderwritingBR --> Response
    UnderwritingOp --> Response
    
    style Router fill:#4A90E2,stroke:#2E5C8A,stroke-width:2px,color:#fff
    style AppAgent fill:#50C878,stroke:#2E7D4E,stroke-width:2px,color:#fff
    style AdvisorAgent fill:#50C878,stroke:#2E7D4E,stroke-width:2px,color:#fff
    style DocAgent fill:#50C878,stroke:#2E7D4E,stroke-width:2px,color:#fff
    style AppraisalAgent fill:#50C878,stroke:#2E7D4E,stroke-width:2px,color:#fff
    style UnderwritingAgent fill:#50C878,stroke:#2E7D4E,stroke-width:2px,color:#fff
    style SharedRules fill:#FF6B6B,stroke:#C93838,stroke-width:2px,color:#fff
    style MCP fill:#F39C12,stroke:#B8770A,stroke-width:2px,color:#fff
```

---

## 7️⃣ Detailed Agent Configuration

| Agent | Operational Tools | Business Rules Tools | Total | Purpose |
|-------|------------------|---------------------|-------|---------|
| **ApplicationAgent** | 5 | 2 | **7** | Application intake, data collection, URLA generation |
| **MortgageAdvisorAgent** | 3 | 3 | **6** | Customer guidance, loan recommendations, qualification advice |
| **DocumentAgent** | 5 | 1 | **6** | Document processing, verification, status tracking |
| **AppraisalAgent** | 6 | 1 | **7** | **Appraisal scheduling, notifications**, property valuation, market analysis |
| **UnderwritingAgent** | 8 | 3 | **11** | Credit analysis, DTI calculation, underwriting decisions |

### ApplicationAgent Tools
**Operational (5):**
1. `receive_mortgage_application` - Collect application data
2. `retrieve_stored_application` - Retrieve saved applications
3. `check_application_completeness` - Verify data completeness
4. `perform_initial_qualification` - Calculate DTI/LTV (NO thresholds)
5. `generate_urla_form` - Generate URLA Form 1003

**Business Rules (2):**
1. `get_application_intake_rules` - Required fields, validation rules
2. `get_loan_program_requirements` - Program-specific requirements

---

### MortgageAdvisorAgent Tools
**Operational (3):**
1. `explain_loan_programs` - Explain loan types (NO specific requirements)
2. `recommend_loan_program` - Calculate metrics, suggest programs (NO qualification)
3. `check_qualification_requirements` - Check data completeness (NO thresholds)

**Business Rules (3):**
1. `get_loan_program_requirements` - Program requirements
2. `get_qualification_criteria` - Qualification thresholds
3. `get_underwriting_rules` - Credit/DTI/LTV requirements

---

### DocumentAgent Tools
**Operational (5):**
1. `process_uploaded_document` - Process document content
2. `extract_document_data` - Extract structured data
3. `get_document_status` - Check upload status
4. `verify_document_completeness` - List uploaded docs (NO requirements)
5. `validate_urla_form` - Validate URLA structure

**Business Rules (1):**
1. `get_document_requirements` - Required documents by loan type

---

### AppraisalAgent Tools
**Operational (6):**
1. `schedule_appraisal` - **Schedule appraisal appointments & send email notifications** ⭐ **NEW**
2. `analyze_property_value` - Property valuation analysis
3. `find_comparable_sales` - Research comparable properties
4. `assess_property_condition` - Property condition assessment
5. `review_appraisal_report` - Review appraisal documents
6. `evaluate_market_conditions` - Market trend evaluation

**Business Rules (1):**
1. `get_property_appraisal_rules` - LTV limits, appraisal standards

---

### UnderwritingAgent Tools
**Operational (8):**
1. `analyze_credit_risk` - Credit risk analysis (NO thresholds)
2. `calculate_debt_to_income` - DTI calculation (NO limits)
3. `evaluate_income_sources` - Income source evaluation
4. `run_aus_check` - AUS system integration
5. `make_underwriting_decision` - Decision analysis (NO approval rules)
6. `get_credit_score` - MCP: Real-time credit scores
7. `verify_identity` - MCP: Identity verification
8. `get_credit_report` - MCP: Credit reports

**Business Rules (3):**
1. `get_underwriting_rules` - Credit/DTI/LTV requirements
2. `get_aus_rules` - AUS system rules
3. `get_income_calculation_rules` - Income qualification rules

---

## 8️⃣ Code Organization Structure

```
app/agents/
├── shared/                          #  Shared utilities
│   ├── rules/                       # 🔴 Business Rules (MCP)
│   │   ├── __init__.py             
│   │   ├── get_application_intake_rules.py
│   │   ├── get_loan_program_requirements.py
│   │   ├── get_document_requirements.py
│   │   ├── get_qualification_criteria.py
│   │   ├── get_underwriting_rules.py
│   │   ├── get_aus_rules.py
│   │   ├── get_income_calculation_rules.py
│   │   └── get_property_appraisal_rules.py
│   └── prompt_loader.py
│
├── application_agent/               # 📝 Application Agent
│   ├── agent.py                    # Combines operational + business rules
│   ├── prompts.yaml
│   └── tools/                       # 🟢 Operational tools only
│       ├── __init__.py
│       ├── receive_mortgage_application.py
│       ├── retrieve_stored_application.py
│       ├── check_application_completeness.py
│       ├── perform_initial_qualification.py
│       └── generate_urla_form.py
│
├── mortgage_advisor_agent/          # 💼 Advisor Agent
│   ├── agent.py
│   ├── prompts.yaml
│   └── tools/                       # 🟢 Operational tools only
│       ├── __init__.py
│       ├── explain_loan_programs.py
│       ├── recommend_loan_program.py
│       └── check_qualification_requirements.py
│
├── document_agent/                  # 📄 Document Agent
│   ├── agent.py
│   ├── prompts.yaml
│   └── tools/                       # 🟢 Operational tools only
│       ├── __init__.py
│       ├── process_uploaded_document.py
│       ├── extract_document_data.py
│       ├── get_document_status.py
│       ├── verify_document_completeness.py
│       └── validate_urla_form.py
│
├── appraisal_agent/                 # 🏠 Appraisal Agent
│   ├── agent.py
│   ├── prompts.yaml
│   └── tools/                       # 🟢 Operational tools only
│       ├── __init__.py
│       ├── schedule_appraisal.py          # ⭐ NEW: Scheduling + Email
│       ├── analyze_property_value.py
│       ├── find_comparable_sales.py
│       ├── assess_property_condition.py
│       ├── review_appraisal_report.py
│       └── evaluate_market_conditions.py
│
├── underwriting_agent/              # 🔍 Underwriting Agent
│   ├── agent.py
│   ├── prompts.yaml
│   └── tools/                       # 🟢 Operational tools only
│       ├── __init__.py
│       ├── analyze_credit_risk.py
│       ├── calculate_debt_to_income.py
│       ├── evaluate_income_sources.py
│       ├── run_aus_check.py
│       ├── make_underwriting_decision.py
│       ├── get_credit_score.py (MCP)
│       ├── verify_identity.py (MCP)
│       └── get_credit_report.py (MCP)
│
└── mortgage_workflow.py             # 🎯 Router (5 agents, no business_rules_agent)
```

---

## 9️⃣ Key Architectural Decisions

###  **What Changed:**
1. **Deleted `business_rules_agent`** - No longer a separate agent
2. **Centralized business rules** - All in `shared/rules/`
3. **Scoped business rules** - Each agent gets only what it needs
4. **Clean tool separation** - Operational vs. business rules
5. **Direct access** - Agents call business rules directly (no routing)

###  **Design Principles:**
1. **Operational tools** → NO hardcoded business rules
2. **Business rules tools** → From `shared/rules/`, accessed via MCP
3. **Operational tools** → Call Neo4j DIRECTLY (for speed)
4. **Business rules tools** → Call Neo4j via MCP (for consistency)
5. **Each agent** → Only includes business rules it needs (scoped)

###  **Benefits:**
- **Faster response times** - No agent-to-agent routing
- **Better maintainability** - Business rules in one location
- **Clearer separation** - Operational vs. business logic
- **Easier testing** - Test operational and business rules independently
- **Flexible scaling** - Add new agents or rules without impacting others

---

## 🎯 **Summary**

The current architecture achieves:
-  **5 specialized agents** (no business_rules_agent)
-  **37 total tools** (27 operational, 10 business rules)
-  **Clean separation** (operational vs. business rules)
-  **Scoped business rules** (each agent has only what it needs)
-  **Centralized rules** (shared/rules/ directory)
-  **Direct access** (no routing to separate business rules agent)
-  **Email notifications** (SMTP-based appraisal scheduling) ⭐ **NEW**
-  **Real database integration** (Neo4j for appraisal orders)

**Result:** A production-ready, efficient, and scalable mortgage processing system!
