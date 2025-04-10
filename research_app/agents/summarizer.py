import os
# Import Google Generative AI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models.chat_models import BaseChatModel # For type hinting

from .schemas import SummaryResult, ResearchResult
from ..config import app_settings, AppSettings # Import app_settings instance and the class for type hinting

# --- TDD Anchor: test_summarizer_initialization ---
# Test Case: Ensure summarizer agent initializes correctly with settings.
# Test Case: Mock LLM dependency.
# Test Case: Test initialization failure if settings are invalid/missing.
# --- End TDD Anchor ---
class SummarizerAgent:
    """Agent responsible for summarizing researched content using PydanticAI."""
    llm: BaseChatModel # Use BaseChatModel for type hinting the LangChain LLM

    def __init__(self, settings: AppSettings):
        """Initializes the Summarizer Agent with necessary configurations."""
        # Updated check for Google API Key
        if not settings or not settings.google_api_key:
             raise ValueError("Valid settings object with Google API key is required for SummarizerAgent initialization.")
        print("Initializing Summarizer Agent...")

        # Initialize the LangChain Google Gemini LLM
        google_llm = ChatGoogleGenerativeAI(
            model=settings.google_llm_model_name, # Use Google model name from settings
            google_api_key=settings.google_api_key, # Use Google API key from settings
            temperature=0.3, # Keep temperature setting
            convert_system_message_to_human=True # Gemini often requires this
        )
        # Store the initialized LangChain LLM directly
        self.llm = google_llm
        print("Summarizer Agent Initialized.")

    # --- TDD Anchor: test_summarizer_run ---
    # Test Case: Input ResearchResult, mock LLM response, verify output (SummaryResult).
    # Test Case: Handle empty input content (ResearchResult.raw_content is empty).
    # Test Case: Handle LLM API errors.
    # Test Case: Ensure summary is based on input content.
    # --- End TDD Anchor ---
    def run(self, research_data: ResearchResult) -> SummaryResult:
        """Generates a summary from the researched content using PydanticAI."""
        print(f"Summarizer Agent: Starting summarization for query: '{research_data.query}'")
        original_query = research_data.query if research_data else "Unknown"

        if not research_data or not research_data.raw_content or "Error during" in research_data.raw_content:
            warning_msg = "No valid content found to summarize."
            if research_data and research_data.raw_content and "Error during" in research_data.raw_content:
                # Include the specific error if it came from the researcher
                warning_msg = f"Skipping summary due to previous error: {research_data.raw_content}"
            print(f"Summarizer Agent: {warning_msg}")
            # Return a valid SummaryResult indicating the issue
            return SummaryResult(summary=warning_msg, original_query=original_query)

        # Construct the prompt for PydanticAI, instructing it to generate a SummaryResult
        prompt = f"""
        Based on the following research content about '{research_data.query}', please generate a concise summary.
        Ensure the output strictly follows the required JSON format for SummaryResult.

        --- RESEARCH CONTENT START ---
        {research_data.raw_content}
        --- RESEARCH CONTENT END ---

        Generate the SummaryResult object now.
        """

        try:
            # Use LangChain's structured output method
            print("Summarizer Agent: Calling LLM with structured output...")
            structured_llm = self.llm.with_structured_output(SummaryResult)
            summary_result: SummaryResult = structured_llm.invoke(prompt)

            print("Summarizer Agent: LLM summarization successful.")
            # Ensure the original query is preserved if the LLM doesn't include it
            # (This might be less necessary now as structured output often handles it)
            if not summary_result.original_query:
                 summary_result.original_query = original_query
            return summary_result

        except Exception as e:
            error_msg = f"Error generating summary via LLM: {e}" # Updated error message source
            print(f"ERROR: Summarizer Agent failed for query '{original_query}': {error_msg}")
            # Return a valid SummaryResult indicating the error
            return SummaryResult(summary=error_msg, original_query=original_query)

# Note: Agent instantiation is removed from here.
# It will be handled by the graph builder or main application logic.