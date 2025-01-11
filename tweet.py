from datetime import datetime, timezone
import html

import json
from typing import List, Optional

from sqlmodel import Field, SQLModel

# TODO: create a separate RawTweet to store raw tweet data
# have Tweet responsible for storing processed tweet data
class Tweet(SQLModel, table=True):
    id: str = Field(primary_key=True)
    text: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    media_urls: Optional[str] = Field(default=None)
    is_retweet: bool = False
    mirrored_at: Optional[datetime] = Field(default=None)

    @property
    def media_urls_list(self) -> List[str]:
        """Return media URLs as a list"""
        return json.loads(self.media_urls) if self.media_urls else []
    
    @media_urls_list.setter
    def media_urls_list(self, urls: List[str]):
        """Set media URLs as a list"""
        self.media_urls = json.dumps(urls) if urls else None

    @classmethod
    def from_api_response(cls, data: dict) -> "Tweet":
        """Create a Tweet instance from Twitter's API response"""
        is_retweet = "retweeted_status_result" in data["legacy"]
        urls = _extract_media_urls(data)

        tweet = cls(
            text=html.unescape(data["legacy"]["full_text"]),
            id=data["legacy"]["id_str"],
            is_retweet=is_retweet,
        )
        tweet.media_urls_list = urls

        return tweet



def _extract_media_urls(data: dict) -> List[str]:
    """Helper to extract media URLs from the Twitter API response"""
    urls = []
    if "extended_entities" in data["legacy"]:
        for item in data["legacy"]["extended_entities"]["media"]:
            if item["type"] == "video":
                variants = item["video_info"]["variants"]
                mp4_variants = [v for v in variants if v["content_type"] == "video/mp4"]
                if mp4_variants:
                    highest_quality = max(mp4_variants, key=lambda x: x.get("bitrate", 0))
                    urls.append(highest_quality["url"])
            else:
                urls.append(item["media_url_https"])
    return urls
