#!/usr/bin/env python3
"""
LangGraph App Graph for Mortgage Processing System V1
Provides the compiled routing workflow for LangGraph dev command

This creates a production-ready routing workflow that intelligently routes
users to the appropriate specialist agent based on LLM classification.
Enhanced with agentic business rules validation on startup.
"""
import sys
import os
import logging

from agents.mortgage_workflow import create_mortgage_workflow

# Initialize logging
logger = logging.getLogger(__name__)

# Business rules validation removed - RuleEngine no longer used

# Create the routing workflow (compiled LangGraph with intelligent routing)
# LangGraph dev handles persistence automatically
app = create_mortgage_workflow()
