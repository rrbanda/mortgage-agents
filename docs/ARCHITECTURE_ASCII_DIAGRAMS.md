# Mortgage Agent System - ASCII Architecture Diagrams

**Refactored Architecture Overview**  
Last Updated: 2025-10-06

---

## 📋 Table of Contents

1. [System Architecture Overview](#1-system-architecture-overview)
2. [Agent Tool Breakdown](#2-agent-tool-breakdown)
3. [Data Access Patterns](#3-data-access-patterns)
4. [Example: How An Agent Uses Both Tool Types](#4-example-how-an-agent-uses-both-tool-types)
5. [Request Flow](#5-request-flow)
6. [Code Structure](#6-code-structure)
7. [Key Statistics](#7-key-statistics)
8. [Key Principles](#8-key-principles)

---

## 1️⃣ SYSTEM ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          👤 USER / CUSTOMER                              │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   🎯 INTELLIGENT ROUTER (LLM-Powered)                    │
│                  Classifies and routes to specialist agent               │
└───┬─────────┬──────────┬──────────┬──────────┬───────────────────────────┘
    │         │          │          │          │
    ▼         ▼          ▼          ▼          ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│   📝    │ │   💼    │ │   📄    │ │   🏠    │ │   🔍    │
│  APP    │ │ ADVISOR │ │   DOC   │ │APPRAISAL│ │UNDERWRIT│
│ AGENT   │ │  AGENT  │ │  AGENT  │ │  AGENT  │ │  AGENT  │
│         │ │         │ │         │ │         │ │         │
│ 5+2=7   │ │ 3+3=6   │ │ 5+1=6   │ │ 5+1=6   │ │ 8+3=11  │
│ tools   │ │ tools   │ │ tools   │ │ tools   │ │ tools   │
└────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘
     │           │           │           │           │
     │           │           │           │           │
     └───────────┴───────────┴───────────┴───────────┘
                             │
                             ▼
            ┌────────────────────────────────────┐
            │  📚 SHARED BUSINESS RULES          │
            │  app/agents/shared/rules/          │
            │                                    │
            │  • get_application_intake_rules    │
            │  • get_loan_program_requirements   │
            │  • get_document_requirements       │
            │  • get_qualification_criteria      │
            │  • get_underwriting_rules          │
            │  • get_aus_rules                   │
            │  • get_income_calculation_rules    │
            │  • get_property_appraisal_rules    │
            └────────────────┬───────────────────┘
                             │
                             ▼
            ┌────────────────────────────────────┐
            │  🔌 MCP SERVER                     │
            │  Model Context Protocol            │
            └────────────────┬───────────────────┘
                             │
                             ▼
            ┌────────────────────────────────────┐
            │  🗄️  NEO4J GRAPH DATABASE         │
            │  Business Rules Storage            │
            └────────────────────────────────────┘

KEY:
━━━ Operational Tools → Direct Neo4j Access (fast)
─── Business Rules Tools → Via MCP (consistent)
```

---

## 2️⃣ AGENT TOOL BREAKDOWN

```
╔════════════════════════════════════════════════════════════════════╗
║                     5 SPECIALIZED AGENTS                           ║
║                     26 Operational + 10 Business Rules = 36 Tools  ║
╚════════════════════════════════════════════════════════════════════╝

┌────────────────────────────────────────────────────────────────────┐
│ 📝 APPLICATION AGENT (7 tools: 5 operational + 2 business rules)   │
├────────────────────────────────────────────────────────────────────┤
│ OPERATIONAL (5):                                                   │
│  ✓ receive_mortgage_application     - Collect application data    │
│  ✓ retrieve_stored_application      - Get saved applications      │
│  ✓ check_application_completeness   - Verify data completeness    │
│  ✓ perform_initial_qualification    - Calculate DTI/LTV           │
│  ✓ generate_urla_form                - Generate Form 1003         │
│                                                                    │
│ BUSINESS RULES (2):                                                │
│  🔴 get_application_intake_rules     - Required fields            │
│  🔴 get_loan_program_requirements    - Program requirements       │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│ 💼 MORTGAGE ADVISOR AGENT (6 tools: 3 operational + 3 business)    │
├────────────────────────────────────────────────────────────────────┤
│ OPERATIONAL (3):                                                   │
│  ✓ explain_loan_programs             - Explain loan types         │
│  ✓ recommend_loan_program            - Suggest programs           │
│  ✓ check_qualification_requirements  - Check data completeness    │
│                                                                    │
│ BUSINESS RULES (3):                                                │
│  🔴 get_loan_program_requirements    - Program requirements       │
│  🔴 get_qualification_criteria       - Qualification thresholds   │
│  🔴 get_underwriting_rules           - Credit/DTI/LTV limits      │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│ 📄 DOCUMENT AGENT (6 tools: 5 operational + 1 business rules)      │
├────────────────────────────────────────────────────────────────────┤
│ OPERATIONAL (5):                                                   │
│  ✓ process_uploaded_document         - Process documents          │
│  ✓ extract_document_data             - Extract structured data    │
│  ✓ get_document_status               - Check upload status        │
│  ✓ verify_document_completeness      - List uploaded docs         │
│  ✓ validate_urla_form                - Validate URLA structure    │
│                                                                    │
│ BUSINESS RULES (1):                                                │
│  🔴 get_document_requirements        - Required documents         │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│ 🏠 APPRAISAL AGENT (6 tools: 5 operational + 1 business rules)     │
├────────────────────────────────────────────────────────────────────┤
│ OPERATIONAL (5):                                                   │
│  ✓ analyze_property_value            - Property valuation         │
│  ✓ find_comparable_sales             - Research comparables       │
│  ✓ assess_property_condition         - Condition assessment       │
│  ✓ review_appraisal_report           - Review appraisal docs      │
│  ✓ evaluate_market_conditions        - Market analysis            │
│                                                                    │
│ BUSINESS RULES (1):                                                │
│  🔴 get_property_appraisal_rules     - LTV limits, standards      │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│ 🔍 UNDERWRITING AGENT (11 tools: 8 operational + 3 business)       │
├────────────────────────────────────────────────────────────────────┤
│ OPERATIONAL (8):                                                   │
│  ✓ analyze_credit_risk               - Credit risk analysis       │
│  ✓ calculate_debt_to_income          - DTI calculation            │
│  ✓ evaluate_income_sources           - Income evaluation          │
│  ✓ run_aus_check                     - AUS integration            │
│  ✓ make_underwriting_decision        - Decision analysis          │
│  ✓ get_credit_score (MCP)            - Real-time credit scores    │
│  ✓ verify_identity (MCP)             - Identity verification      │
│  ✓ get_credit_report (MCP)           - Credit reports             │
│                                                                    │
│ BUSINESS RULES (3):                                                │
│  🔴 get_underwriting_rules           - Credit/DTI/LTV limits      │
│  🔴 get_aus_rules                    - AUS system rules            │
│  🔴 get_income_calculation_rules     - Income qualification       │
└────────────────────────────────────────────────────────────────────┘

LEGEND:
  ✓  = Operational Tool (NO hardcoded business rules)
  🔴 = Business Rules Tool (from shared/rules/, via MCP)
```

---

## 3️⃣ DATA ACCESS PATTERNS

```
╔═══════════════════════════════════════════════════════════════╗
║          TWO TYPES OF TOOLS = TWO DATA ACCESS PATHS          ║
╚═══════════════════════════════════════════════════════════════╝

┌───────────────────────────────────────────────────────────────┐
│ PATH 1: OPERATIONAL TOOLS (Fast, Direct Access)              │
└───────────────────────────────────────────────────────────────┘

    Agent calls operational tool
         │
         ▼
    ┌──────────────────┐
    │ Operational Tool │  Examples:
    │                  │  - calculate_debt_to_income
    │ • Calculate      │  - extract_document_data
    │ • Process        │  - analyze_property_value
    │ • Extract        │
    │ • Display        │  NO hardcoded business rules
    └────────┬─────────┘  Just operations & calculations
             │
             │ Direct Cypher Queries
             ▼
    ┌─────────────────┐
    │   NEO4J DB      │
    │  (Direct)       │
    └─────────────────┘


┌───────────────────────────────────────────────────────────────┐
│ PATH 2: BUSINESS RULES TOOLS (Consistent, Via MCP)           │
└───────────────────────────────────────────────────────────────┘

    Agent calls business rules tool
         │
         ▼
    ┌──────────────────────┐
    │ Business Rules Tool  │  Examples:
    │                      │  - get_underwriting_rules
    │ From shared/rules/   │  - get_loan_program_requirements
    │                      │  - get_qualification_criteria
    │ • Query rules        │
    │ • Get thresholds     │  Returns actual requirements
    │ • Fetch requirements │  (credit scores, DTI limits, etc)
    └──────────┬───────────┘
               │
               │ Via MCP Protocol
               ▼
    ┌──────────────────────┐
    │    MCP SERVER        │
    │                      │
    │ - Standardized API   │
    │ - Consistent format  │
    │ - Rule validation    │
    └──────────┬───────────┘
               │
               │ Cypher Queries
               ▼
    ┌──────────────────────┐
    │   NEO4J DB           │
    │  (Via MCP)           │
    └──────────────────────┘
```

---

## 4️⃣ EXAMPLE: HOW AN AGENT USES BOTH TOOL TYPES

```
╔════════════════════════════════════════════════════════════════╗
║  EXAMPLE: MortgageAdvisorAgent answering "Can I get FHA?"     ║
╚════════════════════════════════════════════════════════════════╝

User: "I have 600 credit score, make $5k/month, $500 debts.
       Can I qualify for FHA loan?"
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│  MortgageAdvisorAgent decides which tools to use             │
└──────────────────────────────────────────────────────────────┘
       │
       ├──────────────────┬────────────────────────────────┐
       │                  │                                │
       ▼                  ▼                                ▼
┌─────────────┐  ┌──────────────────┐  ┌─────────────────────┐
│ OPERATIONAL │  │ OPERATIONAL      │  │ BUSINESS RULES      │
│ TOOL        │  │ TOOL             │  │ TOOL                │
└─────────────┘  └──────────────────┘  └─────────────────────┘
│               │                  │
│ calculate_   │  │ recommend_      │  │ get_loan_program_   │
│ debt_to_     │  │ loan_program    │  │ requirements        │
│ income       │  │                 │  │                     │
│               │                  │
│ Input:       │  │ Input:          │  │ Input:              │
│ • $5k income │  │ • Credit: 600   │  │ • Program: "FHA"    │
│ • $500 debts │  │ • DTI: 10%      │  │                     │
│               │  │ • Down: $10k    │  │                     │
│ Output:      │  │                 │  │ Output:             │
│ ✓ DTI = 10%  │  │ Output:         │  │ 🔴 Min Credit: 580  │
│              │  │ ✓ "FHA might    │  │ 🔴 Min Down: 3.5%   │
│ NO RULES!    │  │    be suitable" │  │ 🔴 Max DTI: 43%     │
│ Just math    │  │                 │  │                     │
│              │  │ NO THRESHOLDS!  │  │ ACTUAL RULES!       │
└──────┬───────┘  └────────┬────────┘  └──────┬──────────────┘
       │                   │                  │
       └───────────────────┴──────────────────┘
                           │
                           ▼
       ┌────────────────────────────────────────┐
       │  Agent combines all results:           │
       │                                        │
       │  "Your DTI is 10% (excellent!)         │
       │   FHA loan requirements:               │
       │   ✓ Credit 580+ (you have 600 ✓)      │
       │   ✓ Down payment 3.5%                  │
       │   ✓ DTI max 43% (you have 10% ✓)      │
       │                                        │
       │    You qualify for FHA!"             │
       └────────────────────────────────────────┘
```

---

## 5️⃣ REQUEST FLOW

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER MAKES REQUEST                          │
│     "I want to apply for a mortgage with 620 credit score"     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │   INTELLIGENT ROUTER │
                  │   (LLM Classification)│
                  └──────────┬───────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
       Application?      Document?       Guidance?
            │                │                │
            ▼                ▼                ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │ Application  │  │  Document    │  │  Mortgage    │
    │    Agent     │  │   Agent      │  │   Advisor    │
    └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
           │                 │                 │
           ▼                 ▼                 ▼
    Uses operational    Uses operational    Uses operational
    + business rules    + business rules    + business rules
           │                 │                 │
           └─────────────────┴─────────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │   RESPONSE TO USER   │
                  └──────────────────────┘
```

---

## 6️⃣ CODE STRUCTURE

```
app/agents/
│
├── shared/
│   └── rules/                          🔴 BUSINESS RULES (Shared)
│       ├── __init__.py
│       ├── get_application_intake_rules.py
│       ├── get_loan_program_requirements.py
│       ├── get_document_requirements.py
│       ├── get_qualification_criteria.py
│       ├── get_underwriting_rules.py
│       ├── get_aus_rules.py
│       ├── get_income_calculation_rules.py
│       └── get_property_appraisal_rules.py
│
├── application_agent/
│   ├── agent.py                       ⚙️  Combines operational + BR
│   └── tools/                         ✓  OPERATIONAL ONLY
│       ├── receive_mortgage_application.py
│       ├── retrieve_stored_application.py
│       ├── check_application_completeness.py
│       ├── perform_initial_qualification.py
│       └── generate_urla_form.py
│
├── mortgage_advisor_agent/
│   ├── agent.py                       ⚙️  Combines operational + BR
│   └── tools/                         ✓  OPERATIONAL ONLY
│       ├── explain_loan_programs.py
│       ├── recommend_loan_program.py
│       └── check_qualification_requirements.py
│
├── document_agent/
│   ├── agent.py                       ⚙️  Combines operational + BR
│   └── tools/                         ✓  OPERATIONAL ONLY
│       ├── process_uploaded_document.py
│       ├── extract_document_data.py
│       ├── get_document_status.py
│       ├── verify_document_completeness.py
│       └── validate_urla_form.py
│
├── appraisal_agent/
│   ├── agent.py                       ⚙️  Combines operational + BR
│   └── tools/                         ✓  OPERATIONAL ONLY
│       ├── analyze_property_value.py
│       ├── find_comparable_sales.py
│       ├── assess_property_condition.py
│       ├── review_appraisal_report.py
│       └── evaluate_market_conditions.py
│
├── underwriting_agent/
│   ├── agent.py                       ⚙️  Combines operational + BR
│   └── tools/                         ✓  OPERATIONAL ONLY
│       ├── analyze_credit_risk.py
│       ├── calculate_debt_to_income.py
│       ├── evaluate_income_sources.py
│       ├── run_aus_check.py
│       ├── make_underwriting_decision.py
│       ├── get_credit_score.py (MCP)
│       ├── verify_identity.py (MCP)
│       └── get_credit_report.py (MCP)
│
└── mortgage_workflow.py               🎯 ROUTER (5 agents only)
```

---

## 7️⃣ KEY STATISTICS

```
╔════════════════════════════════════════════════════════════════╗
║                    SYSTEM STATISTICS                           ║
╚════════════════════════════════════════════════════════════════╝

┌────────────────────────────────────────────────────────────────┐
│  AGENTS: 5 Total                                               │
│  ├─ ApplicationAgent          (7 tools)                        │
│  ├─ MortgageAdvisorAgent      (6 tools)                        │
│  ├─ DocumentAgent             (6 tools)                        │
│  ├─ AppraisalAgent            (6 tools)                        │
│  └─ UnderwritingAgent         (11 tools)                       │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│  TOOLS: 36 Total                                               │
│  ├─ Operational Tools         26 tools (72%)                   │
│  └─ Business Rules Tools      10 tools (28%)                   │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│  BUSINESS RULES: 8 Unique Rule Sets (in shared/rules/)        │
│  ├─ get_application_intake_rules                               │
│  ├─ get_loan_program_requirements                              │
│  ├─ get_document_requirements                                  │
│  ├─ get_qualification_criteria                                 │
│  ├─ get_underwriting_rules                                     │
│  ├─ get_aus_rules                                              │
│  ├─ get_income_calculation_rules                               │
│  └─ get_property_appraisal_rules                               │
└────────────────────────────────────────────────────────────────┘
```

---

## 8️⃣ KEY PRINCIPLES

```
╔════════════════════════════════════════════════════════════════╗
║               ARCHITECTURAL PRINCIPLES                         ║
╚════════════════════════════════════════════════════════════════╝

 SEPARATION OF CONCERNS
   ┌─────────────────────────────────────────────────────────┐
   │ Operational Tools:   NO hardcoded business rules        │
   │ Business Rules Tools: From shared/rules/ via MCP        │
   └─────────────────────────────────────────────────────────┘

 DATA ACCESS
   ┌─────────────────────────────────────────────────────────┐
   │ Operational Tools:   Direct Neo4j access (fast)         │
   │ Business Rules Tools: Via MCP (consistent)              │
   └─────────────────────────────────────────────────────────┘

 SCOPED BUSINESS RULES
   ┌─────────────────────────────────────────────────────────┐
   │ Each agent gets ONLY the business rules it needs        │
   │ Not all 8 rules - just relevant ones                    │
   └─────────────────────────────────────────────────────────┘

 NO SEPARATE BUSINESS RULES AGENT
   ┌─────────────────────────────────────────────────────────┐
   │ Agents access business rules DIRECTLY                   │
   │ No routing to separate agent needed                     │
   └─────────────────────────────────────────────────────────┘

 CENTRALIZED BUSINESS RULES
   ┌─────────────────────────────────────────────────────────┐
   │ All business rules in: app/agents/shared/rules/         │
   │ Single source of truth for all agents                   │
   └─────────────────────────────────────────────────────────┘
```

---

## 📊 Quick Summary Table

| Agent | Operational Tools | Business Rules | Total | Key Purpose |
|-------|------------------|----------------|-------|-------------|
| ApplicationAgent | 5 | 2 | 7 | Application intake & URLA |
| MortgageAdvisorAgent | 3 | 3 | 6 | Guidance & recommendations |
| DocumentAgent | 5 | 1 | 6 | Document processing |
| AppraisalAgent | 5 | 1 | 6 | Property valuation |
| UnderwritingAgent | 8 | 3 | 11 | Credit & underwriting |
| **TOTAL** | **26** | **10** | **36** | **Complete mortgage system** |

---

## 🎯 Benefits of This Architecture

1. **⚡ Faster Response Times**
   - No agent-to-agent routing
   - Direct access to business rules
   - Operational tools use direct Neo4j queries

2. **🧹 Cleaner Code**
   - Clear separation: operational vs business rules
   - No hardcoded business logic in operational tools
   - Single source of truth for business rules

3. **🔧 Easier Maintenance**
   - Business rules in one location (`shared/rules/`)
   - Changes to rules don't affect operational code
   - Each agent only has rules it needs (scoped)

4. **🧪 Better Testing**
   - Test operational and business rules independently
   - Mock business rules easily for operational tests
   - Validate business rules separately

5. **📈 Scalable**
   - Add new agents without touching business rules
   - Add new business rules without touching operational code
   - Each agent is independent and focused

---

**🎉 This architecture provides a clean, maintainable, and efficient mortgage processing system!**
