"""
Social Media Integration - SocialDrafter (Cloud) + SocialPoster (Local).

SocialDrafter: Creates structured social media drafts (Cloud-safe).
SocialPoster: Posts to Twitter/X via API (Local only, SecretGuard enforced).

Usage:
    drafter = SocialDrafter()
    draft = drafter.create_draft("New release!", platform="twitter")

    poster = SocialPoster(settings)
    poster.post("Hello world!")
"""

import json
import logging
import hashlib
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger("platinum.social_client")


@dataclass
class SocialDraft:
    """Structured social media draft."""
    draft_id: str
    platform: str  # twitter, linkedin, etc.
    content: str
    hashtags: List[str] = field(default_factory=list)
    media_urls: List[str] = field(default_factory=list)
    scheduled_time: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    status: str = "draft"


class SocialDrafter:
    """Creates structured social media drafts (Cloud-safe, no API access).

    The Cloud Agent uses this to prepare posts for Local Agent review.
    """

    MAX_TWITTER_LENGTH = 280

    def create_draft(self, content: str, platform: str = "twitter",
                     hashtags: Optional[List[str]] = None,
                     media_urls: Optional[List[str]] = None,
                     scheduled_time: Optional[str] = None) -> SocialDraft:
        """Create a structured social media draft.

        Args:
            content: Post content text.
            platform: Target platform (twitter, linkedin, etc.).
            hashtags: Optional list of hashtags.
            media_urls: Optional list of media URLs.
            scheduled_time: Optional ISO timestamp for scheduling.

        Returns:
            SocialDraft object.
        """
        draft_id = f"SOCIAL-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{hashlib.md5(content.encode()).hexdigest()[:6]}"

        if platform == "twitter" and len(content) > self.MAX_TWITTER_LENGTH:
            content = content[:self.MAX_TWITTER_LENGTH - 3] + "..."
            logger.warning(f"Tweet truncated to {self.MAX_TWITTER_LENGTH} chars")

        return SocialDraft(
            draft_id=draft_id,
            platform=platform,
            content=content,
            hashtags=hashtags or [],
            media_urls=media_urls or [],
            scheduled_time=scheduled_time,
        )

    def draft_to_json(self, draft: SocialDraft) -> str:
        """Serialize a draft to JSON for storage."""
        return json.dumps({
            "draft_id": draft.draft_id,
            "platform": draft.platform,
            "content": draft.content,
            "hashtags": draft.hashtags,
            "media_urls": draft.media_urls,
            "scheduled_time": draft.scheduled_time,
            "created_at": draft.created_at,
            "status": draft.status,
        }, indent=2)

    def save_draft(self, draft: SocialDraft, vault_path: str) -> str:
        """Save a draft to the Needs_Action/social/ directory.

        Returns:
            Path to saved draft file.
        """
        needs_dir = Path(vault_path) / "Platinum" / "Needs_Action" / "social"
        needs_dir.mkdir(parents=True, exist_ok=True)
        file_path = needs_dir / f"{draft.draft_id}.json"
        file_path.write_text(self.draft_to_json(draft), encoding="utf-8")
        logger.info(f"Social draft saved: {draft.draft_id}")
        return str(file_path)


class SocialPoster:
    """Posts to Twitter/X via API - Local agent ONLY.

    Cloud agent NEVER has access to API keys.
    SecretGuard enforced: only Local agent can instantiate.
    """

    def __init__(self, settings):
        self.api_key = settings.TWITTER_API_KEY
        self.api_secret = settings.TWITTER_API_SECRET
        self.access_token = settings.TWITTER_ACCESS_TOKEN
        self.access_secret = settings.TWITTER_ACCESS_SECRET
        self.agent_role = settings.AGENT_ROLE

        if self.agent_role == "cloud":
            raise PermissionError(
                "Cloud agent is not permitted to post to social media. "
                "Only the Local agent has social media post authority."
            )

    @property
    def is_configured(self) -> bool:
        return bool(
            self.api_key and self.api_secret
            and self.access_token and self.access_secret
        )

    def post(self, content: str) -> bool:
        """Post a tweet via Twitter/X API.

        Args:
            content: Tweet text (max 280 chars).

        Returns:
            True if posted successfully, False otherwise.
        """
        if not self.is_configured:
            logger.warning("Twitter API credentials not configured")
            return False

        try:
            # Twitter API v2 post
            import requests
            from requests_oauthlib import OAuth1

            auth = OAuth1(
                self.api_key, self.api_secret,
                self.access_token, self.access_secret,
            )
            response = requests.post(
                "https://api.twitter.com/2/tweets",
                json={"text": content[:280]},
                auth=auth,
                timeout=30,
            )
            if response.status_code in (200, 201):
                logger.info(f"Tweet posted: {content[:50]}...")
                return True
            else:
                logger.error(f"Twitter API error {response.status_code}: {response.text}")
                return False
        except ImportError:
            logger.error("requests-oauthlib not installed; cannot post to Twitter")
            return False
        except Exception as e:
            logger.error(f"Failed to post tweet: {e}")
            return False

    def post_draft(self, draft: SocialDraft) -> bool:
        """Post a SocialDraft to the appropriate platform."""
        if draft.platform != "twitter":
            logger.warning(f"Platform '{draft.platform}' not yet supported")
            return False
        return self.post(draft.content)
