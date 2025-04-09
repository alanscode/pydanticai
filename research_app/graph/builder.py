from langgraph.graph import StateGraph, END
from typing import Dict, Any
from functools import partial

# Import the state definition and agent classes
from .state import AgentState
from ..agents.researcher import ResearcherAgent
from ..agents.summarizer import SummarizerAgent
from ..config import AppSettings # For type hinting

# --- Node Functions (Modified to accept agent instances) ---

# --- TDD Anchor: test_research_node ---
# Test Case: Input state with query, mock researcher_agent.run, verify state update with research_info.
# Test Case: Handle exceptions from researcher_agent.run, verify state update with error_message.
# Test Case: Test with missing 'query' in input state.
# --- End TDD Anchor ---
def execute_research(state: AgentState, researcher: ResearcherAgent) -> Dict[str, Any]:
    """Node that executes the researcher agent."""
    print("--- Graph Node: execute_research ---")
    query = state.get("query")
    if not query:
        print("ERROR: No query found in state for research.")
        return {"error_message": "Input Error: Query not provided."}

    try:
        print(f"Calling Researcher Agent for query: '{query}'")
        research_result = researcher.run(query)
        print("Researcher Agent finished.")
        # Check if the agent itself caught an error during its run
        if research_result and research_result.raw_content and "Error during" in research_result.raw_content:
             error_msg = f"Research failed internally: {research_result.raw_content}"
             print(f"ERROR: {error_msg}")
             # Pass partial result + error message to state
             return {"research_info": research_result, "error_message": error_msg}
        else:
             # Clear any previous error if successful
             return {"research_info": research_result, "error_message": None}
    except Exception as e:
        error_msg = f"Research node execution failed: {e}"
        print(f"ERROR: {error_msg}")
        # Return state indicating error, potentially without research_info
        return {"research_info": None, "error_message": error_msg}

# --- TDD Anchor: test_summarize_node ---
# Test Case: Input state with research_info, mock summarizer_agent.run, verify state update with final_summary.
# Test Case: Input state with error_message from previous step, verify node skips or handles error.
# Test Case: Input state with None research_info, verify handling.
# Test Case: Handle exceptions from summarizer_agent.run, verify state update with error_message.
# --- End TDD Anchor ---
def execute_summary(state: AgentState, summarizer: SummarizerAgent) -> Dict[str, Any]:
    """Node that executes the summarizer agent."""
    print("--- Graph Node: execute_summary ---")

    # Check if a critical error occurred in the previous step
    if state.get("error_message"):
        print(f"Skipping summary due to previous error: {state['error_message']}")
        # Don't overwrite existing error, just pass through state
        return {}

    research_info = state.get('research_info')
    if not research_info:
         error_msg = "Summarization failed: No research info provided to summarizer node."
         print(f"ERROR: {error_msg}")
         return {"final_summary": None, "error_message": error_msg}

    try:
        print(f"Calling Summarizer Agent for query: '{research_info.query}'")
        summary_result = summarizer.run(research_info)
        print("Summarizer Agent finished.")
        # Check if the agent itself caught an error (e.g., PydanticAI failure)
        if summary_result and "Error generating summary" in summary_result.summary:
             error_msg = f"Summarization failed internally: {summary_result.summary}"
             print(f"ERROR: {error_msg}")
             # Pass partial result + error message
             return {"final_summary": summary_result, "error_message": error_msg}
        else:
             # Clear any previous error if successful
             return {"final_summary": summary_result, "error_message": None}
    except Exception as e:
        error_msg = f"Summary node execution failed: {e}"
        print(f"ERROR: {error_msg}")
        return {"final_summary": None, "error_message": error_msg}


# --- Graph Definition ---

# --- TDD Anchor: test_graph_build_and_flow ---
# Test Case: Build the graph, ensure nodes and edges exist.
# Test Case: Run a simple query through the compiled graph, mock agent calls, verify final state.
# Test Case: Simulate an error in the research node, verify the graph terminates or handles error state correctly.
# Test Case: Simulate an error in the summary node, verify the graph terminates or handles error state correctly.
# Test Case: Test graph build failure if agent instantiation fails.
# --- End TDD Anchor ---
def build_graph(settings: AppSettings):
    """
    Builds and compiles the LangGraph.
    Instantiates agents internally based on provided settings.
    """
    if not settings:
        print("ERROR: Cannot build graph, settings object is missing.")
        return None

    try:
        # Instantiate agents *inside* the builder, ensuring settings are valid first
        researcher = ResearcherAgent(settings)
        summarizer = SummarizerAgent(settings)
        print("Agents instantiated successfully for graph building.")
    except ValueError as e:
        print(f"ERROR: Failed to instantiate agents during graph build: {e}")
        print("Please ensure LLM_API_KEY and SEARCH_API_KEY are set in your .env file.")
        return None
    except Exception as e: # Catch other potential init errors
        print(f"ERROR: An unexpected error occurred during agent instantiation: {e}")
        return None


    print("Building LangGraph workflow...")
    workflow = StateGraph(AgentState)

    # Use partial to bind the instantiated agent to its corresponding node function
    research_node = partial(execute_research, researcher=researcher)
    summary_node = partial(execute_summary, summarizer=summarizer)

    # Add nodes
    workflow.add_node("researcher", research_node)
    workflow.add_node("summarizer", summary_node)
    print("Nodes added to graph.")

    # Define edges (Sequential Flow)
    workflow.set_entry_point("researcher")
    print("Entry point set to 'researcher'.")

    workflow.add_edge("researcher", "summarizer")
    print("Edge added: researcher -> summarizer")

    workflow.add_edge("summarizer", END) # End after summarizer
    print("Edge added: summarizer -> END")

    # Compile the graph
    try:
        app_graph = workflow.compile()
        print("Graph compiled successfully.")
        return app_graph
    except Exception as e:
        print(f"ERROR: Failed to compile graph: {e}")
        return None

# Note: Graph instantiation is removed from here.
# It should happen in the main application entry point (main.py)
# after loading settings, like: research_graph = build_graph(app_settings)