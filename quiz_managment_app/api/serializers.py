from rest_framework import serializers
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
import yt_dlp


class YTURLSerializer(serializers.Serializer):

    url = serializers.CharField(max_length=255)

    VALID_DOMAINS = {"www.youtube.com", "youtube.com", "m.youtube.com", "youtu.be"}
    MAX_DURATION = 15 * 60

    def validate_url(self, url):
        if not url:
            raise serializers.ValidationError("URL cannot be empty.")

        parsed = urlparse(url)

        if parsed.netloc not in self.VALID_DOMAINS:
            raise serializers.ValidationError("Invalid YouTube URL domain.")

        video_id = self._extract_video_id(parsed)
        if not video_id:
            raise serializers.ValidationError("No video ID found in URL.")

        self._validate_video_duration(video_id)

        return self._build_clean_url(video_id)

    def _extract_video_id(self, parsed):
        if parsed.netloc == "youtu.be":
            return parsed.path.lstrip("/")

        query_params = parse_qs(parsed.query)
        video_id_list = query_params.get("v")
        return video_id_list[0] if video_id_list else None

    def _validate_video_duration(self, video_id):
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "skip_download": True,
            "no_warnings": True,
        }

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

        duration = info.get("duration")
        if duration is None:
            raise serializers.ValidationError(
                "The length of the video could not be read."
            )

        if duration > self.MAX_DURATION:
            raise serializers.ValidationError(
                "Video is longer than 15 minutes."
            )

    def _build_clean_url(self, video_id):
        query = urlencode({"v": video_id})
        return urlunparse(
            ("https", "www.youtube.com", "/watch", "", query, "")
        )