# Researcher Agent using Groq & BraveAPI

## 🎯 Overview
This app demonstrates Groq API’s **tool use (function calling)** via a Streamlit UI.  
You ask questions, and the LLM decides whether to call:
- **web_search(query)**  
- **scrape_url(url)**  
to fetch live info or page details.

## 🧾 Setup
1. Clone this repo  
2. Create `.env` with:
GROQ_API_KEY= "api"
SERPER_API_KEY ="api"
FIRECRAWL_API_KEY="api"
3. Install deps:
pip install -r requirements.txt
4. Run:
streamlit run app.py

## 🧠 Conversation Flow

User enters a question → → Groq assistant (tool_choice=auto) decides:
User → Groq Model (system + user + tool definitions)
└─→ Tool call: web_search(query) → tools.py → SerpAPI → returns JSON
├─→ (optional) Tool call: scrape_url(url) → tools.py → scrapes page
└─→ Groq uses results to answer

Diagram:

User Input
↓
System + User → Groq API
↓
LLM decides → tool call (e.g. web_search)
↓
tools.py executes it
↓
Return execution result to Groq
↓
LLM may decide next tool (e.g. scrape_url) or final answer
↓
Answer returns to UI

markdown
Copy
Edit


## 🧪 Example Use Cases:
- “What’s the latest GPT‑4o release date?” → uses `web_search`
- “Summarize content at https://example.com” → `web_search` then `scrape_url`

## 📚 References
- Groq docs on tool use :contentReference[oaicite:3]{index=3}  
