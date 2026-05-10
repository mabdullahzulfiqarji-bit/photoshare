"""
Azure AI Services:
  1. Azure Computer Vision - image tag analysis
  2. Azure Language / TextAnalytics - sentiment analysis on captions/comments

Falls back gracefully when not configured (returns empty results).
"""

import json
from typing import Optional, Tuple, List
from config import settings


class AIService:
    """Azure Cognitive / AI Services wrapper."""

    def __init__(self):
        self.vision_enabled = bool(settings.AZURE_VISION_KEY and settings.AZURE_VISION_ENDPOINT)
        self.language_enabled = False  # Will enable if key present

        if self.vision_enabled:
            from azure.ai.vision.imageanalysis import ImageAnalysisClient
            from azure.core.credentials import AzureKeyCredential
            self.vision_client = ImageAnalysisClient(
                endpoint=settings.AZURE_VISION_ENDPOINT,
                credential=AzureKeyCredential(settings.AZURE_VISION_KEY),
            )
            print("✅ Azure AI Vision connected")
        else:
            print("⚠️  Azure AI Vision not configured — analysis disabled")

        # Azure Language for sentiment
        if settings.AZURE_VISION_KEY:  # Reuse same key if multi-service resource
            try:
                from azure.ai.textanalytics import TextAnalyticsClient
                from azure.core.credentials import AzureKeyCredential
                self.language_client = TextAnalyticsClient(
                    endpoint=settings.AZURE_VISION_ENDPOINT or "",
                    credential=AzureKeyCredential(settings.AZURE_VISION_KEY),
                )
                self.language_enabled = True
                print("✅ Azure Language (Sentiment) connected")
            except Exception:
                pass

    def analyze_image(self, image_url: str) -> Tuple[List[str], str]:
        """
        Analyze an image URL with Azure Computer Vision.
        Returns: (tags_list, description_string)
        """
        if not self.vision_enabled:
            return [], ""

        try:
            from azure.ai.vision.imageanalysis.models import VisualFeatures
            result = self.vision_client.analyze_from_url(
                image_url=image_url,
                visual_features=[VisualFeatures.TAGS, VisualFeatures.CAPTION],
                language="en",
            )

            tags = []
            if result.tags:
                tags = [t.name for t in result.tags.list if t.confidence > 0.7]

            description = ""
            if result.caption:
                description = result.caption.text

            return tags, description
        except Exception as e:
            print(f"Vision analysis failed: {e}")
            return [], ""

    def analyze_sentiment(self, text: str) -> Tuple[str, float]:
        """
        Analyze sentiment of text using Azure Language Service.
        Returns: (sentiment_label, confidence_score)
        sentiment_label: 'positive', 'negative', or 'neutral'
        """
        if not self.language_enabled or not text:
            return "neutral", 0.5

        try:
            result = self.language_client.analyze_sentiment([text])
            doc = result[0]
            if doc.is_error:
                return "neutral", 0.5
            return doc.sentiment, doc.confidence_scores[doc.sentiment]
        except Exception as e:
            print(f"Sentiment analysis failed: {e}")
            return "neutral", 0.5

    def get_image_tags_json(self, image_url: str) -> str:
        """Return AI tags as JSON string for database storage."""
        tags, description = self.analyze_image(image_url)
        return json.dumps({"tags": tags, "description": description})


# Singleton
ai_service = AIService()
