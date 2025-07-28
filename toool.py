# tools.py
import os, json, requests
from dotenv import load_dotenv

load_dotenv()
SERPER_API_KEY    = os.getenv("SERPER_API_KEY")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

def web_search(query: str) -> str:
    """Return top Serper (Google Search) results as JSON‐serialisable primitives."""
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "q": query,
        "num": 5
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract organic search results
        web_results = []
        for item in data.get("organic", [])[:5]:  # Limit to 5 results
            web_results.append({
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", "")
            })
        
        # If no organic results, provide fallback
        if not web_results:
            web_results = [
                {
                    "title": f"Search results for: {query}",
                    "url": f"https://www.google.com/search?q={query.replace(' ', '+')}",
                    "snippet": f"No results found for '{query}'. You can search manually on Google."
                }
            ]
        
        return json.dumps({"query": query, "web_results": web_results})
        
    except Exception as e:
        # Fallback in case of API error
        return json.dumps({
            "query": query, 
            "web_results": [{
                "title": f"Search for: {query}",
                "url": f"https://www.google.com/search?q={query.replace(' ', '+')}",
                "snippet": f"Error accessing search API: {str(e)}. You can search manually at the provided URL."
            }]
        })

def scrape_url(url: str) -> str:
    """Use FireCrawl to pull cleaned markdown from a page."""
    try:
        resp = requests.post(
            "https://api.firecrawl.dev/scrape",
            headers={"Authorization": f"Bearer {FIRECRAWL_API_KEY}"},
            json={"url": url},
            timeout=30,
        )
        
        if resp.status_code == 200:
            try:
                data = resp.json()
                content = data.get("markdown") or data.get("page_content") or ""
                return json.dumps({"url": url, "content": content})
            except json.JSONDecodeError:
                return json.dumps({"url": url, "content": f"Error: Invalid JSON response from FireCrawl API"})
        else:
            return json.dumps({"url": url, "content": f"Error: FireCrawl API returned status code {resp.status_code}"})
            
    except Exception as e:
        return json.dumps({"url": url, "content": f"Error accessing FireCrawl API: {str(e)}"})
