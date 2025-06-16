import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
import random
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

# Import configurations
from config import (
    GEMINI_API_KEY_ENV_VAR,
    GOOGLE_SEARCH_API_KEY_ENV_VAR,
    GOOGLE_SEARCH_CX_ENV_VAR,
    SCRAPE_CHAR_LIMIT_PER_PAGE,
    MAX_SEARCH_RESULTS_TO_FETCH
)

# Configure Gemini API
try:
    gemini_api_key = os.environ.get(GEMINI_API_KEY_ENV_VAR)
    if not gemini_api_key:
        raise ValueError(f"Environment variable {GEMINI_API_KEY_ENV_VAR} not set.")
    genai.configure(api_key=gemini_api_key)
except ValueError as e:
    print(f"Error configuring Gemini API: {e}")
    print("Please ensure your GEMINI_API_KEY is set correctly in your environment or .env file.")
    # In a real application, you might want to stop execution or show a prominent error in the UI
except Exception as e:
    print(f"An unexpected error occurred during Gemini API configuration: {e}")

# Initialize Gemini models globally
# *** CRITICAL CHANGE HERE: Using gemini-1.5-flash for both models for better free-tier handling ***
normal_chat_model = genai.GenerativeModel('gemini-1.5-flash')
hard_question_model = genai.GenerativeModel('gemini-1.5-flash')
intent_classifier_model = genai.GenerativeModel('gemini-1.5-flash')


def classify_intent(query: str) -> str:
    """
    Classifies the user query as 'NORMAL_CHAT' or 'INFORMATION_SEEKING' using an LLM.
    """
    prompt = f"""
    Analyze the following user query and classify its intent.
    Respond with exactly one word: "NORMAL_CHAT" for greetings, pleasantries, or simple conversational questions, or "INFORMATION_SEEKING" for questions that require factual lookup or detailed explanation.

    Examples:
    User: Hi -> NORMAL_CHAT
    User: How are you? -> NORMAL_CHAT
    User: Tell me a joke -> NORMAL_CHAT
    User: What is data science? -> INFORMATION_SEEKING
    User: Who is the president of France? -> INFORMATION_SEEKING
    User: Explain quantum physics -> INFORMATION_SEEKING
    User: Good morning -> NORMAL_CHAT
    User: what is car -> INFORMATION_SEEKING
    User: tell me something about AI -> INFORMATION_SEEKING
    User: What's the weather like? -> INFORMATION_SEEKING

    User: {query} ->
    """
    try:
        response = intent_classifier_model.generate_content(prompt)
        classification = response.text.strip().upper().replace('.', '')
        
        if classification not in ["NORMAL_CHAT", "INFORMATION_SEEKING"]:
            print(f"DEBUG: Unexpected classification result: '{classification}'. Defaulting to NORMAL_CHAT.")
            return "NORMAL_CHAT"
        return classification
    
    except Exception as e:
        print(f"ERROR: Intent classification failed: {e}. Defaulting to NORMAL_CHAT.")
        return "NORMAL_CHAT"


def is_normal_question(query: str) -> bool:
    """
    Determines if a question is 'normal' based on LLM classification.
    """
    classification = classify_intent(query)
    print(f"DEBUG: Query '{query}' classified as: {classification}")
    return classification == "NORMAL_CHAT"


