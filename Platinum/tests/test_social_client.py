"""
Tests for SocialDrafter and SocialPoster.
"""

import json
import pytest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

from Platinum.src.social_client import SocialDrafter, SocialPoster, SocialDraft


@pytest.fixture
def mock_settings_local(tmp_path):
    return SimpleNamespace(
        AGENT_ROLE="local",
        TWITTER_API_KEY="key123",
        TWITTER_API_SECRET="secret123",
        TWITTER_ACCESS_TOKEN="token123",
        TWITTER_ACCESS_SECRET="tsecret123",
    )


@pytest.fixture
def mock_settings_cloud():
    return SimpleNamespace(
        AGENT_ROLE="cloud",
        TWITTER_API_KEY="",
        TWITTER_API_SECRET="",
        TWITTER_ACCESS_TOKEN="",
        TWITTER_ACCESS_SECRET="",
    )


@pytest.fixture
def mock_settings_no_creds():
    return SimpleNamespace(
        AGENT_ROLE="local",
        TWITTER_API_KEY="",
        TWITTER_API_SECRET="",
        TWITTER_ACCESS_TOKEN="",
        TWITTER_ACCESS_SECRET="",
    )


class TestSocialDrafter:

    def test_create_draft(self):
        drafter = SocialDrafter()
        draft = drafter.create_draft("Hello, world!", platform="twitter")
        assert draft.platform == "twitter"
        assert draft.content == "Hello, world!"
        assert draft.draft_id.startswith("SOCIAL-")
        assert draft.status == "draft"

    def test_create_draft_with_hashtags(self):
        drafter = SocialDrafter()
        draft = drafter.create_draft(
            "New release!",
            hashtags=["#AI", "#automation"],
        )
        assert draft.hashtags == ["#AI", "#automation"]

    def test_tweet_truncation(self):
        drafter = SocialDrafter()
        long_text = "A" * 300
        draft = drafter.create_draft(long_text, platform="twitter")
        assert len(draft.content) <= 280

    def test_no_truncation_for_other_platforms(self):
        drafter = SocialDrafter()
        long_text = "A" * 300
        draft = drafter.create_draft(long_text, platform="linkedin")
        assert len(draft.content) == 300

    def test_draft_to_json(self):
        drafter = SocialDrafter()
        draft = drafter.create_draft("Test post")
        json_str = drafter.draft_to_json(draft)
        data = json.loads(json_str)
        assert data["content"] == "Test post"
        assert data["platform"] == "twitter"

    def test_save_draft(self, tmp_path):
        drafter = SocialDrafter()
        draft = drafter.create_draft("Save me!")
        path = drafter.save_draft(draft, str(tmp_path))
        assert Path(path).exists()
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        assert data["content"] == "Save me!"

    def test_scheduled_draft(self):
        drafter = SocialDrafter()
        draft = drafter.create_draft(
            "Scheduled post",
            scheduled_time="2025-01-01T12:00:00",
        )
        assert draft.scheduled_time == "2025-01-01T12:00:00"

    def test_media_urls(self):
        drafter = SocialDrafter()
        draft = drafter.create_draft(
            "Check this out!",
            media_urls=["https://example.com/image.png"],
        )
        assert draft.media_urls == ["https://example.com/image.png"]


class TestSocialPoster:

    def test_cloud_agent_blocked(self, mock_settings_cloud):
        with pytest.raises(PermissionError, match="Cloud agent is not permitted"):
            SocialPoster(mock_settings_cloud)

    def test_local_agent_allowed(self, mock_settings_local):
        poster = SocialPoster(mock_settings_local)
        assert poster.is_configured is True

    def test_not_configured(self, mock_settings_no_creds):
        poster = SocialPoster(mock_settings_no_creds)
        assert poster.is_configured is False
        assert poster.post("test") is False

    def test_post_success(self, mock_settings_local):
        pytest.importorskip("requests_oauthlib")
        with patch("requests.post") as mock_post:
            with patch("requests_oauthlib.OAuth1"):
                mock_response = MagicMock()
                mock_response.status_code = 201
                mock_post.return_value = mock_response

                poster = SocialPoster(mock_settings_local)
                result = poster.post("Hello Twitter!")
                assert result is True

    def test_post_draft_unsupported_platform(self, mock_settings_local):
        poster = SocialPoster(mock_settings_local)
        draft = SocialDraft(
            draft_id="test",
            platform="tiktok",
            content="Hello",
        )
        assert poster.post_draft(draft) is False
