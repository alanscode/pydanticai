# Pseudocode for research_app/graph/state.py

from typing import TypedDict, Optional, Dict, Any
# Import the actual schemas when implemented
from ..agents.schemas import ResearchResult, SummaryResult

# --- TDD Anchor: test_graph_state_definition ---
# Test Case: Ensure AgentState structure is correct (keys and types).
# Test Case: Check default values or optional fields in the state.
# --- End TDD Anchor ---

# Using TypedDict for state definition provides type hints
# LangGraph often uses standard dictionaries, but TypedDict helps development
class AgentState(TypedDict, total=False):
    """
    Represents the state passed between nodes in the LangGraph.
    `total=False` means keys are not required to be present.
    """
    # Input
    query: str

    # Intermediate results
    research_info: Optional[ResearchResult] # Output of researcher
    # You could add more intermediate steps here if needed

    # Final output
    final_summary: Optional[SummaryResult] # Output of summarizer

    # Error tracking
    error_message: Optional[str] # To capture errors during flow

    # Optional: Could add configuration or other shared resources if needed
    # config: Optional[Dict[str, Any]]