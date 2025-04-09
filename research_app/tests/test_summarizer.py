import pytest
from unittest.mock import patch, MagicMock

# Use absolute imports from the research_app package
from research_app.config import AppSettings
from research_app.agents.summarizer import SummarizerAgent
from research_app.agents.schemas import ResearchResult, SummaryResult # Ensure schemas are accessible

# --- Test Fixtures ---

@pytest.fixture
def mock_settings():
    """Provides mock AppSettings for testing."""
    settings = MagicMock(spec=AppSettings)
    settings.llm_api_key = "fake_llm_key"
    settings.llm_model_name = "gpt-test"
    # No search key needed for summarizer
    return settings

@pytest.fixture
def mock_settings_missing_llm_key():
    """Provides mock AppSettings with missing LLM key."""
    settings = MagicMock(spec=AppSettings)
    settings.llm_api_key = None # Missing key
    settings.llm_model_name = "gpt-test"
    return settings

@pytest.fixture
def mock_research_result():
    """Provides a mock ResearchResult object for testing the run method."""
    return ResearchResult(
        query="test query",
        search_results=["Result 1.", "Result 2."],
        raw_content="Result 1.\n\n---\n\nResult 2."
    )

@pytest.fixture
def mock_research_result_empty():
    """Provides a mock ResearchResult object with empty content."""
    return ResearchResult(
        query="empty query",
        search_results=[],
        raw_content=""
    )

@pytest.fixture
def mock_research_result_error():
    """Provides a mock ResearchResult object indicating a previous error."""
    return ResearchResult(
        query="error query",
        search_results=[],
        raw_content="Error during Tavily search: API unavailable"
    )


# --- Test Cases for __init__ ---

# TDD Anchor: test_summarizer_initialization (from summarizer.py)
@patch('research_app.agents.summarizer.ChatOpenAI')
# Removed patch for PydanticAI
def test_summarizer_initialization_success(mock_chat_openai, mock_settings):
    """Tests successful initialization of SummarizerAgent."""
    # Arrange
    mock_llm_instance = MagicMock()
    mock_chat_openai.return_value = mock_llm_instance
    # No PydanticAI instance to mock anymore

    # Act
    agent = SummarizerAgent(settings=mock_settings)

    # Assert
    mock_chat_openai.assert_called_once_with(
        model=mock_settings.llm_model_name,
        api_key=mock_settings.llm_api_key,
        temperature=0.3
    )
    # Check that the agent's llm attribute is the ChatOpenAI instance
    assert agent.llm == mock_llm_instance


def test_summarizer_initialization_missing_key(mock_settings_missing_llm_key):
    """Tests that SummarizerAgent raises ValueError if LLM API key is missing."""
    # Arrange (fixture provides settings with missing key)

    # Act & Assert
    with pytest.raises(ValueError, match="Valid settings object with LLM API key is required"):
        SummarizerAgent(settings=mock_settings_missing_llm_key)


# --- Test Cases for run ---

# TDD Anchor: test_summarizer_run (from summarizer.py)
@patch('research_app.agents.summarizer.ChatOpenAI') # Patch the LLM used in init and run
def test_summarizer_run_success(mock_chat_openai, mock_settings, mock_research_result):
    """Tests the run method successfully returns a SummaryResult."""
    # Arrange
    mock_llm_instance = MagicMock()
    mock_chat_openai.return_value = mock_llm_instance

    # Mock the chain: llm.with_structured_output().invoke()
    mock_structured_llm = MagicMock()
    mock_llm_instance.with_structured_output.return_value = mock_structured_llm

    # Mock the final invoke call return value
    expected_summary = "This is the summarized content."
    mock_llm_response = SummaryResult(summary=expected_summary, original_query=mock_research_result.query)
    mock_structured_llm.invoke.return_value = mock_llm_response

    agent = SummarizerAgent(settings=mock_settings)

    # Act
    result = agent.run(mock_research_result)

    # Assert
    mock_llm_instance.with_structured_output.assert_called_once_with(SummaryResult)
    mock_structured_llm.invoke.assert_called_once()
    # Check that the prompt passed to invoke contains the raw content
    call_args, call_kwargs = mock_structured_llm.invoke.call_args
    prompt_arg = call_args[0] if call_args else call_kwargs.get('prompt', '') # Get the prompt argument
    assert mock_research_result.raw_content in prompt_arg
    assert mock_research_result.query in prompt_arg

    assert isinstance(result, SummaryResult)
    assert result.summary == expected_summary
    assert result.original_query == mock_research_result.query

@patch('research_app.agents.summarizer.ChatOpenAI')
# Removed PydanticAI patch
def test_summarizer_run_empty_input(mock_chat_openai, mock_settings, mock_research_result_empty):
    """Tests run method handles ResearchResult with empty raw_content."""
    # Arrange
    mock_llm_instance = MagicMock()
    mock_chat_openai.return_value = mock_llm_instance
    agent = SummarizerAgent(settings=mock_settings)

    # Act
    result = agent.run(mock_research_result_empty)

    # Assert
    mock_llm_instance.with_structured_output.assert_not_called() # LLM chain should not be called
    assert isinstance(result, SummaryResult)
    assert "No valid content found to summarize" in result.summary
    assert result.original_query == mock_research_result_empty.query

@patch('research_app.agents.summarizer.ChatOpenAI')
# Removed PydanticAI patch
def test_summarizer_run_input_error(mock_chat_openai, mock_settings, mock_research_result_error):
    """Tests run method handles ResearchResult with a previous error message."""
    # Arrange
    mock_llm_instance = MagicMock()
    mock_chat_openai.return_value = mock_llm_instance
    agent = SummarizerAgent(settings=mock_settings)

    # Act
    result = agent.run(mock_research_result_error)

    # Assert
    mock_llm_instance.with_structured_output.assert_not_called() # LLM chain should not be called
    assert isinstance(result, SummaryResult)
    assert "Skipping summary due to previous error" in result.summary
    assert mock_research_result_error.raw_content in result.summary # Ensure original error is included
    assert result.original_query == mock_research_result_error.query


@patch('research_app.agents.summarizer.ChatOpenAI')
# Removed PydanticAI patch
def test_summarizer_run_llm_api_error(mock_chat_openai, mock_settings, mock_research_result):
    """Tests run method handles exceptions during PydanticAI call."""
    # Arrange
    mock_llm_instance = MagicMock()
    mock_chat_openai.return_value = mock_llm_instance

    # Mock the chain: llm.with_structured_output().invoke() to raise an exception
    mock_structured_llm = MagicMock()
    mock_llm_instance.with_structured_output.return_value = mock_structured_llm
    error_message = "LLM unavailable"
    mock_structured_llm.invoke.side_effect = Exception(error_message)

    agent = SummarizerAgent(settings=mock_settings)

    # Act
    result = agent.run(mock_research_result)

    # Assert
    mock_llm_instance.with_structured_output.assert_called_once_with(SummaryResult)
    mock_structured_llm.invoke.assert_called_once() # Ensure invoke was called
    assert isinstance(result, SummaryResult)
    assert f"Error generating summary via LLM: {error_message}" in result.summary # Updated error source
    assert result.original_query == mock_research_result.query