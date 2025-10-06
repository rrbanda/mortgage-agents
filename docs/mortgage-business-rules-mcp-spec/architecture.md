# System Architecture

## Architecture Overview

```
External Client (MCP Inspector, Claude, Other LLMs)
    ↓ MCP Protocol (streamable-http)
┌──────────────────────────────────────────────────────────┐
│ gen-mcp Binary (Go)                                      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  MCP Tools (Auto-generated from mcpfile.yaml)           │
│  ├─ evaluate_application_intake_rules                   │
│  ├─ check_qualification_thresholds                      │
│  ├─ assess_credit_score_rules                           │
│  ├─ evaluate_income_calculation_rules                   │
│  ├─ check_document_verification_rules                   │
│  ├─ assess_underwriting_rules                           │
│  ├─ evaluate_pricing_rules                              │
│  └─ check_compliance_rules                              │
│                                                          │
│  gen-mcp → HTTP Proxy → Backend Service                 │
│  ┌────────────────────────────────────────────┐         │
│  │ MCP Protocol Translation:                   │         │
│  │ 1. Receive MCP tool call                    │         │
│  │ 2. Convert to HTTP POST request             │         │
│  │ 3. Forward to backend service               │         │
│  │ 4. Convert HTTP response to MCP result      │         │
│  └────────────────────────────────────────────┘         │
│                                                          │
└──────────────────────────────────────────────────────────┘
    ↓ HTTP (port 3000)
┌──────────────────────────────────────────────────────────┐
│ Business Rules Backend Service (Python/FastAPI)         │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  FastAPI Endpoints                                       │
│  ├─ POST /tools/evaluate_application_intake_rules       │
│  ├─ POST /tools/check_qualification_thresholds          │
│  ├─ POST /tools/assess_credit_score_rules               │
│  ├─ POST /tools/evaluate_income_calculation_rules       │
│  ├─ POST /tools/check_document_verification_rules       │
│  ├─ POST /tools/assess_underwriting_rules               │
│  ├─ POST /tools/evaluate_pricing_rules                  │
│  ├─ POST /tools/check_compliance_rules                  │
│  └─ GET /health                                          │
│                                                          │
│  Business Rules Engine                                   │
│  ┌────────────────────────────────────────────┐         │
│  │ Business Rules Evaluation Pattern:          │         │
│  │ 1. Receive structured input data            │         │
│  │ 2. Query Neo4j for relevant rules           │         │
│  │ 3. Apply rules to input data                │         │
│  │ 4. Return evaluation results                │         │
│  └────────────────────────────────────────────┘         │
│                                                          │
│  Neo4j Rules Engine (Based on business_rules/)          │
│  ├─ Application Processing Rules                        │
│  ├─ Financial Assessment Rules                          │
│  ├─ Risk Scoring Rules                                  │
│  ├─ Compliance Rules                                    │
│  ├─ Underwriting Rules                                  │
│  ├─ Pricing Rules                                       │
│  ├─ Verification Rules                                  │
│  └─ Process Optimization Rules                          │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. GenMCP Server Layer

**Purpose**: Main server that exposes MCP tools and handles protocol communication

**Components**:
- **MCP Server**: GenMCP server instance
- **Tool Registry**: Auto-generated tool definitions
- **Protocol Handler**: MCP protocol implementation
- **Request Router**: Routes requests to appropriate tools

**Responsibilities**:
- Handle MCP protocol communication
- Route requests to business rules tools
- Manage server lifecycle and configuration
- Provide health checks and monitoring

### 2. Business Rules Tools Layer

**Purpose**: Individual tools for each business rules category

**Components**:
- **Application Rules Tools**: Application intake and validation
- **Qualification Rules Tools**: Qualification threshold evaluation
- **Financial Rules Tools**: Income and financial assessment
- **Risk Rules Tools**: Credit score and risk assessment
- **Compliance Rules Tools**: Regulatory compliance checking
- **Underwriting Rules Tools**: Underwriting decision support
- **Pricing Rules Tools**: Rate and fee calculation
- **Verification Rules Tools**: Document and identity verification

**Responsibilities**:
- Receive structured input data
- Query Neo4j for relevant business rules
- Apply rules to input data
- Return structured evaluation results

### 3. Rules Engine Layer

**Purpose**: Core business rules evaluation engine

**Components**:
- **Neo4j Connection Manager**: Database connection management
- **Query Builder**: Builds Neo4j queries for different rule types
- **Rule Evaluator**: Applies business rules to input data
- **Result Formatter**: Formats evaluation results

**Responsibilities**:
- Manage Neo4j database connections
- Build and execute rule queries
- Apply business logic to input data
- Format and return results

### 4. Data Layer

**Purpose**: Data models and schemas for input/output

**Components**:
- **Input Schemas**: Pydantic models for input validation
- **Output Schemas**: Pydantic models for result formatting
- **Business Rules Models**: Neo4j data models for rules

**Responsibilities**:
- Define data structures for input/output
- Validate input data against schemas
- Serialize/deserialize data for API communication
- Ensure type safety across the system

## Data Flow

### 1. Request Flow

```
Client Request
    ↓
