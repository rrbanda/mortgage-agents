"""
Production Multi-Agent Routing Coordinator
Following LangGraph's official routing pattern with structured output

Based on LangGraph documentation: 
https://langchain-ai.github.io/langgraph/tutorials/introduction/#routing

This implements the routing workflow pattern where an LLM classifies 
input and directs it to specialized followup tasks.
"""

from typing import Annotated, Sequence, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

# Removed parser imports - agents now handle extraction via LLM

# Import individual agents
from .application_agent import create_application_agent
from .mortgage_advisor_agent import create_mortgage_advisor_agent  
from .document_agent import create_document_agent
from .appraisal_agent import create_appraisal_agent
from .underwriting_agent import create_underwriting_agent

# Import LLM and file processing
from utils import get_llm, extract_message_content_and_files, clean_file_entries_from_messages


class MortgageRoutingState(TypedDict):
    """State for multi-agent mortgage routing workflow"""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    route_decision: str
    current_agent: str  # Track which agent is currently active


class RouteClassification(BaseModel):
    """Schema for structured output routing classification"""
    agent: Literal[
        "mortgage_advisor_agent", 
        "application_agent", 
        "document_agent", 
        "appraisal_agent", 
        "underwriting_agent"
    ] = Field(description="The specialist agent best suited to handle this mortgage request")


# Removed parse_input_node - agents now handle extraction via LLM


