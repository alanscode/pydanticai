# Research & Summary Application Documentation

## 1. Overview

This application automates the process of researching a given topic (query) using online search tools and generating a concise summary using a Large Language Model (LLM). It leverages the `langchain` and `langgraph` libraries to create a robust workflow (graph) that orchestrates the research and summarization steps.

## 2. Features

*   Accepts a user query as input.
*   Uses a configured search tool (e.g., Tavily) to find relevant information.
*   Utilizes a configured LLM (e.g., OpenAI's GPT models) to process search results and generate a summary.
*   Handles configuration via environment variables.
*   Provides error handling and status messages during execution.

## 3. Architecture & Workflow

The application follows a defined sequence of steps orchestrated by a `langgraph` graph:


**Workflow Steps:**

1.  **Load Settings:** Reads API keys and model configurations from environment variables (`.env` file) via `config.py`.
2.  **Build Graph:** Constructs the `langgraph` execution graph defined in `graph/builder.py`. This graph defines the agents and their connections.
3.  **Invoke Graph:** Executes the graph with the user's query as input (`main.py`). The graph manages calls to search agents and summarization agents.
4.  **Process Final State:** Examines the output state of the graph.
5.  **Display Result:** Prints the generated summary or any error messages encountered during the process.

## 4. Setup & Configuration

### Prerequisites

*   Python 3.10+
*   `pip` (Python package installer)

### Installation

1.  **Clone the repository (if applicable).**
2.  **Navigate to the `research_app` directory.**
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Environment Variables

1.  **Copy the example environment file:**
    ```bash
    cp .env.example .env
    ```
2.  **Edit the `.env` file:**
    *   Replace `"YOUR_LLM_API_KEY_HERE"` with your actual API key for the chosen Language Model (e.g., OpenAI).
    *   Replace `"YOUR_SEARCH_API_KEY_HERE"` with your actual API key for the chosen Search Tool (e.g., Tavily).
    *   (Optional) Uncomment and set `LLM_MODEL_NAME` if you want to use a model other than the default (`gpt-3.5-turbo`).

    **Example `.env`:**
    ```dotenv
    # Environment variables for the Research & Summary Application

    # --- Language Model Configuration ---
    LLM_API_KEY="sk-..." # Your actual OpenAI key

    # Optional: Specify the model name
    # LLM_MODEL_NAME="gpt-4-turbo-preview"

    # --- Search Tool Configuration ---
    SEARCH_API_KEY="tvly-..." # Your actual Tavily key

    # --- Optional Configuration ---
    # EXAMPLE_SETTING="example_value"
    ```
    **Note:** Never commit your actual `.env` file with secret keys to version control.

## 5. Usage

Run the application from the parent directory of `research_app` using the Python module execution flag (`-m`):

```bash
# Use a default query
python -m research_app.main

# Provide your own query
python -m research_app.main "What are the latest advancements in quantum computing?"
```

The application will print status updates and the final summary (or errors) to the console.

## 6. Code Structure

*   **`research_app/`**: Main application package.
    *   **`main.py`**: Entry point of the application. Orchestrates loading settings, building the graph, and running the query.
    *   **`config.py`**: Handles loading and validation of application settings from environment variables.
    *   **`requirements.txt`**: Lists Python dependencies.
    *   **`.env.example`**: Template for the required environment variables.
    *   **`agents/`**: Contains the core logic for different agents (e.g., `researcher.py`, `summarizer.py`) used as nodes in the graph.
        *   `schemas.py`: Defines data structures (using Pydantic) for agent inputs/outputs.
    *   **`graph/`**: Defines the `langgraph` structure.
        *   `builder.py`: Contains the function to construct and connect the graph nodes (agents).
        *   `state.py`: Defines the shared state object passed between graph nodes.
    *   **`tests/`**: Contains unit and integration tests for the application components.