MCP Protocol Handler
    ↓
Tool Router
    ↓
Business Rules Tool
    ↓
Rules Engine
    ↓
Neo4j Database
    ↓
Rule Evaluation
    ↓
Result Formatting
    ↓
Response to Client
```

### 2. Error Handling Flow

```
Error Occurs
    ↓
Error Classification
    ↓
Error Logging
    ↓
Error Response Generation
    ↓
Client Error Response
```

## Technology Stack

### Core Technologies
- **Python 3.11+**: Primary programming language
- **GenMCP**: MCP server framework
- **Neo4j**: Graph database for business rules
- **Pydantic**: Data validation and serialization
- **FastAPI**: HTTP server framework (for REST API fallback)

### Supporting Technologies
- **Docker**: Containerization
- **Docker Compose**: Local development environment
- **pytest**: Testing framework
- **black**: Code formatting
- **mypy**: Type checking

## Deployment Architecture

### Development Environment
```
Developer Machine
    ↓
Docker Compose
    ├─ Neo4j Database
    └─ MCP Server
```

### Production Environment
```
Load Balancer
    ↓
MCP Server Cluster
    ├─ Instance 1
    ├─ Instance 2
    └─ Instance N
    ↓
Neo4j Cluster
    ├─ Primary Node
    ├─ Secondary Node
    └─ Read Replicas
```

## Security Architecture

### Authentication & Authorization
- **API Keys**: For client authentication
- **Role-based Access**: Different access levels for different rule categories
- **Audit Logging**: Track all rule evaluations and access

### Data Security
- **Encryption in Transit**: TLS for all communications
- **Encryption at Rest**: Database encryption
- **Data Masking**: Sensitive data protection
- **Access Controls**: Database access restrictions

## Monitoring & Observability

### Metrics
- **Performance Metrics**: Response times, throughput
- **Business Metrics**: Rule evaluation counts, success rates
- **System Metrics**: CPU, memory, disk usage
- **Error Metrics**: Error rates, error types

### Logging
- **Structured Logging**: JSON-formatted logs
- **Log Levels**: DEBUG, INFO, WARN, ERROR
- **Log Aggregation**: Centralized log collection
- **Log Retention**: Configurable retention policies

### Alerting
- **Performance Alerts**: Response time thresholds
- **Error Alerts**: Error rate thresholds
- **System Alerts**: Resource usage thresholds
- **Business Alerts**: Rule evaluation failures

## Scalability Considerations

### Horizontal Scaling
- **Stateless Design**: No server-side state
- **Load Balancing**: Distribute requests across instances
- **Database Connection Pooling**: Efficient database connections
- **Caching**: Redis for rule caching

### Performance Optimization
- **Query Optimization**: Optimized Neo4j queries
- **Connection Pooling**: Efficient database connections
- **Async Processing**: Non-blocking I/O operations
- **Result Caching**: Cache frequently accessed rules

## Integration Patterns

### MCP Integration
- **Direct MCP**: stdio-based communication
- **HTTP MCP**: HTTP-based MCP protocol
- **Tool Discovery**: Automatic tool registration

### REST API Integration
- **OpenAPI Spec**: Auto-generated API documentation
- **REST Endpoints**: HTTP endpoints for each tool
- **JSON Schema**: Request/response validation

### Database Integration
- **Neo4j Driver**: Official Neo4j Python driver
- **Connection Pooling**: Efficient connection management
- **Query Optimization**: Optimized Cypher queries
- **Transaction Management**: Proper transaction handling
