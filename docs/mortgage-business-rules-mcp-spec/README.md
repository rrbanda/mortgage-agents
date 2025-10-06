# Mortgage Business Rules MCP Server Specification

## Overview

This specification defines a standalone MCP server for mortgage business rules evaluation using GenMCP framework and Neo4j business rules engine. This is NOT a spec-kit generated specification, but rather a custom specification following modular documentation principles.

## Specification Structure

Following spec-driven development principles, this specification is organized into focused modules:

### Core Specification Files
- [`spec.md`](./spec.md) - Main specification document
- [`architecture.md`](./architecture.md) - System architecture and design
- [`api-contracts.md`](./api-contracts.md) - API contracts and schemas
- [`data-model.md`](./data-model.md) - Data models and schemas

### Implementation Files
- [`plan.md`](./plan.md) - Implementation plan and roadmap
- [`research.md`](./research.md) - Technical research and decisions
- [`quickstart.md`](./quickstart.md) - Quick start guide

### Supporting Files
- [`contracts/`](./contracts/) - API contracts and OpenAPI specs
- [`templates/`](./templates/) - Code templates and examples

## Quick Navigation

- **Getting Started**: See [quickstart.md](./quickstart.md)
- **Architecture**: See [architecture.md](./architecture.md)
- **API Reference**: See [api-contracts.md](./api-contracts.md)
- **Implementation**: See [plan.md](./plan.md)

## Key Features

 **Standalone Business Rules Server**: Focused solely on business rules evaluation  
 **GenMCP Framework**: Uses GenMCP for automatic MCP tool generation  
 **Neo4j Integration**: Direct queries to Neo4j business rules database  
 **Structured Input/Output**: Pydantic schemas for type safety  
 **8 Core Business Rules Tools**: Covering all major mortgage processing categories  
 **OpenAPI Compatible**: Auto-generated schemas for easy integration  

## Business Rules Categories

The MCP server exposes tools for these business rules categories:

1. **Application Processing Rules** - Application intake, validation, completeness
2. **Financial Assessment Rules** - Income calculation, debt analysis, property valuation
3. **Risk Scoring Rules** - Network risk analysis, behavioral scoring, market risk
4. **Compliance Rules** - Regulatory compliance, fair lending, privacy regulations
5. **Underwriting Rules** - Automated underwriting, manual rules, exception handling
6. **Pricing Rules** - Rate calculation, fee structure, market positioning
7. **Verification Rules** - Identity, document, and employment verification
8. **Process Optimization Rules** - Workflow optimization, analytics, predictive models

## Next Steps

1. Review the [main specification](./spec.md)
2. Understand the [architecture](./architecture.md)
3. Check the [implementation plan](./plan.md)
4. Follow the [quickstart guide](./quickstart.md)
