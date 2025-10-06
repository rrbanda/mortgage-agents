# MCP Migration Guide

This guide helps you update import statements and references after moving MCP-related files to the organized `mcp/` directory structure.

## Import Path Changes

### Before (Old Structure)
```python
# Direct imports from root
from mcp_config import get_mcp_client
from mcp_direct_client import MCPClient
from mcp_tools import get_twilio_mcp_tools
from app.utils.mcp_integration import get_mcp_tools
```

### After (New Structure)
```python
# Organized imports from mcp/ directory
from mcp.clients.direct.mcp_config import get_mcp_client
from mcp.clients.direct.mcp_direct_client import MCPClient
from mcp.clients.langchain.mcp_tools import get_twilio_mcp_tools
from mcp.clients.langchain.mcp_integration import get_mcp_tools
```

## Files That Need Import Updates

### 1. Agent Files
Update these files to use the new MCP import paths:

- `app/agents/application_agent/__init__.py`
- `app/agents/underwriting_agent/__init__.py`
- `app/agents/document_agent/__init__.py`
- `app/agents/mortgage_advisor_agent/__init__.py`
- `app/agents/appraisal_agent/__init__.py`

### 2. Workflow Files
- `app/agents/mortgage_workflow.py`

### 3. Configuration Files
- `app/utils/config.py` (if it imports MCP modules)

## Step-by-Step Migration

### Step 1: Update Agent Tool Imports
In each agent's `__init__.py` file, update MCP tool imports:

```python
# OLD
from mcp_tools import get_twilio_mcp_tools
from app.utils.mcp_integration import get_mcp_tools

# NEW
from mcp.clients.langchain.mcp_tools import get_twilio_mcp_tools
from mcp.clients.langchain.mcp_integration import get_mcp_tools
```

### Step 2: Update Workflow Imports
In `app/agents/mortgage_workflow.py`:

```python
# OLD
from app.utils.mcp_integration import get_mcp_tools

# NEW
from mcp.clients.langchain.mcp_integration import get_mcp_tools
```

### Step 3: Update Configuration Imports
In `app/utils/config.py` (if applicable):

```python
# OLD
from mcp_config import setup_twilio_mcp

# NEW
from mcp.clients.direct.mcp_config import setup_twilio_mcp
```

## Automated Migration Script

You can use this script to automatically update imports:

```bash
#!/bin/bash
# migrate_mcp_imports.sh

# Update agent files
find app/agents -name "*.py" -exec sed -i 's/from mcp_tools import/from mcp.clients.langchain.mcp_tools import/g' {} \;
find app/agents -name "*.py" -exec sed -i 's/from app.utils.mcp_integration import/from mcp.clients.langchain.mcp_integration import/g' {} \;

# Update workflow files
find app/agents -name "*.py" -exec sed -i 's/from mcp_config import/from mcp.clients.direct.mcp_config import/g' {} \;

# Update config files
find app/utils -name "*.py" -exec sed -i 's/from mcp_config import/from mcp.clients.direct.mcp_config import/g' {} \;
```

## Testing After Migration

### 1. Test Import Resolution
```python
# Test each import path
try:
    from mcp.clients.langchain.mcp_integration import get_mcp_tools
    print(" MCP integration import successful")
except ImportError as e:
    print(f" MCP integration import failed: {e}")

try:
    from mcp.clients.direct.mcp_config import get_mcp_client
    print(" MCP config import successful")
except ImportError as e:
    print(f" MCP config import failed: {e}")
```

### 2. Test MCP Functionality
```python
# Test MCP tools loading
from mcp.clients.langchain.mcp_integration import get_mcp_tools
tools = get_mcp_tools()
print(f"Loaded {len(tools)} MCP tools")
```

### 3. Test Agent Integration
```python
# Test agent tool loading
from app.agents.application_agent import get_all_application_agent_tools
tools = get_all_application_agent_tools()
print(f"Application agent has {len(tools)} tools")
```

## Common Issues and Solutions

### Issue 1: ImportError: No module named 'mcp'
**Solution**: Ensure you're running from the project root directory, or add the project root to your Python path.

### Issue 2: Circular Import Errors
**Solution**: Check for circular imports between MCP modules and agent modules. You may need to use lazy imports.

### Issue 3: Missing Dependencies
**Solution**: Ensure all required packages are installed:
```bash
pip install -r requirements.txt
```

## Verification Checklist

- [ ] All agent files can import MCP tools without errors
- [ ] MCP tools are discoverable by agents
- [ ] Credit check MCP server starts successfully
- [ ] LangGraph workflow can use MCP tools
- [ ] No circular import errors
- [ ] All tests pass

## Rollback Plan

If issues arise, you can temporarily rollback by:

1. **Revert import changes**: Change imports back to original paths
2. **Move files back**: Move MCP files back to their original locations
3. **Update imports**: Update imports to use original paths

## Support

If you encounter issues during migration:

1. Check the `mcp/INDEX.md` for quick reference
2. Review the `mcp/README.md` for detailed documentation
3. Test individual components using the examples in `mcp/examples/`
4. Check the troubleshooting section in `mcp/servers/credit-check/README.md`
