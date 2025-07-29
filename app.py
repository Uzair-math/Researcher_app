import os, json, streamlit as st
from dotenv import load_dotenv
from groq import Groq
from tools import web_search, scrape_url 

load_dotenv()

MODEL = "llama-3.3-70b-versatile" 
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

#  functions 
available_functions = {
    "web_search": web_search,
    "scrape_url": scrape_url
}

# Tool 
tools = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web and return top results",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to look up"
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "scrape_url",
            "description": "Scrape webpage content",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to scrape"
                    }
                },
                "required": ["url"],
            },
        },
    },
]

SYSTEM_PROMPT = """
You are a helpful research assistant with access to web search and URL scraping tools.

CRITICAL: You must use the tool calling mechanism properly. Do NOT output function calls as text like <web_search>{"query": "example"}</web_search>.

Instead, use the tools parameter in your API calls to make proper tool calls. The system will handle the tool execution automatically.

Available tools:
- web_search: Search the web for current information
- scrape_url: Get detailed content from a specific webpage

When a user asks a question that requires current information, you should automatically use the web_search tool to find relevant information, then provide a comprehensive answer based on the search results.
"""

def run_agent(user_input: str) -> str:
    try:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ]
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.0,
            max_tokens=4096
        )
        response_message = response.choices[0].message
        messages.append(response_message)
        
        # Check if the model output function call syntax as text (incorrect behavior)
        if response_message.content and ("<web_search>" in response_message.content or "<scrape_url>" in response_message.content):
            # Force the model to use proper tool calling by making another request
            messages.append({
                "role": "user", 
                "content": "Please use the proper tool calling mechanism instead of outputting function calls as text. Search for the information I requested."
            })
            
            # Make another request to force proper tool usage
            retry_response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.0,
                max_tokens=4096
            )
            
            response_message = retry_response.choices[0].message
            messages.append(response_message)
        
        # Check if tool_calls exist and process them
        if response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                if function_name in available_functions:
                    function_to_call = available_functions[function_name]
                    function_response = function_to_call(**function_args)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": function_response
                    })
                else:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps({"error": f"Function {function_name} not found"})
                    })
            
            # Make final request after tool execution
            final_response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.0,
                max_tokens=4096
            )
            
            return final_response.choices[0].message.content.strip()
        else:
            # If no tool calls, return the initial response
            return response_message.content.strip()
        
    except Exception as e:
        return f"Error: {str(e)}"

st.title("Researcher Agent (Serper + FireCrawl)")
query = st.text_input("Ask anything:")
if st.button("Search"):
    with st.spinner("Thinking…"):
        result = run_agent(query)
        st.write(result)
