# app.py
import os, json, streamlit as st
from dotenv import load_dotenv
from groq import Groq
from tools import web_search, scrape_url   # one‑way import → no cycle

load_dotenv()

MODEL  = "llama-3.3-70b-versatile"  # or 70b variant
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

tools = [
    {
        "type":"function",
        "function":{
            "name":"web_search",
            "description":"Search the web and return top results",
            "parameters":{
                "type":"object",
                "properties":{"query":{"type":"string"}},
                "required":["query"],
            },
        },
    },
    {
        "type":"function",
        "function":{
            "name":"scrape_url",
            "description":"Scrape webpage content",
            "parameters":{
                "type":"object",
                "properties":{"url":{"type":"string"}},
                "required":["url"],
            },
        },
    },
]

SYSTEM_PROMPT = """
You are a helpful research assistant. When users ask questions, you have access to tools that you can use to search for information.

IMPORTANT: Do NOT output function call syntax as text. Instead, use the available tools through the proper tool calling mechanism.

Available tools:
- web_search: Use this to search the web for information
- scrape_url: Use this to get detailed content from a specific URL

When you need information, use these tools and then provide a comprehensive answer based on the results.
"""

def run_agent(user_input: str) -> str:
    # For research queries, directly use web_search
    try:
        # First, search for information
        search_results = web_search(user_input)
        search_data = json.loads(search_results)
        
        # Then ask the model to provide a response based on the search results
        msgs = [
            {"role":"system","content":"You are a helpful research assistant. Provide comprehensive answers based on the search results provided."},
            {"role":"user","content":f"Question: {user_input}\n\nSearch Results: {search_results}"},
        ]
        
        resp = client.chat.completions.create(
            model=MODEL,
            messages=msgs,
            temperature=0.0,
            top_p=1.0,
        )
        
        return resp.choices[0].message.content.strip()
        
    except Exception as e:
        return f"Error: {str(e)}"

# --- Streamlit UI ---
st.title("Researcher Agent (Serper + FireCrawl)")
query = st.text_input("Ask anything:")
if st.button("Search"):
    with st.spinner("Thinking…"):
        st.write(run_agent(query))
