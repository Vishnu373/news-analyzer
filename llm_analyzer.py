import os
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Constants
MAX_CONTENT_LENGTH = 4000  # characters
MODEL_NAME = "gemini-3-flash-preview"


def init_gemini() -> Optional[genai.Client]:
    """
    Initialize Gemini client.
    
    Returns:
        Configured Gemini client or None on failure
    """
    if not GEMINI_API_KEY:
        print("[ERROR] Gemini: API key not found in .env file")
        return None
    
    try:
        os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
        client = genai.Client()
        print(f"[OK] Gemini: Client initialized ({MODEL_NAME})")
        return client
    except Exception as e:
        print(f"[ERROR] Gemini: Initialization failed - {str(e)}")
        return None


def truncate_content(content: str, max_length: int = MAX_CONTENT_LENGTH) -> str:
    """Truncate content to fit within token limits."""
    if len(content) <= max_length:
        return content
    return content[:max_length] + "... [truncated]"


def analyze_article(article: Dict, client: genai.Client) -> Optional[Dict]:
    """
    Analyze a single article using Gemini.
    
    Args:
        article: Article dictionary with title, content, etc.
        client: Initialized Gemini client
        
    Returns:
        Analysis dictionary or None on failure
    """
    title = article.get("title", "No title")
    content = truncate_content(article.get("content", ""))
    
    if not content or content == "No content":
        print(f"[WARN] Skipping article with no content: {title[:50]}")
        return {
            "gist": "No content available for analysis",
            "sentiment": "neutral",
            "tone": "unknown",
            "key_entities": [],
            "error": "no_content"
        }
    
    prompt = f"""Analyze the following news article about Indian politics and provide a structured JSON response.

Article Title: {title}

Article Content:
{content}

Provide your analysis in the following JSON format (respond ONLY with valid JSON, no other text):
{{
    "gist": "A concise 1-2 sentence summary of the article",
    "sentiment": "positive OR negative OR neutral",
    "tone": "One of: urgent, analytical, satirical, balanced, critical, optimistic, informative",
    "key_entities": ["List of important people, organizations, or places mentioned"]
}}

Rules:
- Sentiment: positive (favorable/good news), negative (unfavorable/bad news), neutral (factual/balanced)
- Tone: Choose the most appropriate tone that matches the article's writing style
- Key entities: Extract 3-5 most important names/organizations
- Respond ONLY with valid JSON, no markdown formatting or additional text"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        response_text = response.text.strip()
        
        # Clean up response - remove markdown code blocks if present
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1]) if len(lines) > 2 else response_text
        
        # Parse JSON
        analysis = json.loads(response_text)
        
        # Validate required fields
        required_fields = ["gist", "sentiment", "tone", "key_entities"]
        if not all(field in analysis for field in required_fields):
            print(f"[WARN] Incomplete analysis for: {title[:50]}")
            return None
        
        return analysis
        
    except Exception as e:
        print(f"[ERROR] Analysis failed for '{title[:50]}': {str(e)[:100]}")
        return None


def analyze_all_articles(articles: List[Dict]) -> List[Dict]:
    """
    Analyze all articles using Gemini.
    Continues even if some analyses fail.
    
    Args:
        articles: List of article dictionaries
        
    Returns:
        List of articles with analysis added
    """
    print("\n" + "="*60)
    print("Starting LLM Analysis (Gemini)")
    print("="*60)
    
    client = init_gemini()
    if not client:
        print("[ERROR] FAILED: Could not initialize Gemini")
        for article in articles:
            article["analysis"] = "failed"
            article["analysis_error"] = "gemini_init_failed"
        return articles
    
    analyzed_articles = []
    success_count = 0
    fail_count = 0
    
    for idx, article in enumerate(articles, 1):
        print(f"\n[{idx}/{len(articles)}] Analyzing: {article['title'][:60]}...")
        
        analysis = analyze_article(article, client)
        
        if analysis:
            article["analysis"] = analysis
            analyzed_articles.append(article)
            success_count += 1
            print(f"   [OK] Sentiment: {analysis['sentiment']} | Tone: {analysis['tone']}")
        else:
            article["analysis"] = "failed"
            article["analysis_error"] = "analysis_failed"
            analyzed_articles.append(article)
            fail_count += 1
            print(f"   [ERROR] Analysis failed")
    
    # Summary
    print("\n" + "-"*60)
    print(f"[OK] SUCCESS: Analyzed {success_count}/{len(articles)} articles")
    if fail_count > 0:
        print(f"[WARN] WARNING: {fail_count} articles failed analysis")
    print("="*60 + "\n")
    
    return analyzed_articles


if __name__ == "__main__":
    # Test the analyzer with a sample article
    sample_article = {
        "title": "India announces new economic policy",
        "source": "Test Source",
        "url": "https://example.com",
        "published_at": "2026-01-18",
        "content": "India's government announced a new economic policy aimed at boosting manufacturing. The policy includes tax incentives for domestic companies and aims to create millions of jobs over the next five years.",
        "api_source": "test"
    }
    
    client = init_gemini()
    if client:
        result = analyze_article(sample_article, client)
        if result:
            print("\nAnalysis Result:")
            print(json.dumps(result, indent=2))