def create_routing_node():
    """Create LLM-powered routing node following LangGraph routing pattern"""
    
    llm = get_llm()
    classifier = llm.with_structured_output(RouteClassification)
    
    def router(state: MortgageRoutingState):
        """Route classification using LLM with structured output"""
        
        # Get the original message content for context
        messages = state.get("messages", [])
        if not messages:
            return {"route_decision": "mortgage_advisor_agent"}
        
        # Get user message content for context
        user_messages = [msg for msg in messages if getattr(msg, 'type', None) == 'human']
        if not user_messages:
            return {"route_decision": "mortgage_advisor_agent"}
        
        last_user_message = user_messages[-1]
        
        # Extract content for routing context
        try:
            # Extract full content including files for agent reasoning
            parsed_content = extract_message_content_and_files(last_user_message)
            content = parsed_content['full_content']  # LLM sees everything
            
        except Exception:
            # Fallback to original parsing logic if enhanced parser fails
            content = ""
            if hasattr(last_user_message, 'content'):
                raw_content = last_user_message.content
                if isinstance(raw_content, list):
                    content = raw_content[0].get('text', '') if raw_content and isinstance(raw_content[0], dict) else str(raw_content[0]) if raw_content else ""
                else:
                    content = str(raw_content)
        
        if not content.strip():
            return {"route_decision": "mortgage_advisor_agent"}
        
        # SAFETY CHECK: Pre-routing document upload detection
        document_indicators = [
            "UPLOADED DOCUMENTS:",
            "**UPLOADED DOCUMENTS:**",
            "uploaded documents",
            "attached documents", 
            "submitted documents",
            "document upload",
            "file upload"
        ]
        
        content_lower = content.lower()
        for indicator in document_indicators:
            if indicator.lower() in content_lower:
                print(f"🔍 Pre-routing: Document upload detected via '{indicator}' - routing to document_agent")
                return {"route_decision": "document_agent"}
        
        # Also check routing hint from file processing
        try:
            if parsed_content.get('routing_hint') == 'documents' and parsed_content.get('has_files'):
                print(f"🔍 Pre-routing: File upload detected via routing_hint - routing to document_agent")
                return {"route_decision": "document_agent"}
        except Exception:
            # parsed_content might not be defined if earlier extraction failed
            pass
        
        # Build conversation context for context-aware routing
        conversation_context = ""
        if len(messages) >= 2:
            # Get the last few messages to understand conversation flow
            recent_messages = messages[-3:] if len(messages) >= 3 else messages[-2:]
            for msg in recent_messages:
                sender = "Agent" if getattr(msg, 'type', None) == 'ai' else "User"
                msg_content = getattr(msg, 'content', str(msg))
                if isinstance(msg_content, list) and msg_content:
                    # Handle multimodal content
                    msg_content = str(msg_content[0].get('text', '')) if isinstance(msg_content[0], dict) else str(msg_content[0])
                elif not isinstance(msg_content, str):
                    msg_content = str(msg_content)
                conversation_context += f"{sender}: {msg_content[:200]}...\n" if len(msg_content) > 200 else f"{sender}: {msg_content}\n"
        
        # CONTEXT-AWARE LLM classification
        classification_prompt = [
            SystemMessage(content="""You are an intelligent mortgage processing coordinator. Use conversation context to understand the flow and route appropriately.

**DOCUMENT UPLOAD DETECTION (ABSOLUTE PRIORITY):**
- If the message contains "UPLOADED DOCUMENTS:" anywhere in the text, route to "document_agent" IMMEDIATELY
- If the message contains "**UPLOADED DOCUMENTS:**" anywhere in the text, route to "document_agent" IMMEDIATELY  
- If user says they "uploaded", "attached", or "submitted" documents, route to "document_agent"
- Document uploads ALWAYS go to document_agent regardless of other content

**CONTEXT-AWARE ROUTING GUIDELINES:**

**CONVERSATION CONTEXT RULES (HIGH PRIORITY):**
- If the previous agent asked a specific question and the user is providing an answer, route BACK to that same agent
- If ApplicationAgent asked for personal info (name, DOB, etc.) and user provides it, route to "application_agent"
- If DocumentAgent asked about documents and user responds, route to "document_agent"
- Continue with the same agent until their task is completely finished

**ROUTING GUIDELINES:**

**document_agent**: Document processing, verification, uploads (CHECK FIRST)
- Use when: Customer uploads documents OR mentions specific documents
- CRITICAL: If you see "UPLOADED DOCUMENTS:" or "**UPLOADED DOCUMENTS:**" anywhere in content, route here
- CRITICAL: If user mentions uploading, attaching, or submitting files, route here
- Documents include: paystubs, W2s, bank statements, tax returns, ID, drivers license, etc.
- Keywords: "upload", "attach", "submit documents", "process documents", "verify documents"

**underwriting_agent**: Credit analysis, approval decisions, underwriting (CHECK SECOND - HIGH PRIORITY)
- Use when: Credit-related questions, approval status, lending decisions, underwriting analysis
- CRITICAL: If user says "underwriting decision", "make decision", "approve application", "underwriting", route here
- CRITICAL: If user asks for credit check, credit score verification, identity verification, route here
- Keywords: "underwriting", "underwriting decision", "make decision", "approve", "approval", "deny", "denial", "credit check", "credit score", "verify identity", "lending decision"
- Examples: "make underwriting decision for APP_123", "run underwriting", "approve this loan", "check credit"

**mortgage_advisor_agent**: General guidance, loan options, rates, eligibility
- Use when: Customer asks questions about loan types, rates, qualification
- Keywords: "options", "rates", "qualify", "first-time buyer", "programs"

**application_agent**: Formal application submission AND data collection
- Use when: Customer wants to start/complete formal application OR is providing application data
- Keywords: "apply", "application", "submit", "URLA", "form", names, addresses, income, employment
- IMPORTANT: If user is answering application questions (name, DOB, address, etc.), stay with application_agent
- NOTE: If user mentions "underwriting decision" or "approve application", route to underwriting_agent instead

**appraisal_agent**: Property valuation, market analysis
- Use when: Questions about property value, appraisals, market conditions
- Keywords: "value", "appraisal", "market", "worth", "price"

**NOTE**: Business rules questions (loan program requirements, credit requirements, DTI limits) 
should go to application_agent or mortgage_advisor_agent as they now have access to business rules tools.

**REASONING APPROACH:**
1. **FIRST**: Check for document uploads - if ANY document upload indicators, route to document_agent
2. **SECOND**: Check for underwriting requests - if user asks for "underwriting decision", "approve", "credit check", route to underwriting_agent
3. **THIRD**: Check conversation context - if user is responding to an agent's question, continue with that agent  
4. **FOURTH**: Look at the main intent of the customer's request
5. **FIFTH**: Route based on PRIMARY need and conversation flow

REMEMBER: 
- Document uploads are HIGHEST PRIORITY and ALWAYS go to document_agent
- Underwriting decisions are SECOND HIGHEST PRIORITY and ALWAYS go to underwriting_agent"""),
            HumanMessage(content=f"Recent conversation:\n{conversation_context}\n\nCurrent user message: {content}")
        ]
        
        try:
            classification = classifier.invoke(classification_prompt)
            return {"route_decision": classification.agent}
        except Exception:
            # Fallback to mortgage advisor for any classification errors
            return {"route_decision": "mortgage_advisor_agent"}
    
    return router


