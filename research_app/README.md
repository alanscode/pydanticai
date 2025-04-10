# Research & Summary Application Documentation

## 1. Overview

This application automates the process of researching a given topic (query) using online search tools and generating a concise summary using a Large Language Model (LLM). It leverages the `langchain` and `langgraph` libraries to create a robust workflow (graph) that orchestrates the research and summarization steps. Building this app to help me learn the basics of langgraph and pydantic AI frameworks.

## 2. Features

- Accepts a user query as input.
- Uses a configured search tool (e.g., Tavily) to find relevant information.
- Utilizes a configured LLM (e.g., OpenAI's GPT models) to process search results and generate a summary.
- Handles configuration via environment variables.
- Provides error handling and status messages during execution.

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

- Python 3.10+
- Python 3.10+
- `uv` (Python package installer and virtual environment manager - install via `pip install uv` or see [uv documentation](https://github.com/astral-sh/uv))

### Installation

1.  **Clone the repository (if applicable).**
2.  **Navigate to the `research_app` directory.**
3.  **Create a virtual environment using `uv`:**
    ```bash
    uv venv
    ```
4.  **Install dependencies using `uv` (this uses the virtual environment automatically):**
    ```bash
    uv pip install -r requirements.txt
    ```

### Environment Variables

1.  **Copy the example environment file:**
    ```bash
    cp .env.example .env
    ```
2.  **Edit the `.env` file:**

    - Replace `"YOUR_GOOGLE_API_KEY_HERE"` with your actual Google Generative AI API key.
    - Replace `"YOUR_BRAVE_API_KEY_HERE"` with your actual Brave Search API key.
    - (Optional) Set `GOOGLE_LLM_MODEL_NAME` if you want to use a Google model other than the default (`gemini-2.5-pro-preview-03-25`).

    **Example `.env`:**

    ```dotenv
    # Environment variables for the Research & Summary Application

    # --- Google Generative AI Configuration ---
    GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY_HERE"

    # Optional: Specify the Google LLM model name
    # GOOGLE_LLM_MODEL_NAME="gemini-1.5-pro-latest"

    # --- Brave Search Configuration ---
    BRAVE_API_KEY="YOUR_BRAVE_API_KEY_HERE"

    # --- Optional Configuration ---
    # EXAMPLE_SETTING="example_value"
    ```

    **Note:** Never commit your actual `.env` file with secret keys to version control.

## 5. Usage

Run the application from the **parent directory** (`pydanticai/`) using the Python interpreter located inside the virtual environment and the module execution flag (`-m`):

```bash
# On Windows (PowerShell/CMD):
# Use a default query
.\research_app\.venv\Scripts\python.exe -m research_app.main

# Provide your own query
.\research_app\.venv\Scripts\python.exe -m research_app.main "Your query here"

# On macOS/Linux (Bash/Zsh):
# Use a default query
./research_app/.venv/bin/python -m research_app.main

# Provide your own query
./research_app/.venv/bin/python -m research_app.main "Your query here"
```

The application will print status updates and the final summary (or errors) to the console.

## 6. Code Structure

- **`research_app/`**: Main application package.
  - **`main.py`**: Entry point of the application. Orchestrates loading settings, building the graph, and running the query.
  - **`config.py`**: Handles loading and validation of application settings from environment variables.
  - **`requirements.txt`**: Lists Python dependencies.
  - **`.env.example`**: Template for the required environment variables.
  - **`agents/`**: Contains the core logic for different agents (e.g., `researcher.py`, `summarizer.py`) used as nodes in the graph.
    - `schemas.py`: Defines data structures (using Pydantic) for agent inputs/outputs.
  - **`graph/`**: Defines the `langgraph` structure.
    - `builder.py`: Contains the function to construct and connect the graph nodes (agents).
    - `state.py`: Defines the shared state object passed between graph nodes.
  - **`tests/`**: Contains unit and integration tests for the application components.
