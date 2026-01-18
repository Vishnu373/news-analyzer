# Dual-LLM News Analyzer

A fact-checking pipeline that fetches Indian politics news, analyzes articles with **Gemini** (LLM#1), and validates the analysis with **Mistral** (LLM#2).

## Overview

This project demonstrates a multi-agent LLM system where:
- fetches news from NewsAPI and Guardian API
- analyzes articles using Google Gemini for gist, sentiment, and tone
- validates the analysis using Mistral 7B via OpenRouter
- generates JSON and Markdown reports

## File Structure

```
news-analyzer/
├── news_fetcher.py          # Fetches news from NewsAPI + Guardian
├── llm_analyzer.py          # Gemini-based analysis
├── llm_validator.py         # Mistral-based validation
├── main.py                  # Orchestrator + output generation
├── requirements.txt         # Python dependencies
├── .env                     # API keys (not committed)
├── .gitignore              # Git ignore rules
├── test/
│   └── test_analyzer.py    # Unit tests (5 test cases)
└── output/                 # Generated reports (not committed)
    ├── raw_articles.json
    ├── analysis_reports.json
    └── final_report.md
```

## Setup

### 1. Clone Repository

```bash
git clone https://github.com/Vishnu373/news-analyzer.git
cd news-analyzer
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

Create a `.env` file in the project root:

```env
# LLM API Keys
GEMINI_API_KEY=your_gemini_api_key_here (https://ai.google.dev/)
OPEN_ROUTER_API=your_openrouter_api_key_here (https://openrouter.ai/)

# News API Keys
NEWS_API_KEY=your_newsapi_key_here (https://newsapi.org/)
GUARDIAN_API_KEY=your_guardian_api_key_here (https://open-platform.theguardian.com/)
```

### 4. Run the Pipeline

```bash
python main.py
```

### 5. Run Tests

```bash
python test/test_analyzer.py
```

## Output

The pipeline generates 3 files in the `output/` directory:

1. **raw_articles.json** - Raw fetched articles
2. **analysis_reports.json** - Complete analysis with validation
3. **final_report.md** - Human-readable report with:
   - Sentiment summary (positive/negative/neutral counts)
   - Analysis success rate
   - Validation accuracy
   - Detailed per-article breakdown

## Example Output

```markdown
# News Analysis Report

**Date:** 2026-01-18 16:46:52
**Articles Analyzed:** 6
**Source:** NewsAPI + Guardian API

## Summary
- Positive: 2 articles
- Negative: 1 articles
- Neutral: 3 articles

**Analysis Success Rate:** 6/6 (100.0%)
**Validation Success Rate:** 6/6 (100.0%)
```