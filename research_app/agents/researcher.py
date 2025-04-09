import os
from typing import List
# Removed PydanticAI import as it's not used here
from langchain_openai.chat_models import ChatOpenAI
from tavily import TavilyClient

from .schemas import ResearchResult
from ..config import app_settings, AppSettings # Import app_settings instance and the class for type hinting

# --- TDD Anchor: test_researcher_initialization ---
# Test Case: Ensure researcher agent initializes correctly with settings.
# Test Case: Mock LLM and Search Tool dependencies.
# Test Case: Test initialization failure if settings are invalid/missing.
# --- End TDD Anchor ---
class ResearcherAgent:
    """Agent responsible for performing web searches using Tavily."""
    # llm: PydanticAI # Removed - LLM instance not directly used by researcher currently
    search_tool: TavilyClient

    def __init__(self, settings: AppSettings):
        """Initializes the Researcher Agent with necessary configurations."""
        if not settings or not settings.llm_api_key or not settings.search_api_key:
             raise ValueError("Valid settings object with LLM and Search API keys is required for ResearcherAgent initialization.")
        print("Initializing Researcher Agent...")

        # Initialize the LangChain LLM first
        openai_llm = ChatOpenAI(
            model=settings.llm_model_name,
            api_key=settings.llm_api_key,
            temperature=0.1 # Lower temperature for more factual research/search
        )
        # PydanticAI wraps the LangChain LLM for structured output, but we don't need it for the search step itself.
        # We might use it if we wanted the *researcher* to structure the raw results, but here it just searches.
        # self.llm = PydanticAI(llm=openai_llm) # Removed - LLM instance not directly used by researcher currently

        # Initialize the Search Tool
        self.search_tool = TavilyClient(api_key=settings.search_api_key)
        print("Researcher Agent Initialized.")

    # --- TDD Anchor: test_researcher_run ---
    # Test Case: Input a query, mock search results, verify output structure (ResearchResult).
    # Test Case: Handle empty search results.
    # Test Case: Handle search tool API errors.
    # --- End TDD Anchor ---
    def run(self, query: str) -> ResearchResult:
        """Performs web search based on the query using Tavily."""
        print(f"Researcher Agent: Starting research for query: '{query}'")
        results_list: List[str] = []
        combined_content = ""
        try:
            # Use the Tavily search tool
            # Note: TavilyClient.search returns a dict, typically {'results': [...]}
            # where each item in results has 'title', 'url', 'content', 'score', 'raw_content'
            search_output = self.search_tool.search(query=query, search_depth="basic", max_results=5) # Use basic for speed, can be advanced

            if search_output and 'results' in search_output:
                # Extract content from Tavily results
                results_list = [str(result.get('content', '')) for result in search_output['results'] if result.get('content')]
                combined_content = "\n\n---\n\n".join(results_list) # Use more distinct separator
                print(f"Researcher Agent: Found {len(results_list)} results.")
            else:
                print("Researcher Agent: No results found by Tavily.")

        except Exception as e:
            print(f"ERROR: Researcher Agent failed during Tavily search for '{query}': {e}")
            # Return empty results but include error message in raw_content for visibility
            results_list = []
            combined_content = f"Error during Tavily search: {e}"

        research_data = ResearchResult(
            query=query,
            search_results=results_list, # Store the extracted content snippets
            raw_content=combined_content
        )
        return research_data

# Note: Agent instantiation is removed from here.
# It will be handled by the graph builder or main application logic
# to ensure settings are loaded and valid first.