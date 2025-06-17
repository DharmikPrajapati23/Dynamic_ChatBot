🤖 AI Chatbot with Web Search
This project implements an intelligent chatbot that can engage in general conversation and, for more complex or factual questions, can perform web searches and scrape information to provide accurate, context-aware answers. The application is built using Streamlit for a simple web interface, integrating with Google's Gemini API for conversational AI and intent classification, and the Google Custom Search API for web search capabilities.

✨ Features
Conversational AI: Handles general chat queries using a lightweight LLM (gemini-1.5-flash).

Intelligent Intent Classification: Determines if a user's question requires a web search or can be answered directly by the LLM (e.g., greetings, simple math, jokes). This is powered by gemini-1.5-flash.

Web Search Integration: Utilizes the Google Custom Search API to find relevant web pages for "hard" or "information-seeking" questions.

Robust Web Scraping: Fetches content from identified web pages, handles access denials (e.g., 403 errors), and truncates content to fit LLM context limits. It also attempts to find content from fallback pages if initial scrapes fail.

Context-Aware Responses: Provides answers synthesized from the scraped web content, ensuring information is current and relevant.

Modular Code Structure: Organized into separate files (app.py, chatbot_logic.py, config.py) for easy management and scalability.

User-Friendly Web Interface: Built with Streamlit for an interactive chat experience.

🚀 Getting Started
Follow these steps to set up and run the chatbot on your local machine.

Prerequisites
Before you begin, ensure you have the following:

Python 3.9+ installed.

pip (Python package installer).

A Google Cloud Project with:

Gemini API enabled.

Google Custom Search API enabled.

A Google Custom Search Engine (CX ID) configured to search the entire web or specific sites.

A Hugging Face Account (Optional): If you later decide to integrate a local LLM, you'll need a Hugging Face token for model downloads. For this project's current setup, the "hard question" model defaults to gemini-1.5-flash for ease of use and free-tier compatibility, but the architecture allows for a switch.

1. Clone the Repository (Conceptual)
Assuming your project files are in a directory named my_chatbot_app:

# If you have a Git repository
git clone <your-repo-url>
cd my_chatbot_app

# If you downloaded files directly
# cd my_chatbot_app

2. Create a Virtual Environment
It's highly recommended to use a virtual environment to manage project dependencies.

python -m venv venv
# On Windows
.\venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

3. Install Dependencies
Navigate to your project directory and install the required libraries:

pip install -r requirements.txt

Your requirements.txt should contain:

streamlit
google-generativeai
requests
beautifulsoup4
python-dotenv
transformers

4. Configure Environment Variables
Create a file named .env in the root of your my_chatbot_app directory (the same level as app.py).

GEMINI_API_KEY='YOUR_GEMINI_API_KEY'
GOOGLE_SEARCH_API_KEY='YOUR_GOOGLE_SEARCH_API_KEY'
GOOGLE_SEARCH_CX='YOUR_GOOGLE_SEARCH_CX'
HF_TOKEN='YOUR_HUGGING_FACE_TOKEN' # Optional: Only needed if you activate a Hugging Face model

Replace the placeholder values with your actual API keys and CX ID. The python-dotenv library (included in requirements.txt) will automatically load these variables when your app runs locally.

Important for Deployment (e.g., Streamlit Community Cloud): Do NOT commit your .env file to public repositories. For deployment platforms, you will typically configure these as "Secrets" or environment variables directly within the platform's settings.

5. Run the Chatbot
Once the setup is complete, run the Streamlit application:

streamlit run app.py

This command will open a new tab in your web browser with the chatbot interface.

👩‍💻 Usage
Simply type your questions into the chat input box at the bottom of the page and press Enter.

General Questions (e.g., "Hi", "How are you?", "2+2"): The chatbot will respond conversationally using gemini-1.5-flash.

Complex/Factual Questions (e.g., "What is machine learning?", "Tell me about quantum computing"): The chatbot will:

Perform a Google search.

Scrape content from the top 3 (or more, if some are blocked) relevant web pages.

Synthesize an answer using gemini-1.5-flash based only on the scraped content.

Display the source URLs from which it gathered information.

📁 Project Structure Explained
app.py:

The main Streamlit application file.

Sets up the Streamlit page configuration, title, and chat interface.

Manages chat history and displays messages.

Calls functions from chatbot_logic.py to handle user input and generate responses.

Responsible for loading the Hugging Face model (if enabled) using @st.cache_resource to ensure it's loaded only once.

chatbot_logic.py:

Contains the core logic of the chatbot.

classify_intent(): Uses gemini-1.5-flash to classify user queries as "normal chat" or "information-seeking."

get_google_search_results(): Interacts with the Google Custom Search API.

scrape_webpage_content(): Handles web scraping with error handling, random delays, and content truncation.

get_llm_response(): Manages calls to the appropriate LLM (gemini-1.5-flash for both normal and hard questions in the current configuration).

config.py:

Stores global configuration variables and constants (e.g., API key environment variable names, content limits, number of search results).

requirements.txt:

Lists all Python package dependencies.

.env:

(Local only) Stores environment variables for API keys.

💡 Troubleshooting & Common Issues
Quota Exceeded (429 Error): This typically means you've hit the rate limits for the free tier of the Gemini API.

Solution: Wait for your quota to reset (daily or per minute), or consider enabling billing on your Google Cloud Project for higher limits. The current setup uses gemini-1.5-flash which has more generous free-tier limits.

API Key/CX ID not set: Ensure your .env file is correctly formatted and located, and that you've activated your virtual environment before running streamlit run app.py. Also, double-check that the variable names in .env (e.g., GOOGLE_SEARCH_API_KEY) exactly match those used in config.py and chatbot_logic.py.

Trust Remote Code Error (Hugging Face): If you decide to uncomment and activate the DeepSeek model in app.py and chatbot_logic.py you might encounter this.

Solution: Ensure trust_remote_code=True is passed to the transformers.pipeline() call (as shown in the app.py code). This acknowledges that the model contains custom code.

StreamlitSetPageConfigMustBeFirstCommandError: This means a Streamlit command (like model loading via @st.cache_resource) executed before st.set_page_config().

Solution: Ensure the st.set_page_config() call is the very first Streamlit command in your app.py script. The provided app.py structure addresses this.

Hugging Face Model Download/Memory Issues: The first time a Hugging Face model is loaded, it downloads large files.

Solution: Ensure you have sufficient disk space and RAM (and GPU VRAM if using a GPU). This can take several minutes depending on your internet speed and hardware.
