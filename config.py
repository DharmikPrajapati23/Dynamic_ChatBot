# Environment variable names for API keys
GEMINI_API_KEY_ENV_VAR = "GEMINI_API_KEY"
GOOGLE_SEARCH_API_KEY_ENV_VAR = "GOOGLE_SEARCH_API_KEY"
GOOGLE_SEARCH_CX_ENV_VAR = "GOOGLE_SEARCH_CX"

# Content limits
SCRAPE_CHAR_LIMIT_PER_PAGE = 1500
MAX_TOTAL_CONTEXT_CHARS_FOR_LLM = 5000 # Max total characters sent to LLM for hard questions
MAX_SEARCH_RESULTS_TO_FETCH = 7 # Fetch this many initial search results for fallbacks
NUM_SUCCESSFUL_SCRAPES_NEEDED = 3 # Try to get content from this many pages