def route_to_agent(state: MortgageRoutingState) -> Literal["mortgage_advisor_agent", "application_agent", "document_agent", "appraisal_agent", "underwriting_agent"]:
    """Conditional edge function following LangGraph routing pattern"""
    return state["route_decision"]


def create_agent_node(agent_name: str, agent):
    """Create agent execution node"""
    
    async def agent_execution(state: MortgageRoutingState):
        """Execute agent with enhanced message content for document processing"""
        
        messages = state["messages"]
        if not messages:
            return {"messages": [], "current_agent": agent_name}
            
        # For document-related agents, enhance the last user message with file content
        if agent_name == "document_agent" and messages:
            try:
                # Get the last user message
                user_messages = [msg for msg in messages if getattr(msg, 'type', None) == 'human']
                if user_messages:
                    last_user_msg = user_messages[-1]
                    
                    # DEBUG: Log raw message structure
                    print(f"\n🔍 RAW MESSAGE DEBUG:")
                    print(f"Message type: {type(last_user_msg)}")
                    print(f"Message content type: {type(last_user_msg.content)}")
                    if isinstance(last_user_msg.content, list):
                        print(f"Content is list with {len(last_user_msg.content)} items")
                        for i, item in enumerate(last_user_msg.content[:3]):  # First 3 items
                            print(f"  Item {i}: {type(item)} - {str(item)[:100]}")
                    else:
                        print(f"Content (first 200 chars): {str(last_user_msg.content)[:200]}")
                    print(f"{'='*60}\n")
                    
                    # Extract full content including files
                    parsed_content = extract_message_content_and_files(last_user_msg)
                    
                    # Log file processing for DocumentAgent
                    if parsed_content.get('has_files'):
                        print(f"🔍 DocumentAgent processing {parsed_content.get('file_count', 0)} uploaded files")
                    
                    # Create enhanced message for agent with all file content visible
                    # CRITICAL: Must be TEXT ONLY since OpenAI doesn't support 'type: file'
                    content_to_send = parsed_content['full_content']
                    
                    # DEBUG: Show what agent will receive
                    print(f"\n{'='*60}")
                    print(f"📋 DOCUMENT AGENT INPUT (length: {len(content_to_send)} chars)")
                    print(f"{'='*60}")
                    print(f"First 500 chars:\n{content_to_send[:500]}")
                    print(f"{'='*60}\n")
                    
                    # Allow larger document content for proper extraction (increased from 2000 to 10000)
                    if len(content_to_send) > 10000:
                        content_to_send = content_to_send[:10000] + "\n\n[Content truncated - document exceeds 10k chars...]"
                        print(f"⚠️ DEBUG: Truncated large content from {len(parsed_content['full_content'])} to {len(content_to_send)} chars")
                    
                    # Create TEXT-ONLY message (OpenAI doesn't support type: 'file')
                    # Replace ALL user messages to ensure no multimodal content reaches OpenAI
                    clean_messages = []
                    for msg in messages[:-1]:
                        if getattr(msg, 'type', None) == 'human':
                            # Convert any user message to text-only
                            msg_content = getattr(msg, 'content', '')
                            if isinstance(msg_content, list):
                                # Extract text from multimodal content
                                text_parts = [item.get('text', '') for item in msg_content if isinstance(item, dict) and item.get('type') == 'text']
                                clean_msg = HumanMessage(content=' '.join(text_parts), id=getattr(msg, 'id', None))
                            else:
                                clean_msg = HumanMessage(content=str(msg_content), id=getattr(msg, 'id', None))
                            clean_messages.append(clean_msg)
                        else:
                            clean_messages.append(msg)
                    
                    # Add the enhanced message with full document content (already text)
                    # Preserve message ID to prevent duplication
                    enhanced_message = HumanMessage(content=content_to_send, id=getattr(last_user_msg, 'id', None))
                    clean_messages.append(enhanced_message)
                    
                    result = await agent.ainvoke({"messages": clean_messages})
                    return {
                        "messages": result["messages"], 
                        "current_agent": agent_name
                    }
                    
            except Exception as e:
                # Fallback: If enhancement fails, clean messages before sending
                # This ensures multimodal content doesn't reach OpenAI
                print(f"⚠️ Document enhancement failed: {e}, falling back to cleaned messages")
                messages = clean_file_entries_from_messages(messages)
        
        # Default execution for other agents
        # Clean file entries from messages for non-document agents
        # DocumentAgent fallback (if enhancement failed) is handled above
        if agent_name != "document_agent":
            messages = clean_file_entries_from_messages(messages)
        # Note: If document_agent enhancement succeeded, clean_messages were already used (returned at line 283)
        
        result = await agent.ainvoke({"messages": messages})
        
        return {
            "messages": result["messages"], 
            "current_agent": agent_name
        }
    
    return agent_execution


