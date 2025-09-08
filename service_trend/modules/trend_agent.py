from googleapiclient.discovery import build

class TrendAgent:
    def __init__(self):
        self.fallback_trends = [
            "mobile gaming", "indie games", "puzzle games",
            "action games", "casual games", "strategy games"
        ]

    def get_youtube_trends(self, api_key, region="US", max_results=10):
        """YouTube Data API v3 ile gaming trendlerini çek"""
        youtube = build("youtube", "v3", developerKey=api_key)
        request = youtube.videos().list(
            part="snippet",
            chart="mostPopular",
            regionCode=region,
            videoCategoryId="20",  # Gaming category
            maxResults=max_results
        )
        response = request.execute()
        return [item["snippet"]["title"] for item in response["items"]]

    def get_fallback_trends(self):
        return self.fallback_trends
