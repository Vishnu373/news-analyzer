import os
import json
from datetime import datetime
from typing import List, Dict
from news_fetcher import fetch_all_news
from llm_analyzer import analyze_all_articles
from llm_validator import validate_all_analyses


def save_json_report(articles: List[Dict], filepath: str = "output/analysis_reports.json"):
    """Save complete analysis to JSON file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    
    print(f"Saved JSON report: {filepath}")


def save_raw_articles(articles: List[Dict], filepath: str = "output/raw_articles.json"):
    """Save raw fetched articles to JSON file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Create clean version without analysis/validation
    raw_articles = []
    for article in articles:
        raw_articles.append({
            "title": article.get("title"),
            "source": article.get("source"),
            "url": article.get("url"),
            "published_at": article.get("published_at"),
            "content": article.get("content"),
            "api_source": article.get("api_source")
        })
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(raw_articles, f, indent=2, ensure_ascii=False)
    
    print(f"Saved raw articles: {filepath}")


def calculate_summary_stats(articles: List[Dict]) -> Dict:
    """Calculate summary statistics from analyzed articles."""
    stats = {
        "total_articles": len(articles),
        "sentiment_counts": {"positive": 0, "negative": 0, "neutral": 0},
        "tone_counts": {},
        "analysis_success": 0,
        "analysis_failed": 0,
        "validation_success": 0,
        "validation_failed": 0,
        "validation_correct": 0,
        "validation_incorrect": 0
    }
    
    for article in articles:
        analysis = article.get("analysis")
        validation = article.get("validation")
        
        # Count analysis results
        if analysis and analysis != "failed" and not isinstance(analysis, str):
            stats["analysis_success"] += 1
            
            # Count sentiments
            sentiment = analysis.get("sentiment", "neutral")
            if sentiment in stats["sentiment_counts"]:
                stats["sentiment_counts"][sentiment] += 1
            
            # Count tones
            tone = analysis.get("tone", "unknown")
            stats["tone_counts"][tone] = stats["tone_counts"].get(tone, 0) + 1
        else:
            stats["analysis_failed"] += 1
        
        # Count validation results
        if validation and validation != "skipped" and not isinstance(validation, str):
            stats["validation_success"] += 1
            if validation.get("is_valid"):
                stats["validation_correct"] += 1
            else:
                stats["validation_incorrect"] += 1
        else:
            stats["validation_failed"] += 1
    
    return stats