def get_google_search_results(query: str, num_results: int = MAX_SEARCH_RESULTS_TO_FETCH) -> list[str]:
    """
    Uses Google Custom Search API to get search results (URLs).
    """
    api_key = os.environ.get(GOOGLE_SEARCH_API_KEY_ENV_VAR)
    cx = os.environ.get(GOOGLE_SEARCH_CX_ENV_VAR)

    if not api_key:
        print(f"ERROR: {GOOGLE_SEARCH_API_KEY_ENV_VAR} environment variable is not set. Cannot perform Google Search.")
        return []
    if not cx:
        print(f"ERROR: {GOOGLE_SEARCH_CX_ENV_VAR} environment variable is not set. Cannot perform Google Search.")
        return []

    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cx}&q={query}&num={num_results}"
    
    print(f"DEBUG: Making Google Search API call to: {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        results = response.json()
        print(f"DEBUG: Google Search API raw response keys: {results.keys()}")

        urls = []
        if 'items' in results:
            print(f"DEBUG: Found {len(results['items'])} items in Google Search results.")
            for i, item in enumerate(results['items']):
                if 'link' in item:
                    urls.append(item['link'])
                else:
                    print(f"DEBUG: Item {i} has no 'link' key: {item.keys()}")
        else:
            print("DEBUG: 'items' key not found in Google Search API response.")
            print(f"DEBUG: Full Google Search API response (first 500 chars): {str(results)[:500]}...")

        return urls
    except requests.exceptions.HTTPError as e:
        print(f"ERROR: HTTP Error during Google Search API call: {e}. Status code: {e.response.status_code}. Response body (first 200 chars): {e.response.text[:200]}")
        return []
    except requests.exceptions.ConnectionError as e:
        print(f"ERROR: Connection Error during Google Search API call: {e}")
        return []
    except requests.exceptions.Timeout as e:
        print(f"ERROR: Timeout Error during Google Search API call: {e}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"ERROR: General Request Error during Google Search API call: {e}")
        return []
    except ValueError as e:
        print(f"ERROR: Error decoding JSON from Google Search API: {e}. Raw response (first 200 chars): {response.text[:200]}...")
        return []
    except Exception as e:
        print(f"ERROR: An unexpected error occurred in get_google_search_results: {e}")
        return []


def scrape_webpage_content(url: str, char_limit: int = SCRAPE_CHAR_LIMIT_PER_PAGE) -> str:
    """
    Fetches and scrapes content from a URL, with error handling and truncation.
    """
    print(f"DEBUG: Attempting to scrape: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://www.google.com/'
    }
    
    try:
        delay = random.uniform(1, 3)
        print(f"DEBUG: Waiting for {delay:.2f} seconds before scraping {url}")
        time.sleep(delay)

        response = requests.get(url, timeout=7, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            main_content_tags = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'span', 'div'])
            text_content_parts = []
            for tag in main_content_tags:
                if tag.name == 'div' and ('class' in tag.attrs and any(c in tag['class'] for c in ['content', 'article-body', 'post-content', 'main-content', 'entry-content', 'article'])):
                    text = tag.get_text(separator=' ', strip=True)
                    if text and len(text) > 200: # Prefer larger chunks from common content divs
                        text_content_parts.append(text)
                elif tag.name in ['p', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    text = tag.get_text(separator=' ', strip=True)
                    if text and len(text) > 50:
                        text_content_parts.append(text)
            
            combined_text = ' '.join(text_content_parts)
            
            truncated_content = combined_text[:char_limit]
            print(f"DEBUG: Scraped and truncated to {len(truncated_content)} characters from {url} (original length: {len(combined_text)}).")
            return truncated_content
        else:
            print(f"DEBUG: Skipping {url} due to non-200 status code: {response.status_code}")
            return ""
            
    except requests.exceptions.HTTPError as e:
        print(f"ERROR: HTTP Error during scraping {url}: {e}. Status code: {e.response.status_code}")
        return ""
    except requests.exceptions.ConnectionError as e:
        print(f"ERROR: Connection Error during scraping {url}: {e}")
        return ""
    except requests.exceptions.Timeout as e:
        print(f"ERROR: Timeout Error during scraping {url}: {e}")
        return ""
    except requests.exceptions.RequestException as e:
        print(f"ERROR: General Request Error during scraping {url}: {e}")
        return ""
    except Exception as e:
        print(f"ERROR: An unexpected error occurred while scraping {url}: {e}")
        return ""

def get_gemini_response(model_name: str, prompt: str, context: str = "") -> str:
    """
    Gets a response from the specified Gemini model.
    """
    try:
        if model_name == 'normal_chat':
            model = normal_chat_model
        elif model_name == 'hard_question':
            model = hard_question_model
        else:
            raise ValueError(f"Unknown model name: {model_name}")

        full_prompt_template = ""
        if context:
            # full_prompt_template = """
            #     You are an intelligent assistant. Answer the user's question concisely and accurately based *only* on the provided information.
            #     If the information provided is insufficient to answer the question, state that you cannot provide a precise answer based solely on the given context. Do not invent information.

            #     Provided Information:
            #     ```
            #     {context}
            #     ```

            #     User Question: {prompt}
            #     """
            
            full_prompt_template = """
                You are a highly knowledgeable and concise AI assistant. Your primary goal is to answer the user's question accurately and directly, *solely* using the information provided below.

                **Strict Instructions:**
                1.  **Do NOT use any external knowledge.** Your response must be derived *only* from the "Provided Information."
                2.  **Be Concise:** Get straight to the point.
                3.  **If Insufficient:** If the "Provided Information" does not contain enough detail to answer the question, clearly state: "Based on the provided information, I cannot give a precise answer to that question. The context does not contain sufficient details." Do NOT try to guess or invent information.
                4.  **No Extraneous Text:** Do not add conversational fillers beyond a direct answer or the "Insufficient" statement.

                Provided Information:
                ```
                {context}
                ```

                User Question: {prompt}
                Answer:
                """


            full_prompt = full_prompt_template.format(context=context, prompt=prompt)
        else:
            full_prompt = f"User Question: {prompt}"

        print(f"DEBUG: Sending prompt to Gemini '{model_name}' (first 500 chars): {full_prompt[:500]}...")
        
        response = model.generate_content(full_prompt)
        print(f"DEBUG: Gemini raw response from '{model_name}': {response.text[:200]}...")

        if response.text:
            return response.text
        elif response.candidates and response.candidates[0].finish_reason:
            print(f"DEBUG: Gemini finished with reason: {response.candidates[0].finish_reason}")
            if response.candidates[0].finish_reason == 1: # Safety block
                return "I'm sorry, I cannot answer that question due to safety policies."
        return "I'm sorry, I couldn't generate a response at this time."

    except Exception as e:
        print(f"ERROR: Error generating Gemini response for '{model_name}': {e}")
        return "I'm sorry, I couldn't generate a response at this time due to an internal error."

























































#-------------------------------------------------TESTING----------------------------------------------------------



# import os
# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urlparse
# import time
# import random
# import google.generativeai as genai
# from dotenv import load_dotenv
# from transformers import pipeline # Import the pipeline from transformers
# import streamlit as st

# # Load environment variables from .env file (for local development)
# load_dotenv()

# # Import configurations
# from config import (
#     GEMINI_API_KEY_ENV_VAR,
#     GOOGLE_SEARCH_API_KEY_ENV_VAR,
#     GOOGLE_SEARCH_CX_ENV_VAR,
#     SCRAPE_CHAR_LIMIT_PER_PAGE,
#     MAX_SEARCH_RESULTS_TO_FETCH
# )

# # --- Gemini API Configuration ---
# # Configure Gemini API
# try:
#     gemini_api_key = os.environ.get(GEMINI_API_KEY_ENV_VAR)
#     if not gemini_api_key:
#         # If Gemini key is not set, we can still run if only HF model is used for hard questions.
#         # But for intent classification, we need a fallback or assume it's set.
#         print(f"WARNING: {GEMINI_API_KEY_ENV_VAR} not set. Gemini models might not function.")
#         # We'll still initialize with a dummy key if not present to avoid immediate crash,
#         # but calls to Gemini models will likely fail if the key isn't truly valid.
#         genai.configure(api_key="dummy_key_if_not_set") 
#     else:
#         genai.configure(api_key=gemini_api_key)
# except Exception as e:
#     print(f"An unexpected error occurred during Gemini API configuration: {e}")

# # Initialize Gemini models globally (used for normal chat and intent classification)
# normal_chat_model = genai.GenerativeModel('gemini-1.5-flash')
# intent_classifier_model = genai.GenerativeModel('gemini-1.5-flash')

# # --- Hugging Face Model Configuration ---
# # Get Hugging Face Token
# hf_token = os.environ.get("HF_TOKEN")
# if not hf_token:
#     print("WARNING: HF_TOKEN environment variable is not set. Hugging Face model might not function.")
#     # In a real application, you might want to stop or notify the user
#     # For now, we'll let the pipeline creation potentially fail or proceed without auth.

# # Initialize Hugging Face model globally
# # This part can take a long time the first time it runs as it downloads the model
# hf_hard_question_model = None
# HF_MODEL_NAME = "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct" 

# # Streamlit's @st.cache_resource is ideal for loading models once
# @st.cache_resource
# def load_hf_model():
#     try:
#         print(f"DEBUG: Loading Hugging Face model: {HF_MODEL_NAME}...")
#         # Use device_map="auto" to efficiently use GPU if available, else CPU
#         # auth_token is passed for private models or higher rate limits
#         model = pipeline(
#             "text-generation",
#             model=HF_MODEL_NAME,
#             torch_dtype=None, # Use default or torch.float16 for GPU memory saving
#             device_map="auto",
#             token=hf_token # Pass the HF token here
#         )
#         print("DEBUG: Hugging Face model loaded successfully.")
#         return model
#     except Exception as e:
#         print(f"ERROR: Failed to load Hugging Face model {HF_MODEL_NAME}: {e}")
#         print("Please ensure you have sufficient GPU memory (if using GPU), and a valid HF_TOKEN for private models or rate limits.")
#         return None

# # Load the Hugging Face model when the script starts (cached by Streamlit)
# hf_hard_question_model = load_hf_model()


# # --- Chatbot Logic Functions ---

# def classify_intent(query: str) -> str:
#     """
#     Classifies the user query as 'NORMAL_CHAT' or 'INFORMATION_SEEKING' using an LLM.
#     """
#     # This uses the Gemini model for lightweight classification
#     # If Gemini API key is invalid, this will still attempt to call and might raise an error
#     # You might want to add a check for `gemini_api_key` here.
#     if not os.environ.get(GEMINI_API_KEY_ENV_VAR):
#         print("DEBUG: Gemini API key not available for intent classification. Falling back to rule-based.")
#         # Fallback to a simple rule if Gemini key is not configured for classification
#         normal_keywords = ["hi", "hello", "good morning", "how are you", "what's up", "hey", "tell me a joke", "how are you doing", "what's your name"]
#         query_lower = query.lower()
#         for keyword in normal_keywords:
#             if keyword in query_lower:
#                 return "NORMAL_CHAT"
#         return "INFORMATION_SEEKING"

#     prompt = f"""
#     Analyze the following user query and classify its intent.
#     Respond with exactly one word: "NORMAL_CHAT" for greetings, pleasantries, or simple conversational questions, or "INFORMATION_SEEKING" for questions that require factual lookup or detailed explanation.

#     Examples:
#     User: Hi -> NORMAL_CHAT
#     User: How are you? -> NORMAL_CHAT
#     User: Tell me a joke -> NORMAL_CHAT
#     User: What is data science? -> INFORMATION_SEEKING
#     User: Who is the president of France? -> INFORMATION_SEEKING
#     User: Explain quantum physics -> INFORMATION_SEEKING
#     User: Good morning -> NORMAL_CHAT
#     User: what is car -> INFORMATION_SEEKING
#     User: tell me something about AI -> INFORMATION_SEEKING
#     User: What's the weather like? -> INFORMATION_SEEKING

#     User: {query} ->
#     """
#     try:
#         response = intent_classifier_model.generate_content(prompt)
#         classification = response.text.strip().upper().replace('.', '')
#         if classification not in ["NORMAL_CHAT", "INFORMATION_SEEKING"]:
#             print(f"DEBUG: Unexpected classification result: '{classification}'. Defaulting to INFORMATION_SEEKING.")
#             return "INFORMATION_SEEKING"
#         return classification
#     except Exception as e:
#         print(f"ERROR: Intent classification failed with Gemini: {e}. Defaulting to INFORMATION_SEEKING.")
#         return "INFORMATION_SEEKING"


# def is_normal_question(query: str) -> bool:
#     """
#     Determines if a question is 'normal' based on LLM classification.
#     """
#     classification = classify_intent(query)
#     print(f"DEBUG: Query '{query}' classified as: {classification}")
#     return classification == "NORMAL_CHAT"


# def get_google_search_results(query: str, num_results: int = MAX_SEARCH_RESULTS_TO_FETCH) -> list[str]:
#     """
#     Uses Google Custom Search API to get search results (URLs).
#     """
#     api_key = os.environ.get(GOOGLE_SEARCH_API_KEY_ENV_VAR)
#     cx = os.environ.get(GOOGLE_SEARCH_CX_ENV_VAR)

#     if not api_key:
#         print(f"ERROR: {GOOGLE_SEARCH_API_KEY_ENV_VAR} environment variable is not set. Cannot perform Google Search.")
#         return []
#     if not cx:
#         print(f"ERROR: {GOOGLE_SEARCH_CX_ENV_VAR} environment variable is not set. Cannot perform Google Search.")
#         return []

#     url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cx}&q={query}&num={num_results}"
    
#     print(f"DEBUG: Making Google Search API call to: {url}")
#     try:
#         response = requests.get(url, timeout=10)
#         response.raise_for_status()
#         results = response.json()
#         print(f"DEBUG: Google Search API raw response keys: {results.keys()}")

#         urls = []
#         if 'items' in results:
#             print(f"DEBUG: Found {len(results['items'])} items in Google Search results.")
#             for i, item in enumerate(results['items']):
#                 if 'link' in item:
#                     urls.append(item['link'])
#                 else:
#                     print(f"DEBUG: Item {i} has no 'link' key: {item.keys()}")
#         else:
#             print("DEBUG: 'items' key not found in Google Search API response.")
#             print(f"DEBUG: Full Google Search API response (first 500 chars): {str(results)[:500]}...")

#         return urls
#     except requests.exceptions.HTTPError as e:
#         print(f"ERROR: HTTP Error during Google Search API call: {e}. Status code: {e.response.status_code}. Response body (first 200 chars): {e.response.text[:200]}")
#         return []
#     except requests.exceptions.ConnectionError as e:
#         print(f"ERROR: Connection Error during Google Search API call: {e}")
#         return []
#     except requests.exceptions.Timeout as e:
#         print(f"ERROR: Timeout Error during Google Search API call: {e}")
#         return []
#     except requests.exceptions.RequestException as e:
#         print(f"ERROR: General Request Error during Google Search API call: {e}")
#         return []
#     except ValueError as e:
#         print(f"ERROR: Error decoding JSON from Google Search API: {e}. Raw response (first 200 chars): {response.text[:200]}...")
#         return []
#     except Exception as e:
#         print(f"ERROR: An unexpected error occurred in get_google_search_results: {e}")
#         return []


# def scrape_webpage_content(url: str, char_limit: int = SCRAPE_CHAR_LIMIT_PER_PAGE) -> str:
#     """
#     Fetches and scrapes content from a URL, with error handling and truncation.
#     """
#     print(f"DEBUG: Attempting to scrape: {url}")
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
#         'Accept-Language': 'en-US,en;q=0.5',
#         'Accept-Encoding': 'gzip, deflate, br',
#         'Connection': 'keep-alive',
#         'Referer': 'https://www.google.com/'
#     }
    
#     try:
#         delay = random.uniform(1, 3)
#         print(f"DEBUG: Waiting for {delay:.2f} seconds before scraping {url}")
#         time.sleep(delay)

#         response = requests.get(url, timeout=7, headers=headers)
        
#         if response.status_code == 200:
#             soup = BeautifulSoup(response.text, 'html.parser')

#             main_content_tags = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'span', 'div'])
#             text_content_parts = []
#             for tag in main_content_tags:
#                 if tag.name == 'div' and ('class' in tag.attrs and any(c in tag['class'] for c in ['content', 'article-body', 'post-content', 'main-content', 'entry-content', 'article'])):
#                     text = tag.get_text(separator=' ', strip=True)
#                     if text and len(text) > 200:
#                         text_content_parts.append(text)
#                 elif tag.name in ['p', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
#                     text = tag.get_text(separator=' ', strip=True)
#                     if text and len(text) > 50:
#                         text_content_parts.append(text)
            
#             combined_text = ' '.join(text_content_parts)
            
#             truncated_content = combined_text[:char_limit]
#             print(f"DEBUG: Scraped and truncated to {len(truncated_content)} characters from {url} (original length: {len(combined_text)}).")
#             return truncated_content
#         else:
#             print(f"DEBUG: Skipping {url} due to non-200 status code: {response.status_code}")
#             return ""
            
#     except requests.exceptions.HTTPError as e:
#         print(f"ERROR: HTTP Error during scraping {url}: {e}. Status code: {e.response.status_code}")
#         return ""
#     except requests.exceptions.ConnectionError as e:
#         print(f"ERROR: Connection Error during scraping {url}: {e}")
#         return ""
#     except requests.exceptions.Timeout as e:
#         print(f"ERROR: Timeout Error during scraping {url}: {e}")
#         return ""
#     except requests.exceptions.RequestException as e:
#         print(f"ERROR: General Request Error during scraping {url}: {e}")
#         return ""
#     except Exception as e:
#         print(f"ERROR: An unexpected error occurred while scraping {url}: {e}")
#         return ""


# def get_llm_response(model_type: str, prompt: str, context: str = "") -> str:
#     """
#     Gets a response from the specified LLM (Gemini for normal, Hugging Face for hard questions).
#     """
#     if model_type == 'normal_chat':
#         # Use Gemini for normal chat
#         model = normal_chat_model
#         try:
#             full_prompt = f"User Question: {prompt}"
#             print(f"DEBUG: Sending prompt to Gemini '{model_type}' (first 500 chars): {full_prompt[:500]}...")
#             response = model.generate_content(full_prompt)
#             print(f"DEBUG: Gemini raw response from '{model_type}': {response.text[:200]}...")
#             if response.text:
#                 return response.text
#             elif response.candidates and response.candidates[0].finish_reason:
#                 print(f"DEBUG: Gemini finished with reason: {response.candidates[0].finish_reason}")
#                 if response.candidates[0].finish_reason == 1: # Safety block
#                     return "I'm sorry, I cannot answer that question due to safety policies."
#             return "I'm sorry, I couldn't generate a response at this time."
#         except Exception as e:
#             print(f"ERROR: Error generating Gemini response for '{model_type}': {e}")
#             return "I'm sorry, I couldn't generate a response at this time due to an internal error."

#     elif model_type == 'hard_question':
#         # Use Hugging Face model for hard questions
#         if hf_hard_question_model is None:
#             return "Error: Hugging Face model not loaded. Please check your HF_TOKEN and internet connection."

#         # Construct prompt for the Hugging Face model
#         # DeepSeek Instruct models typically use a chat-like format
#         # Example format: <｜fim begin｜>...<｜file_separator｜>...<｜fim end｜>
#         # However, for text-generation pipeline, a simple instruction format often works.
#         hf_prompt_template = ""
#         if context:
#             hf_prompt_template = f"""
# You are an intelligent assistant. Answer the user's question concisely and accurately based *only* on the provided information.
# If the information provided is insufficient to answer the question, state that you cannot provide a precise answer based solely on the given context. Do not invent information.

# Provided Information:
# ```
# {context}
# ```

# User Question: {prompt}
# Assistant:
# """
#         else:
#             hf_prompt_template = f"User Question: {prompt}\nAssistant:"
        
#         print(f"DEBUG: Sending prompt to Hugging Face model '{HF_MODEL_NAME}' (first 500 chars): {hf_prompt_template[:500]}...")

#         try:
#             # Generate response using the Hugging Face pipeline
#             # max_new_tokens controls the length of the generated response
#             # num_return_sequences=1 ensures only one response
#             # temperature for creativity, do_sample=True for non-deterministic output
#             response = hf_hard_question_model(
#                 hf_prompt_template,
#                 max_new_tokens=500, # Adjust max output tokens as needed
#                 num_return_sequences=1,
#                 do_sample=True,
#                 temperature=0.7,
#                 top_p=0.9,
#                 eos_token_id=hf_hard_question_model.tokenizer.eos_token_id # Stop at end of sequence token
#             )
            
#             # The pipeline returns a list of dictionaries, extract the generated text
#             generated_text = response[0]['generated_text']
            
#             # The generated_text will include the input prompt. We need to strip it.
#             # Find the position of the assistant's response start
#             response_start_marker = "Assistant:"
#             start_index = generated_text.find(response_start_marker)
#             if start_index != -1:
#                 final_response = generated_text[start_index + len(response_start_marker):].strip()
#             else:
#                 final_response = generated_text.strip() # Fallback if marker not found

#             print(f"DEBUG: Hugging Face raw response from '{HF_MODEL_NAME}': {generated_text[:200]}...")
#             return final_response

#         except Exception as e:
#             print(f"ERROR: Error generating Hugging Face response for '{model_type}': {e}")
#             return "I'm sorry, I couldn't generate a response from the Hugging Face model at this time."
#     else:
#         raise ValueError(f"Unknown model type: {model_type}")

