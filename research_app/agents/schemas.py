# Pseudocode for research_app/agents/schemas.py

from pydantic import BaseModel, Field
from typing import List, Optional

# --- TDD Anchor: test_research_schema ---
# Test Case: Validate creation of ResearchResult with valid data.
# Test Case: Check default values or optional fields.
# --- End TDD Anchor ---
class ResearchResult(BaseModel):
    """Schema for the output of the Researcher Agent."""
    query: str = Field(description="The original research query")
    search_results: List[str] = Field(description="List of text snippets or URLs from search")
    raw_content: Optional[str] = Field(default="", description="Combined raw text content from search results")

# --- TDD Anchor: test_summary_schema ---
# Test Case: Validate creation of SummaryResult with valid data.
# --- End TDD Anchor ---
class SummaryResult(BaseModel):
    """Schema for the output of the Summarizer Agent."""
    summary: str = Field(description="The final generated summary")
    original_query: str = Field(description="The query that led to this summary")