def create_mortgage_routing_workflow():
    """
    Create production mortgage routing workflow
    Following LangGraph's official routing pattern
    """
    
    # Initialize all specialist agents
    application_agent = create_application_agent()
    mortgage_advisor_agent = create_mortgage_advisor_agent() 
    document_agent = create_document_agent()
    appraisal_agent = create_appraisal_agent()
    underwriting_agent = create_underwriting_agent()
    
    # Build routing workflow
    workflow = StateGraph(MortgageRoutingState)
    
    # Add routing node (first node - no parsing)
    routing_classifier = create_routing_node()
    workflow.add_node("router", routing_classifier)
    
    # Add specialist agent nodes
    workflow.add_node("mortgage_advisor_agent", create_agent_node("mortgage_advisor_agent", mortgage_advisor_agent))
    workflow.add_node("application_agent", create_agent_node("application_agent", application_agent))
    workflow.add_node("document_agent", create_agent_node("document_agent", document_agent))
    workflow.add_node("appraisal_agent", create_agent_node("appraisal_agent", appraisal_agent))
    workflow.add_node("underwriting_agent", create_agent_node("underwriting_agent", underwriting_agent))
    
    # Entry point: router (no parsing - direct LLM classification)
    workflow.add_edge("__start__", "router")
    
    # Conditional routing based on classification
    workflow.add_conditional_edges(
        "router",
        route_to_agent,
        {
            "mortgage_advisor_agent": "mortgage_advisor_agent",
            "application_agent": "application_agent", 
            "document_agent": "document_agent",
            "appraisal_agent": "appraisal_agent",
            "underwriting_agent": "underwriting_agent"
        }
    )
    
    # All agents go to END after execution (agents have business rules tools built-in)
    workflow.add_edge("application_agent", END)
    workflow.add_edge("document_agent", END)
    workflow.add_edge("underwriting_agent", END)
    workflow.add_edge("appraisal_agent", END)
    workflow.add_edge("mortgage_advisor_agent", END)
    
    return workflow.compile()


def create_mortgage_workflow():
    """
    Create production-grade mortgage workflow
    
    Returns compiled LangGraph workflow implementing intelligent routing
    with LLM-based classification for mortgage specialist selection
    """
    return create_mortgage_routing_workflow()
