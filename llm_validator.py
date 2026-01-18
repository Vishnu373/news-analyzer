import os
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPEN_ROUTER_API")

# Constants
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "mistralai/mistral-7b-instruct"


def init_mistral() -> Optional[OpenAI]:
    """
    Initialize OpenRouter client for Mistral.
    
    Returns:
        Configured OpenAI client (OpenRouter compatible) or None on failure
    """
    if not OPENROUTER_API_KEY:
        print("[ERROR] Mistral: API key not found in .env file")
        return None
    
    try:
        client = OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY,
        )
        print("[OK] Mistral: Client initialized (via OpenRouter)")
        return client
    except Exception as e:
        print(f"[ERROR] Mistral: Initialization failed - {str(e)}")
        return None


def validate_analysis(article: Dict, analysis: Dict, client: OpenAI) -> Optional[Dict]:
    """
    Validate analysis using Mistral via OpenRouter.
    
    Args:
        article: Original article dictionary
        analysis: Analysis from Agent 2
        client: Initialized OpenRouter client
        
    Returns:
        Validation dictionary or None on failure
    """
    title = article.get("title", "No title")
    content = article.get("content", "")[:2000]  # Truncate for validation
    
    # Skip if analysis failed
    if analysis == "failed" or isinstance(analysis, str):
        return {
            "is_valid": False,
            "validation_symbol": "[SKIPPED]",
            "justification": "Analysis was not performed",
            "suggested_corrections": []
        }
    
    gist = analysis.get("gist", "")
    sentiment = analysis.get("sentiment", "")
    tone = analysis.get("tone", "")
    
    prompt = f"""You are a fact-checking validator. Review the following news article analysis and determine if it's accurate.

Original Article:
Title: {title}
Content: {content}

Analysis to Validate:
- Gist: {gist}
- Sentiment: {sentiment}
- Tone: {tone}

Your task:
1. Check if the gist accurately summarizes the article
2. Verify if the sentiment (positive/negative/neutral) matches the article's content
3. Confirm if the tone classification is appropriate
4. Identify any errors or misinterpretations

Respond ONLY with valid JSON in this exact format:
{{
    "is_valid": true or false,
    "justification": "Brief explanation of why the analysis is correct or incorrect",
    "suggested_corrections": ["List any specific corrections needed, empty list if none"]
}}

Rules:
- is_valid: true if analysis is mostly accurate, false if there are significant errors
- justification: 1-2 sentences explaining your assessment
- suggested_corrections: specific issues found, or empty list if analysis is correct"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Clean up response - remove markdown code blocks if present
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1]) if len(lines) > 2 else response_text
        
        # Parse JSON
        validation = json.loads(response_text)
        
        # Add validation symbol
        validation["validation_symbol"] = "[VALID]" if validation.get("is_valid", False) else "[INVALID]"
        
        # Validate required fields
        required_fields = ["is_valid", "justification", "suggested_corrections"]
        if not all(field in validation for field in required_fields):
            print(f"[WARN] Incomplete validation for: {title[:50]}")
            return None
        
        return validation
        
    except Exception as e:
        print(f"[ERROR] Validation failed for '{title[:50]}': {str(e)[:100]}")
        return None


def validate_all_analyses(articles: List[Dict]) -> List[Dict]:
    """
    Validate all analyses using Mistral.
    Continues even if some validations fail.
    
    Args:
        articles: List of articles with analysis
        
    Returns:
        List of articles with validation added
    """
    print("\n" + "="*60)
    print("Starting Validation (Mistral via OpenRouter)")
    print("="*60)
    
    client = init_mistral()
    if not client:
        print("[ERROR] FAILED: Could not initialize Mistral")
        for article in articles:
            article["validation"] = "skipped"
            article["validation_error"] = "mistral_init_failed"
        return articles
    
    validated_articles = []
    success_count = 0
    fail_count = 0
    
    for idx, article in enumerate(articles, 1):
        print(f"\n[{idx}/{len(articles)}] Validating: {article['title'][:60]}...")
        
        analysis = article.get("analysis")
        validation = validate_analysis(article, analysis, client)
        
        if validation:
            article["validation"] = validation
            validated_articles.append(article)
            success_count += 1
            symbol = validation["validation_symbol"]
            print(f"   {symbol} Valid: {validation['is_valid']} | {validation['justification'][:60]}")
        else:
            article["validation"] = "skipped"
            article["validation_error"] = "validation_failed"
            validated_articles.append(article)
            fail_count += 1
            print(f"   [WARN] Validation failed")
    
    # Summary
    print("\n" + "-"*60)
    print(f"[OK] SUCCESS: Validated {success_count}/{len(articles)} articles")
    if fail_count > 0:
        print(f"[WARN] WARNING: {fail_count} articles failed validation")
    print("="*60 + "\n")
    
    return validated_articles


if __name__ == "__main__":
    # Test the validator with a sample article and analysis
    sample_article = {
        "title": "India announces new economic policy",
        "content": "India's government announced a new economic policy aimed at boosting manufacturing. The policy includes tax incentives for domestic companies and aims to create millions of jobs over the next five years.",
    }
    
    sample_analysis = {
        "gist": "India announces economic policy to boost manufacturing with tax incentives and job creation goals.",
        "sentiment": "positive",
        "tone": "analytical",
        "key_entities": ["India", "government"]
    }
    
    client = init_mistral()
    if client:
        result = validate_analysis(sample_article, sample_analysis, client)
        if result:
            print("\nValidation Result:")
            print(json.dumps(result, indent=2))
