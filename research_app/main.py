import sys
import pprint # For pretty printing the final state

# Import necessary components
from .config import app_settings # Load settings first
from .graph.builder import build_graph # Import the builder function
from .graph.state import AgentState # For type hinting if needed
from .agents.schemas import SummaryResult # For type hinting

# --- TDD Anchor: test_main_execution ---
# Test Case: Provide a query, mock graph.invoke, verify expected output format (summary string or None).
# Test Case: Simulate graph error during invoke, verify error handling in main.
# Test Case: Test with command-line arguments.
# Test Case: Test scenario where graph building fails (due to missing settings or build error).
# --- End TDD Anchor ---

def run_application(query: str):
    """
    Loads configuration, builds the graph, and runs the research/summary application.

    Args:
        query: The research topic query string.

    Returns:
        The generated summary string, or None if an error occurred.
    """
    print(f"\n=== Starting Application Run ===")
    print(f"Query: '{query}'")

    # 1. Check if settings loaded successfully
    if not app_settings:
        print("CRITICAL ERROR: Application settings failed to load. Check .env file and config.py.")
        print("Please ensure LLM_API_KEY and SEARCH_API_KEY are set.")
        return None

    # 2. Build the graph using the loaded settings
    print("Attempting to build the research graph...")
    research_graph = build_graph(app_settings)

    if not research_graph:
        print("CRITICAL ERROR: Application graph could not be built. Check logs from build_graph.")
        return None
    print("Research graph built successfully.")

    # 3. Prepare initial state and invoke the graph
    initial_input = {"query": query}
    final_state: AgentState | None = None # Initialize final_state

    try:
        print("Invoking the research graph...")
        # The structure of the final state depends on LangGraph version/implementation
        # It usually contains all accumulated state values.
        final_state = research_graph.invoke(initial_input)
        print("Graph invocation complete.")

    except Exception as e:
        print(f"CRITICAL ERROR: An unexpected error occurred during graph execution: {e}")
        # Handle critical errors during the graph invocation itself
        return None # Indicate failure
    finally:
        print("\n--- Final Graph State ---")
        if final_state:
             pprint.pprint(final_state) # Pretty print the dictionary state
        else:
             print("Graph did not return a final state (likely due to critical error during invoke).")
        print("------------------------")


    # 4. Process the final state
    print("\n--- Application Result ---")
    if final_state:
        error_message = final_state.get("error_message")
        final_summary_obj: SummaryResult | None = final_state.get("final_summary") # Type hint

        if error_message:
            print(f"An error occurred during the workflow: {error_message}")
            # Optionally, check if a partial summary was still generated despite the error
            if final_summary_obj and isinstance(final_summary_obj, SummaryResult):
                 print(f"Partial Summary (despite error): {final_summary_obj.summary}")
                 # Decide whether to return partial summary or None based on requirements
            return None # Indicate failure due to error
        elif final_summary_obj and isinstance(final_summary_obj, SummaryResult):
            print(f"Query: {final_summary_obj.original_query}")
            print(f"Summary:\n{final_summary_obj.summary}")
            print("------------------------")
            return final_summary_obj.summary # Return the successful summary
        else:
            print("Application finished, but no valid final summary object was found in the state.")
            print("Check logs and graph logic. Final state keys:", final_state.keys())
            print("------------------------")
            return None # Indicate unexpected state
    else:
        # This case is handled by the finally block's check, but added for robustness
        print("Application did not produce a final state.")
        print("------------------------")
        return None


# --- Example Usage ---
if __name__ == "__main__":
    # Example: Get query from command line arguments or use a default
    if len(sys.argv) > 1:
        user_query = " ".join(sys.argv[1:])
    else:
        # Default query if no arguments are provided
        user_query = "What are the main challenges in deploying large language models?"
        print(f"No query provided via command line, using default: '{user_query}'")

    # Run the application
    summary = run_application(user_query)

    if summary:
        print("\nApplication completed successfully.")
        sys.exit(0) # Exit with success code
    else:
        print("\nApplication finished with errors or no result.")
        sys.exit(1) # Exit with error code