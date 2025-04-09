import pytest
from unittest.mock import patch, MagicMock

# Assuming AppSettings is importable and has the necessary attributes
# Use absolute imports from the research_app package
from research_app.config import AppSettings
from research_app.agents.researcher import ResearcherAgent
from research_app.agents.schemas import ResearchResult # Ensure ResearchResult is accessible

# --- Test Fixtures ---

@pytest.fixture
def mock_settings():
    """Provides mock AppSettings for testing."""
    settings = MagicMock(spec=AppSettings)
    settings.llm_api_key = "fake_llm_key"
    settings.search_api_key = "fake_search_key"
    settings.llm_model_name = "gpt-test"
    return settings

@pytest.fixture
def mock_settings_missing_keys():
    """Provides mock AppSettings with missing keys."""
    settings = MagicMock(spec=AppSettings)
    settings.llm_api_key = None # Missing key
    settings.search_api_key = "fake_search_key"
    settings.llm_model_name = "gpt-test"
    return settings

# --- Test Cases for __init__ ---

# TDD Anchor: test_researcher_initialization (from researcher.py)
@patch('research_app.agents.researcher.ChatOpenAI')
@patch('research_app.agents.researcher.TavilyClient')
def test_researcher_initialization_success(mock_tavily_client, mock_chat_openai, mock_settings):
    """Tests successful initialization of ResearcherAgent."""
    # Arrange
    mock_llm_instance = MagicMock()
    mock_chat_openai.return_value = mock_llm_instance
    mock_search_instance = MagicMock()
    mock_tavily_client.return_value = mock_search_instance

    # Act
    agent = ResearcherAgent(settings=mock_settings)

    # Assert
    mock_chat_openai.assert_called_once_with(
        model=mock_settings.llm_model_name,
        api_key=mock_settings.llm_api_key,
        temperature=0.1
    )
    mock_tavily_client.assert_called_once_with(api_key=mock_settings.search_api_key)
    assert isinstance(agent.search_tool, MagicMock)
    # assert isinstance(agent.llm, PydanticAI) # LLM initialization is commented out in researcher.py currently
    assert agent.search_tool == mock_search_instance


def test_researcher_initialization_missing_keys(mock_settings_missing_keys):
    """Tests that ResearcherAgent raises ValueError if API keys are missing."""
    # Arrange (mock_settings_missing_keys fixture)

    # Act & Assert
    with pytest.raises(ValueError, match="Valid settings object with LLM and Search API keys is required"):
        ResearcherAgent(settings=mock_settings_missing_keys)

# --- Test Cases for run ---

# TDD Anchor: test_researcher_run (from researcher.py)
@patch('research_app.agents.researcher.ChatOpenAI') # Still need to patch dependencies for init
@patch('research_app.agents.researcher.TavilyClient')
def test_researcher_run_success(mock_tavily_client, mock_chat_openai, mock_settings):
    """Tests the run method successfully returns ResearchResult with data."""
    # Arrange
    mock_search_instance = MagicMock()
    mock_tavily_client.return_value = mock_search_instance
    # Mock the return value of the search method
    mock_search_results = {
        'results': [
            {'content': 'Result 1 content.'},
            {'content': 'Result 2 content.'}
        ]
    }
    mock_search_instance.search.return_value = mock_search_results

    agent = ResearcherAgent(settings=mock_settings)
    query = "test query"

    # Act
    result = agent.run(query)

    # Assert
    mock_search_instance.search.assert_called_once_with(query=query, search_depth="basic", max_results=5)
    assert isinstance(result, ResearchResult)
    assert result.query == query
    assert len(result.search_results) == 2
    assert result.search_results[0] == 'Result 1 content.'
    assert result.search_results[1] == 'Result 2 content.'
    assert 'Result 1 content.' in result.raw_content
    assert 'Result 2 content.' in result.raw_content
    assert "---\n\n" in result.raw_content # Check separator

@patch('research_app.agents.researcher.ChatOpenAI')
@patch('research_app.agents.researcher.TavilyClient')
def test_researcher_run_no_results(mock_tavily_client, mock_chat_openai, mock_settings):
    """Tests the run method handles no search results gracefully."""
    # Arrange
    mock_search_instance = MagicMock()
    mock_tavily_client.return_value = mock_search_instance
    # Mock the return value of the search method to be empty
    mock_search_instance.search.return_value = {'results': []} # Empty results

    agent = ResearcherAgent(settings=mock_settings)
    query = "another query"

    # Act
    result = agent.run(query)

    # Assert
    mock_search_instance.search.assert_called_once_with(query=query, search_depth="basic", max_results=5)
    assert isinstance(result, ResearchResult)
    assert result.query == query
    assert len(result.search_results) == 0
    assert result.raw_content == "" # Expect empty raw content when no results

@patch('research_app.agents.researcher.ChatOpenAI')
@patch('research_app.agents.researcher.TavilyClient')
def test_researcher_run_api_error(mock_tavily_client, mock_chat_openai, mock_settings):
    """Tests the run method handles exceptions during search."""
    # Arrange
    mock_search_instance = MagicMock()
    mock_tavily_client.return_value = mock_search_instance
    # Mock the search method to raise an exception
    error_message = "Tavily API unavailable"
    mock_search_instance.search.side_effect = Exception(error_message)

    agent = ResearcherAgent(settings=mock_settings)
    query = "error query"

    # Act
    result = agent.run(query)

    # Assert
    mock_search_instance.search.assert_called_once_with(query=query, search_depth="basic", max_results=5)
    assert isinstance(result, ResearchResult)
    assert result.query == query
    assert len(result.search_results) == 0
    assert f"Error during Tavily search: {error_message}" in result.raw_content