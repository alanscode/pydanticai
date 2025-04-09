# Pseudocode for research_app/config.py

import os
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv

# --- TDD Anchor: test_config_loading ---
# Test Case: Ensure environment variables are loaded correctly.
# Test Case: Ensure default values are used if variables are missing (optional).
# Test Case: Ensure validation error if critical variables are missing.
# --- End TDD Anchor ---
class AppSettings(BaseModel):
    """Application settings loaded from environment variables."""
    llm_api_key: str = Field(..., description="API Key for the Language Model")
    search_api_key: str = Field(..., description="API Key for the Search Tool")
    llm_model_name: str = Field(default="gpt-3.5-turbo", description="Name of the LLM model to use")

def load_settings() -> AppSettings:
    """Loads settings from environment variables."""
    load_dotenv() # Load from .env file if present

    try:
        settings = AppSettings(
            llm_api_key=os.getenv("LLM_API_KEY"),
            search_api_key=os.getenv("SEARCH_API_KEY"),
            llm_model_name=os.getenv("LLM_MODEL_NAME", "gpt-3.5-turbo") # Provide default
        )
        print("Configuration loaded successfully.")
        return settings
    except ValidationError as e:
        print(f"ERROR: Missing critical environment variables: {e}")
        # Extract missing fields for a clearer message
        missing_vars = [err['loc'][0] for err in e.errors() if err['type'] == 'value_error.missing']
        if missing_vars:
            print(f"Please set the following environment variables: {', '.join(missing_vars)}")
        raise ValueError(f"Configuration validation failed: {e}") from e

# Instantiate settings once for application use
try:
    app_settings = load_settings()
except ValueError as e:
    print(f"Failed to initialize application settings: {e}")
    # Depending on the application, you might exit here or handle it differently
    app_settings = None # Indicate failure

# --- TDD Anchor: test_settings_instance ---
# Test Case: Ensure app_settings is an instance of AppSettings (if loaded).
# Test Case: Ensure app_settings contains the loaded values (if loaded).
# --- End TDD Anchor ---