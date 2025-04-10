import os
import requests # Added for making HTTP requests
from typing import List
# Removed PydanticAI import as it's not used here
# Removed TavilyClient import

from .schemas import ResearchResult
from ..config import app_settings, AppSettings # Import app_settings instance and the class for type hinting

# --- TDD Anchor: test_researcher_initialization ---
# Test Case: Ensure researcher agent initializes correctly with settings.
# Test Case: Mock LLM and Search Tool dependencies.
# Test Case: Test initialization failure if settings are invalid/missing.
# --- End TDD Anchor ---
class ResearcherAgent:
    """Agent responsible for performing web searches using the Brave Search API."""
    # No specific search tool client needed, will use requests directly
    brave_api_key: str # Store the API key

    def __init__(self, settings: AppSettings):
        """Initializes the Researcher Agent with necessary configurations."""
        # Updated check for Google and Brave API keys from config
        if not settings or not settings.google_api_key or not settings.brave_api_key:
             raise ValueError("Valid settings object with Google and Brave API keys is required for ResearcherAgent initialization.")
        print("Initializing Researcher Agent (using Brave Search)...")

        # Store the Brave API key from settings
        self.brave_api_key = settings.brave_api_key
        print("Researcher Agent Initialized.")

    # --- TDD Anchor: test_researcher_run ---
    # Test Case: Input a query, mock search results, verify output structure (ResearchResult).
    # Test Case: Handle empty search results.
    # Test Case: Handle search tool API errors.
    # --- End TDD Anchor ---
    def run(self, query: str) -> ResearchResult:
        """Performs web search based on the query using the Brave Search API."""
        print(f"Researcher Agent: Starting research for query: '{query}' using Brave Search")
        results_list: List[str] = []
        combined_content = ""

        search_url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.brave_api_key
        }
        params = {
            "q": query,
            "count": 5 # Number of results to fetch
        }

        try:
            response = requests.get(search_url, headers=headers, params=params, timeout=10)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

            data = response.json()
            search_results = data.get('web', {}).get('results', [])

            if search_results:
                # Extract description/snippet from Brave results
                # Adjust the key if Brave uses a different field name (e.g., 'snippet')
                results_list = [str(result.get('description', '')) for result in search_results if result.get('description')]
                combined_content = "\n\n---\n\n".join(results_list)
                print(f"Researcher Agent: Found {len(results_list)} results via Brave Search.")
            else:
                print("Researcher Agent: No results found by Brave Search.")
                combined_content = f"No search results found for '{query}' via Brave Search."

        except requests.exceptions.RequestException as e:
            error_msg = f"Error during Brave Search API request: {e}"
            print(f"ERROR: Researcher Agent failed for '{query}': {error_msg}")
            combined_content = error_msg
        except Exception as e:
            error_msg = f"An unexpected error occurred during Brave search: {e}"
            print(f"ERROR: Researcher Agent failed for '{query}': {error_msg}")
            combined_content = error_msg

        research_data = ResearchResult(
            query=query,
            search_results=results_list, # Store the extracted content snippets
            raw_content=combined_content
        )
        return research_data

# Note: Agent instantiation is removed from here.
# It will be handled by the graph builder or main application logic
# to ensure settings are loaded and valid first.