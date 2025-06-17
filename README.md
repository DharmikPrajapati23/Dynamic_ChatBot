# 🤖 AI Chatbot with Web Search

This project implements an intelligent chatbot that can engage in general conversation and, for more complex or factual questions, can perform web searches and scrape information to provide accurate, context-aware answers.

The application is built using **Streamlit** for a simple web interface, integrating with **Google's Gemini API** for conversational AI and intent classification, and the **Google Custom Search API** for web search capabilities.

---

## Working of Project

https://github.com/user-attachments/assets/4574cca3-d896-4375-a257-2a2cf30a0838


## ✨ Features

- **Conversational AI**  
  Handles general chat queries using a lightweight LLM (*gemini-1.5-flash*).

- **Intelligent Intent Classification**  
  Determines if a user's question requires a web search or can be answered directly by the LLM (e.g., greetings, simple math, jokes).

- **Web Search Integration**  
  Utilizes the **Google Custom Search API** to find relevant web pages for information-seeking questions.

- **Robust Web Scraping**  
  Scrapes content from web pages, handles access denials (e.g., 403 errors), and falls back to alternate pages if scraping fails.

- **Context-Aware Responses**  
  Synthesizes answers from scraped web content to ensure up-to-date and relevant responses.

- **Modular Code Structure**  
  Organized into `app.py`, `chatbot_logic.py`, and `config.py` for easy scalability.

- **User-Friendly Web Interface**  
  Built with **Streamlit** for interactive chat experience.

---

## 🚀 Getting Started

Follow these steps to set up and run the chatbot on your local machine.

### 🔧 Prerequisites

Ensure the following are installed or configured:

- Python 3.9+
- pip
- Google Cloud Project with:
  - Gemini API enabled
  - Google Custom Search API enabled
  - Custom Search Engine (CX ID)
- Hugging Face account *(Optional)*

---

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd my_chatbot_app
```

> Or manually download and extract the files, then:
```bash
cd my_chatbot_app
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```
GEMINI_API_KEY='YOUR_GEMINI_API_KEY'
GOOGLE_SEARCH_API_KEY='YOUR_GOOGLE_SEARCH_API_KEY'
GOOGLE_SEARCH_CX='YOUR_GOOGLE_SEARCH_CX'
```

### 5. Run the Chatbot

```bash
streamlit run app.py
```

---

## 👩‍💻 Usage

Type your query in the chat input box and press **Enter**:

- **General Questions** (e.g., "Hi", "2+2")  
  → Handled by `gemini-1.5-flash`.

- **Factual Questions** (e.g., "What is AI?")  
  → Triggers:
  - Google Search via Custom Search API
  - Scraping of top search results
  - Synthesis using Gemini LLM
  - Source URLs are shown for transparency

---

## 📌 Notes

- The chatbot currently uses **Gemini's free-tier API (gemini-1.5-flash)** which is optimized for performance and affordability.
- The architecture supports **future upgrades** to local LLMs or Hugging Face-hosted models if needed.

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

## 🙌 Acknowledgements

- [Google Generative AI](https://ai.google/discover/gemini/)
- [Google Custom Search API](https://programmablesearchengine.google.com/)
- [Streamlit](https://streamlit.io/)
