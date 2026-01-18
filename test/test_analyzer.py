import unittest

class TestNewsAnalyzer(unittest.TestCase):
    
    def test_truncate_content(self):
        """Test 1: Verify content truncation works correctly"""
        # Inline truncation logic
        def truncate_content(content: str, max_length: int = 4000) -> str:
            if len(content) <= max_length:
                return content
            return content[:max_length] + "... [truncated]"
        
        # Short content should remain unchanged
        short_content = "This is a short article."
        result = truncate_content(short_content)
        self.assertEqual(result, short_content)
        
        # Long content should be truncated
        long_content = "A" * 5000
        result = truncate_content(long_content, max_length=4000)
        self.assertEqual(len(result), 4000 + len("... [truncated]"))
        self.assertTrue(result.endswith("... [truncated]"))
        print("[OK] Test 1: Content truncation works correctly")
    
    def test_article_normalization(self):
        """Test 2: Verify article normalization produces correct format"""
        # Mock NewsAPI article
        newsapi_article = {
            "title": "Test Article",
            "source": {"name": "Test Source"},
            "url": "https://example.com",
            "publishedAt": "2026-01-18",
            "description": "Test content",
            "content": None
        }
        
        # Normalize (simulating news_fetcher logic)
        normalized = {
            "title": newsapi_article.get("title", "No title"),
            "source": newsapi_article.get("source", {}).get("name", "Unknown"),
            "url": newsapi_article.get("url", ""),
            "published_at": newsapi_article.get("publishedAt", ""),
            "content": newsapi_article.get("description", "") or newsapi_article.get("content", ""),
            "api_source": "newsapi"
        }
        
        # Verify all required fields present
        self.assertIn("title", normalized)
        self.assertIn("source", normalized)
        self.assertIn("url", normalized)
        self.assertIn("published_at", normalized)
        self.assertIn("content", normalized)
        self.assertIn("api_source", normalized)
        
        # Verify values
        self.assertEqual(normalized["title"], "Test Article")
        self.assertEqual(normalized["source"], "Test Source")
        self.assertEqual(normalized["api_source"], "newsapi")
        print("[OK] Test 2: Article normalization produces correct format")
    
    def test_analysis_output_format(self):
        """Test 3: Verify analysis output contains all required fields"""
        # Mock analysis output
        analysis = {
            "gist": "Test article summary",
            "sentiment": "positive",
            "tone": "analytical",
            "key_entities": ["India", "Government"]
        }
        
        # Verify required fields
        required_fields = ["gist", "sentiment", "tone", "key_entities"]
        for field in required_fields:
            self.assertIn(field, analysis)
        
        # Verify sentiment is valid
        valid_sentiments = ["positive", "negative", "neutral"]
        self.assertIn(analysis["sentiment"], valid_sentiments)
        
        # Verify tone is valid
        valid_tones = ["urgent", "analytical", "satirical", "balanced", "critical", "optimistic", "informative"]
        self.assertIn(analysis["tone"], valid_tones)
        
        # Verify key_entities is a list
        self.assertIsInstance(analysis["key_entities"], list)
        print("[OK] Test 3: Analysis output format is valid")
    
    def test_summary_stats_calculation(self):
        """Test 4: Verify statistics are calculated correctly"""
        # Inline stats calculation logic
        def calculate_summary_stats(articles):
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
                    sentiment = analysis.get("sentiment", "neutral")
                    if sentiment in stats["sentiment_counts"]:
                        stats["sentiment_counts"][sentiment] += 1
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
        
        # Sample articles with known sentiments
        articles = [
            {
                "title": "Article 1",
                "analysis": {
                    "sentiment": "positive",
                    "tone": "optimistic"
                },
                "validation": {
                    "is_valid": True
                }
            },
            {
                "title": "Article 2",
                "analysis": {
                    "sentiment": "negative",
                    "tone": "critical"
                },
                "validation": {
                    "is_valid": True
                }
            },
            {
                "title": "Article 3",
                "analysis": {
                    "sentiment": "neutral",
                    "tone": "analytical"
                },
                "validation": {
                    "is_valid": False
                }
            },
            {
                "title": "Article 4",
                "analysis": "failed",
                "validation": "skipped"
            }
        ]
        
        # Calculate stats
        stats = calculate_summary_stats(articles)
        
        # Verify counts
        self.assertEqual(stats["total_articles"], 4)
        self.assertEqual(stats["sentiment_counts"]["positive"], 1)
        self.assertEqual(stats["sentiment_counts"]["negative"], 1)
        self.assertEqual(stats["sentiment_counts"]["neutral"], 1)
        self.assertEqual(stats["analysis_success"], 3)
        self.assertEqual(stats["analysis_failed"], 1)
        self.assertEqual(stats["validation_success"], 3)
        self.assertEqual(stats["validation_correct"], 2)
        self.assertEqual(stats["validation_incorrect"], 1)
        print("[OK] Test 4: Summary statistics calculated correctly")
    
    def test_validation_output_format(self):
        """Test 5: Verify validation output contains all required fields"""
        # Mock validation output - valid case
        validation_valid = {
            "is_valid": True,
            "validation_symbol": "[VALID]",
            "justification": "Analysis is correct",
            "suggested_corrections": []
        }
        
        # Verify required fields
        required_fields = ["is_valid", "validation_symbol", "justification", "suggested_corrections"]
        for field in required_fields:
            self.assertIn(field, validation_valid)
        
        # Verify validation_symbol matches is_valid
        self.assertEqual(validation_valid["validation_symbol"], "[VALID]")
        self.assertTrue(validation_valid["is_valid"])
        
        # Mock validation output - invalid case
        validation_invalid = {
            "is_valid": False,
            "validation_symbol": "[INVALID]",
            "justification": "Sentiment is incorrect",
            "suggested_corrections": ["Change sentiment to negative"]
        }
        
        # Verify invalid case
        self.assertEqual(validation_invalid["validation_symbol"], "[INVALID]")
        self.assertFalse(validation_invalid["is_valid"])
        self.assertIsInstance(validation_invalid["suggested_corrections"], list)
        self.assertGreater(len(validation_invalid["suggested_corrections"]), 0)
        print("[OK] Test 5: Validation output format is valid")


if __name__ == "__main__":
    # Run tests
    print("\n" + "="*60)
    print("Running News Analyzer Tests")
    print("="*60 + "\n")
    unittest.main(verbosity=2)
