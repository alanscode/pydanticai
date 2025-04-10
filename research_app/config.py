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
    google_api_key: str = Field(..., description="API Key for the Google Generative AI") # Renamed from llm_api_key
    brave_api_key: str = Field(..., description="API Key for the Brave Search API") # Renamed from search_api_key
    google_llm_model_name: str = Field(default="gemini-pro", description="Name of the Google LLM model to use") # Renamed and updated default

def load_settings() -> AppSettings:
    """Loads settings from environment variables."""
    load_dotenv() # Load from .env file if present

    try:
        settings = AppSettings(
            google_api_key=os.getenv("GOOGLE_API_KEY"), # Updated env var name
            brave_api_key=os.getenv("BRAVE_API_KEY"), # Updated env var name
            google_llm_model_name=os.getenv("GOOGLE_LLM_MODEL_NAME", "gemini-2.5-pro-preview-03-25") # Updated env var name and default
        )
        print("Configuration loaded successfully.")
        return settings
    except ValidationError as e:
        print(f"ERROR: Missing critical environment variables: {e}")
        # Extract missing fields for a clearer message
        # Updated error message to reflect new variable names
        missing_vars = []
        for err in e.errors():
            if err['type'] == 'value_error.missing':
                # Map internal field name back to environment variable name
                field_name = err['loc'][0]
                if field_name == 'google_api_key':
                    missing_vars.append("GOOGLE_API_KEY")
                elif field_name == 'brave_api_key':
                    missing_vars.append("BRAVE_API_KEY") # Updated env var name
                # Add other mappings if needed
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