def generate_markdown_report(articles: List[Dict], stats: Dict, filepath: str = "output/final_report.md"):
    """Generate human-readable Markdown report."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    report_lines = []
    
    # Header
    report_lines.append("# News Analysis Report")
    report_lines.append("")
    report_lines.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"**Articles Analyzed:** {stats['total_articles']}")
    report_lines.append(f"**Source:** NewsAPI + Guardian API")
    report_lines.append("")
    
    # Summary
    report_lines.append("## Summary")
    report_lines.append("")
    report_lines.append(f"- **Positive:** {stats['sentiment_counts']['positive']} articles")
    report_lines.append(f"- **Negative:** {stats['sentiment_counts']['negative']} articles")
    report_lines.append(f"- **Neutral:** {stats['sentiment_counts']['neutral']} articles")
    report_lines.append("")
    report_lines.append(f"**Analysis Success Rate:** {stats['analysis_success']}/{stats['total_articles']} ({stats['analysis_success']/stats['total_articles']*100:.1f}%)")
    report_lines.append(f"**Validation Success Rate:** {stats['validation_success']}/{stats['total_articles']} ({stats['validation_success']/stats['total_articles']*100:.1f}%)")
    
    if stats['validation_success'] > 0:
        accuracy = stats['validation_correct'] / stats['validation_success'] * 100
        report_lines.append(f"**Validation Accuracy:** {stats['validation_correct']}/{stats['validation_success']} ({accuracy:.1f}%)")
    
    report_lines.append("")
    
    # Tone breakdown
    if stats['tone_counts']:
        report_lines.append("### Tone Distribution")
        report_lines.append("")
        for tone, count in sorted(stats['tone_counts'].items(), key=lambda x: x[1], reverse=True):
            report_lines.append(f"- **{tone.capitalize()}:** {count} articles")
        report_lines.append("")
    
    # Detailed Analysis
    report_lines.append("---")
    report_lines.append("")
    report_lines.append("## Detailed Analysis")
    report_lines.append("")
    
    for idx, article in enumerate(articles, 1):
        title = article.get("title", "No title")
        source = article.get("source", "Unknown")
        url = article.get("url", "")
        analysis = article.get("analysis")
        validation = article.get("validation")
        
        report_lines.append(f"### Article {idx}: \"{title}\"")
        report_lines.append("")
        report_lines.append(f"- **Source:** {source}")
        report_lines.append(f"- **URL:** [{url}]({url})")
        report_lines.append("")
        
        # Analysis section
        if analysis and analysis != "failed" and not isinstance(analysis, str):
            gist = analysis.get("gist", "N/A")
            sentiment = analysis.get("sentiment", "N/A")
            tone = analysis.get("tone", "N/A")
            entities = analysis.get("key_entities", [])
            
            report_lines.append(f"- **Gist:** {gist}")
            report_lines.append(f"- **LLM#1 Sentiment:** {sentiment.capitalize()}")
            report_lines.append(f"- **Tone:** {tone.capitalize()}")
            
            if entities:
                report_lines.append(f"- **Key Entities:** {', '.join(entities)}")
        else:
            report_lines.append(f"- **Analysis:** [FAILED]")
        
        report_lines.append("")
        
        # Validation section
        if validation and validation != "skipped" and not isinstance(validation, str):
            symbol = validation.get("validation_symbol", "?")
            is_valid = validation.get("is_valid", False)
            justification = validation.get("justification", "N/A")
            corrections = validation.get("suggested_corrections", [])
            
            report_lines.append(f"- **LLM#2 Validation:** {symbol} {'Correct' if is_valid else 'Incorrect'}")
            report_lines.append(f"- **Justification:** {justification}")
            
            if corrections:
                report_lines.append(f"- **Suggested Corrections:**")
                for correction in corrections:
                    report_lines.append(f"  - {correction}")
        else:
            report_lines.append(f"- **Validation:** [SKIPPED]")
        
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
    
    # Write to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f"Saved Markdown report: {filepath}")


def run_pipeline():
    """Execute the complete dual-LLM news analysis pipeline."""
    print("\n" + "="*60)
    print("DUAL-LLM NEWS ANALYSIS PIPELINE")
    print("="*60)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")
    
    # Agent 1: Fetch news
    articles = fetch_all_news(query="India politics", target_count=12)
    
    if not articles:
        print("\n[ERROR] PIPELINE FAILED: No articles fetched")
        return
    
    # Save raw articles
    save_raw_articles(articles)
    
    # Agent 2: Analyze with Gemini
    articles = analyze_all_articles(articles)
    
    # Agent 3: Validate with Mistral
    articles = validate_all_analyses(articles)
    
    # Agent 4: Generate outputs
    print("\n" + "="*60)
    print("Generating Reports")
    print("="*60 + "\n")
    
    stats = calculate_summary_stats(articles)
    save_json_report(articles)
    generate_markdown_report(articles, stats)
    
    # Final summary
    print("\n" + "="*60)
    print("[OK] PIPELINE COMPLETE")
    print("="*60)
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nArticles Processed: {stats['total_articles']}")
    print(f"Analysis Success: {stats['analysis_success']}/{stats['total_articles']}")
    print(f"Validation Success: {stats['validation_success']}/{stats['total_articles']}")
    print("\nOutput Files:")
    print("  - output/raw_articles.json")
    print("  - output/analysis_reports.json")
    print("  - output/final_report.md")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_pipeline()
