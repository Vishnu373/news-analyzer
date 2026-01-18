"""
News Fetcher - Agent 1
Fetches news articles from NewsAPI and Guardian API about Indian politics.
"""

import os
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GUARDIAN_API_KEY = os.getenv("GUARDIAN_API_KEY")

# Constants
NEWS_API_URL = "https://newsapi.org/v2/everything"
GUARDIAN_API_URL = "https://content.guardianapis.com/search"
TIMEOUT = 10  # seconds


def fetch_from_newsapi(query: str = "India politics", max_articles: int = 8) -> Optional[List[Dict]]:
    """
    Fetch articles from NewsAPI.
    
    Args:
        query: Search query
        max_articles: Maximum number of articles to fetch
        
    Returns:
        List of normalized articles or None on failure
    """
    if not NEWS_API_KEY:
        print("[ERROR] NewsAPI: API key not found in .env file")
        return None
    
    params = {
        "q": query,
        "apiKey": NEWS_API_KEY,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": max_articles
    }
    
    print(f"Fetching from NewsAPI: '{query}'...")
    
    try:
        response = requests.get(NEWS_API_URL, params=params, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") != "ok":
            print(f"[ERROR] NewsAPI: API returned status '{data.get('status')}'")
            return None
        
        articles = data.get("articles", [])
        
        if not articles:
            print("[WARN] NewsAPI: No articles found")
            return []
        
        # Normalize article format
        normalized = []
        for article in articles:
            normalized.append({
                "title": article.get("title", "No title"),
                "source": article.get("source", {}).get("name", "Unknown"),
                "url": article.get("url", ""),
                "published_at": article.get("publishedAt", ""),
                "content": article.get("description", "") or article.get("content", ""),
                "api_source": "newsapi"
            })
        
        print(f"[OK] NewsAPI: Fetched {len(normalized)} articles")
        return normalized
        
    except requests.RequestException as e:
        print(f"[ERROR] NewsAPI: {e}")
        return None


def fetch_from_guardian(query: str = "India politics", max_articles: int = 8) -> Optional[List[Dict]]:
    """
    Fetch articles from Guardian API.
    
    Args:
        query: Search query
        max_articles: Maximum number of articles to fetch
        
    Returns:
        List of normalized articles or None on failure
    """
    if not GUARDIAN_API_KEY:
        print("[ERROR] Guardian: API key not found in .env file")
        return None
    
    params = {
        "q": query,
        "api-key": GUARDIAN_API_KEY,
        "page-size": max_articles,
        "order-by": "newest",
        "show-fields": "bodyText,trailText"
    }
    
    print(f"Fetching from Guardian: '{query}'...")
    
    try:
        response = requests.get(GUARDIAN_API_URL, params=params, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        if data.get("response", {}).get("status") != "ok":
            print(f"[ERROR] Guardian: API returned status '{data.get('response', {}).get('status')}'")
            return None
        
        articles = data.get("response", {}).get("results", [])
        
        if not articles:
            print("[WARN] Guardian: No articles found")
            return []
        
        # Normalize article format
        normalized = []
        for article in articles:
            fields = article.get("fields", {})
            content = fields.get("bodyText", "") or fields.get("trailText", "")
            
            normalized.append({
                "title": article.get("webTitle", "No title"),
                "source": "The Guardian",
                "url": article.get("webUrl", ""),
                "published_at": article.get("webPublicationDate", ""),
                "content": content,
                "api_source": "guardian"
            })
        
        print(f"[OK] Guardian: Fetched {len(normalized)} articles")
        return normalized
        
    except requests.RequestException as e:
        print(f"[ERROR] Guardian: {e}")
        return None


def fetch_all_news(query: str = "India politics", target_count: int = 12) -> List[Dict]:
    """
    Fetch news from both NewsAPI and Guardian API.
    Continues even if one source fails.
    
    Args:
        query: Search query
        target_count: Target total number of articles
        
    Returns:
        Combined list of articles from both sources
    """
    print("\n" + "="*60)
    print("Starting News Fetch")
    print("="*60)
    
    all_articles = []
    articles_per_source = target_count // 2
    
    # Fetch from NewsAPI
    newsapi_articles = fetch_from_newsapi(query, articles_per_source)
    if newsapi_articles:
        all_articles.extend(newsapi_articles)
    
    # Fetch from Guardian
    guardian_articles = fetch_from_guardian(query, articles_per_source)
    if guardian_articles:
        all_articles.extend(guardian_articles)
    
    # Summary
    print("\n" + "-"*60)
    if not all_articles:
        print("[ERROR] FAILED: No articles fetched from any source")
    else:
        print(f"[OK] SUCCESS: Fetched {len(all_articles)} total articles")
        newsapi_count = sum(1 for a in all_articles if a["api_source"] == "newsapi")
        guardian_count = sum(1 for a in all_articles if a["api_source"] == "guardian")
        print(f"   - NewsAPI: {newsapi_count} articles")
        print(f"   - Guardian: {guardian_count} articles")
    print("="*60 + "\n")
    
    return all_articles


if __name__ == "__main__":
    # Test the news fetcher
    articles = fetch_all_news()
    
    if articles:
        print("\nSample Article:")
        print(f"Title: {articles[0]['title']}")
        print(f"Source: {articles[0]['source']}")
        print(f"URL: {articles[0]['url']}")
        print(f"Content preview: {articles[0]['content'][:200]}...")
