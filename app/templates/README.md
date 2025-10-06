# Tool Templates

This directory contains templates and examples for creating mortgage agent tools.

## Files

### `12_factor_tool_template.py`
A comprehensive template demonstrating 12-factor compliant tool development for mortgage agents.

## 12-Factor Tool Template

The `12_factor_tool_template.py` demonstrates best practices for creating mortgage agent tools that follow the 12-factor methodology:

### Key Features

1. **Factor 1: Natural Language → Tool Calls**
   - Uses `parse_complete_mortgage_input()` instead of regex
   - Handles natural language input gracefully
   - No hardcoded patterns or brittle parsing

2. **Factor 4: Tools as Structured Outputs**
   - Predictable, structured responses
   - Consistent output format
   - Easy for LLMs to process

3. **Factor 8: Own Your Control Flow**
   - Clear business logic flow
   - Explicit decision making
   - No hidden dependencies

4. **Factor 9: Compact Errors**
   - Clear, actionable error messages
   - Graceful failure handling
   - User-friendly feedback

### Example Tools Included

1. **`check_application_completeness_12factor`**
   - Analyzes mortgage application completeness
   - Determines required documents based on loan type and employment
   - Provides structured completeness report

2. **`track_application_status_12factor`**
   - Tracks application status and progress
   - Provides detailed status information
   - Shows completion milestones

3. **`extract_document_data_12factor`**
   - Extracts structured data from documents
   - Returns JSON format for easy processing
   - Validates extracted information

### Usage

```python
from app.templates.12_factor_tool_template import (
    check_application_completeness_12factor,
    track_application_status_12factor,
    extract_document_data_12factor
)

# Use in agent tool lists
tools = [
    check_application_completeness_12factor,
    track_application_status_12factor,
    extract_document_data_12factor
]
```

### Testing

The template includes built-in test cases:

```bash
cd app/templates/
python 12_factor_tool_template.py
```

### Customization

To create your own 12-factor compliant tool:

1. **Copy the template structure**
2. **Update the tool function name and description**
3. **Implement your business logic**
4. **Use `parse_complete_mortgage_input()` for input parsing**
5. **Return structured, predictable output**
6. **Include comprehensive error handling**

### Best Practices

- **Always use the shared input parser** instead of regex
- **Return structured, consistent output**
- **Include clear error messages**
- **Test with various natural language inputs**
- **Document your tool's purpose and usage**
- **Follow the established naming conventions**

### Integration with Agents

These tools can be easily integrated into any mortgage agent:

```python
# In agent __init__.py
from app.templates.12_factor_tool_template import (
    check_application_completeness_12factor,
    track_application_status_12factor
)

def get_all_application_agent_tools() -> List[BaseTool]:
    return [
        # Existing tools...
        check_application_completeness_12factor,
        track_application_status_12factor,
        # More tools...
    ]
```

## Future Templates

Additional templates will be added for:
- Document processing tools
- Credit analysis tools
- Property evaluation tools
- Communication tools
- Compliance checking tools
