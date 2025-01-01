# tweet.py
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Tweet:
    text: str
    id: str
    created_at: str
    media_urls: List[str] = None
    
    @classmethod
    def from_api_response(cls, data: dict) -> 'Tweet':
        """Create a Tweet instance from Twitter's API response"""
        return cls(
            text=data['legacy']['full_text'],
            id=data['legacy']['id_str'],
            created_at=data['legacy']['created_at'],
            media_urls=_extract_media_urls(data)
        )

def _extract_media_urls(data: dict) -> List[str]:
    """Helper to extract media URLs from the Twitter API response"""
    urls = []
    if 'extended_entities' in data['legacy']:
        for item in data['legacy']['extended_entities']['media']:
            if item['type'] == 'video':
                variants = item['video_info']['variants']
                mp4_variants = [v for v in variants if v['content_type'] == 'video/mp4']
                if mp4_variants:
                    highest_quality = max(mp4_variants, key=lambda x: x.get('bitrate', 0))
                    urls.append(highest_quality['url'])
            else:
                urls.append(item['media_url_https'])
    return urls