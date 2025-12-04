from rest_framework import serializers
from django.contrib.auth.models import User
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
from quiz_managment_app.models import Question, Quiz
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

        video_id = self.extract_video_id(parsed)
        if not video_id:
            raise serializers.ValidationError("No video ID found in URL.")

        self.validate_video_duration(video_id)

        return self.build_clean_url(video_id)

    def extract_video_id(self, parsed):
        if parsed.netloc == "youtu.be":
            return parsed.path.lstrip("/")

        query_params = parse_qs(parsed.query)
        video_id_list = query_params.get("v")
        return video_id_list[0] if video_id_list else None

    def validate_video_duration(self, video_id):
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

    def build_clean_url(self, video_id):
        query = urlencode({"v": video_id})
        return urlunparse(
            ("https", "www.youtube.com", "/watch", "", query, "")
        )

    def create(self, validated_data):
        user = self.context["request"].user 
        return Quiz.objects.create(
            title="Generated Quiz",
            owner=user,
            source_url=validated_data["url"]
        )

    
class QuestionSerializer(serializers.ModelSerializer):

    question_options = serializers.ListField(
        child=serializers.CharField(max_length=255),
        allow_empty=False
    )

    class Meta:
        model = Question
        fields = [
            "id",
            "question_title",
            "question_options",
            "answer",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_question_options(self, value):
        if len(value) != 4:
            raise serializers.ValidationError(
                "Each question must have exactly 4 answer options."
            )
        return value
    

class QuizSerializer(serializers.ModelSerializer):

    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "updated_at",
            "video_url",
            "questions",
        ]
        read_only_fields = fields


class QuizPatchSerializer(serializers.ModelSerializer):

    title = serializers.CharField(required=False, max_length=255)
    description = serializers.CharField(required=False, max_length=255)

    class Meta:
        model = Quiz
        fields = [
            "title",
            "description",
            "created_at",
            "updated_at",
            "video_url",
            "questions",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "video_url", "questions"]