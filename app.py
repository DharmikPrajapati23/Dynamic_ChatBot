import streamlit as st
from chatbot_logic import is_normal_question, get_google_search_results, scrape_webpage_content, get_gemini_response
from config import (
    MAX_TOTAL_CONTEXT_CHARS_FOR_LLM,
    MAX_SEARCH_RESULTS_TO_FETCH,
    NUM_SUCCESSFUL_SCRAPES_NEEDED,
    SCRAPE_CHAR_LIMIT_PER_PAGE
)

# --- Streamlit App Configuration ---
st.set_page_config(page_title="AI Chatbot with Web Search", layout="centered")

st.title("🤖 AI Chatbot with Web Search")

# Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sources" not in st.session_state:
    st.session_state.sources = [] # To store sources for the last hard question

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Display sources if available for the last hard question
if st.session_state.sources:
    st.subheader("Information from these sources:")
    for i, source_url in enumerate(st.session_state.sources):
        st.markdown(f"**{i+1}.** [{source_url}]({source_url})")
    st.markdown("---") # Separator


# Input field for user query
if prompt := st.chat_input("Ask me anything..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Clear previous sources
    st.session_state.sources = []

    # Decide whether to use normal chat or search
    if is_normal_question(prompt):
        with st.spinner("Thinking..."):
            response_content = get_gemini_response('normal_chat', prompt)
        st.session_state.messages.append({"role": "assistant", "content": response_content})
        with st.chat_message("assistant"):
            st.markdown(response_content)
    else:
        # Hard question - initiate web search and scraping
        with st.spinner("That's a deep question! Let me check the internet for you..."):
            all_search_urls = get_google_search_results(prompt, num_results=MAX_SEARCH_RESULTS_TO_FETCH)
            
            scraped_data_with_urls = []
            processed_urls_for_display = []

            # Iterate through all fetched URLs until we get content from needed pages
            for url in all_search_urls:
                if len(scraped_data_with_urls) >= NUM_SUCCESSFUL_SCRAPES_NEEDED:
                    break
                
                with st.spinner(f"Fetching data from: {url}"):
                    content = scrape_webpage_content(url, char_limit=SCRAPE_CHAR_LIMIT_PER_PAGE)
                
                if content:
                    scraped_data_with_urls.append((content, url))
                    processed_urls_for_display.append(url)
                else:
                    st.warning(f"Could not retrieve content from: {url}. Trying next available source if any.")

            if processed_urls_for_display:
                st.session_state.sources = processed_urls_for_display # Store sources for display
                
                combined_context = "\n\n".join([item[0] for item in scraped_data_with_urls])
                
                if len(combined_context) > MAX_TOTAL_CONTEXT_CHARS_FOR_LLM:
                    st.info(f"Context too large, truncating from {len(combined_context)} to {MAX_TOTAL_CONTEXT_CHARS_FOR_LLM} characters.")
                    combined_context = combined_context[:MAX_TOTAL_CONTEXT_CHARS_FOR_LLM]
                
                with st.spinner("Generating answer based on search results..."):
                    response_content = get_gemini_response('hard_question', prompt, combined_context)
                
                st.session_state.messages.append({"role": "assistant", "content": response_content})
                with st.chat_message("assistant"):
                    st.markdown(response_content)
                
                # Rerun to display new sources section
                st.rerun() 
            else:
                # Fallback if no data was successfully scraped
                st.warning("I couldn't find enough relevant information online for that question.")
                with st.spinner("Attempting to provide a general answer..."):
                    response_content = get_gemini_response('hard_question', prompt) # Use hard_question model even for fallback
                st.session_state.messages.append({"role": "assistant", "content": response_content})
                with st.chat_message("assistant"):
                    st.markdown(response_content)






































#-------------------------------------------------TESTING----------------------------------------------------------

# import streamlit as st
# # Import the new get_llm_response function
# from chatbot_logic import is_normal_question, get_google_search_results, scrape_webpage_content, get_llm_response
# from config import (
#     MAX_TOTAL_CONTEXT_CHARS_FOR_LLM,
#     MAX_SEARCH_RESULTS_TO_FETCH,
#     NUM_SUCCESSFUL_SCRAPES_NEEDED,
#     SCRAPE_CHAR_LIMIT_PER_PAGE
# )

# # --- Streamlit App Configuration ---
# st.set_page_config(page_title="AI Chatbot with Web Search", layout="centered")

# st.title("🤖 AI Chatbot with Web Search")

# # Initialize chat history in session state if it doesn't exist
# if "messages" not in st.session_state:
#     st.session_state.messages = []
# if "sources" not in st.session_state:
#     st.session_state.sources = [] # To store sources for the last hard question

# # Display chat messages from history on app rerun
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# # Display sources if available for the last hard question
# if st.session_state.sources:
#     st.subheader("Information from these sources:")
#     for i, source_url in enumerate(st.session_state.sources):
#         st.markdown(f"**{i+1}.** [{source_url}]({source_url})")
#     st.markdown("---") # Separator


# # Input field for user query
# if prompt := st.chat_input("Ask me anything..."):
#     # Add user message to chat history
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     # Clear previous sources
#     st.session_state.sources = []

#     # Decide whether to use normal chat or search
#     if is_normal_question(prompt):
#         with st.spinner("Thinking..."):
#             # Call the new get_llm_response function for normal chat
#             response_content = get_llm_response('normal_chat', prompt)
#         st.session_state.messages.append({"role": "assistant", "content": response_content})
#         with st.chat_message("assistant"):
#             st.markdown(response_content)
#     else:
#         # Hard question - initiate web search and scraping
#         with st.spinner("That's a deep question! Let me check the internet for you..."):
#             all_search_urls = get_google_search_results(prompt, num_results=MAX_SEARCH_RESULTS_TO_FETCH)
            
#             scraped_data_with_urls = []
#             processed_urls_for_display = []

#             # Iterate through all fetched URLs until we get content from needed pages
#             for url in all_search_urls:
#                 if len(scraped_data_with_urls) >= NUM_SUCCESSFUL_SCRAPES_NEEDED:
#                     break
                
#                 with st.spinner(f"Fetching data from: {url}"):
#                     content = scrape_webpage_content(url, char_limit=SCRAPE_CHAR_LIMIT_PER_PAGE)
                
#                 if content:
#                     scraped_data_with_urls.append((content, url))
#                     processed_urls_for_display.append(url)
#                 else:
#                     st.warning(f"Could not retrieve content from: {url}. Trying next available source if any.")

#             if processed_urls_for_display:
#                 st.session_state.sources = processed_urls_for_display # Store sources for display
                
#                 combined_context = "\n\n".join([item[0] for item in scraped_data_with_urls])
                
#                 if len(combined_context) > MAX_TOTAL_CONTEXT_CHARS_FOR_LLM:
#                     st.info(f"Context too large, truncating from {len(combined_context)} to {MAX_TOTAL_CONTEXT_CHARS_FOR_LLM} characters.")
#                     combined_context = combined_context[:MAX_TOTAL_CONTEXT_CHARS_FOR_LLM]
                
#                 with st.spinner("Generating answer based on search results..."):
#                     # Call the new get_llm_response function for hard questions
#                     response_content = get_llm_response('hard_question', prompt, combined_context)
                
#                 st.session_state.messages.append({"role": "assistant", "content": response_content})
#                 with st.chat_message("assistant"):
#                     st.markdown(response_content)
                
#                 # Rerun to display new sources section
#                 st.rerun() 
#             else:
#                 # Fallback if no data was successfully scraped
#                 st.warning("I couldn't find enough relevant information online for that question.")
#                 with st.spinner("Attempting to provide a general answer..."):
#                     # Call the new get_llm_response function for fallback
#                     response_content = get_llm_response('hard_question', prompt) 
#                 st.session_state.messages.append({"role": "assistant", "content": response_content})
#                 with st.chat_message("assistant"):
#                     st.markdown(response_content)

