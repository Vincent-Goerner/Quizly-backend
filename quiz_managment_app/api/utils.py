import os
import yt_dlp

from dotenv import load_dotenv
from google import genai


load_dotenv()

def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    return genai.Client(api_key=api_key)


class MediaQuizProcessor:
    def __init__(self):
        self.media_directory = "media"
        self.audio_filename = "audio_track"
        self.transcript_filename = "transcribed_text"
        self.output_filename = "generated_text"
        os.makedirs(self.media_directory, exist_ok=True)

    def fetch_audio_from_url(self, url):
        output_path = os.path.join(self.media_directory, self.audio_filename)

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_path,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                    "preferredquality": "0",
                }
            ],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as audio:
            audio.extract_info(url, download=True)

    def transcribe_with_whisper(self):
        import whisper
        model = whisper.load_model("small", device="cpu")

        audio_file = self._build_path(self.audio_filename + ".wav")
        result = model.transcribe(audio_file)

        self._remove_file(audio_file)

        self._write_file(self.transcript_filename + ".txt", result["text"])

    def generate_quiz_with_gemini(self):
        client = get_client()
        transcript = self._read_file(self.transcript_filename + ".txt")

        prompt = f"""
            Create a quiz based on the following transcript.
            ...
            transcript:
            {transcript[:10000]}
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        self._write_file(self.output_filename + ".txt", response.text)

    def clean_output_text(self):
        filename = self.output_filename + ".txt"
        content = self._read_file(filename)

        content = self._remove_markdown_fencing(content.strip())
        self._write_file(filename, content)

        return content

    def _remove_markdown_fencing(self, text):
        if text.startswith("```json"):
            text = text[len("```json"):]
        if text.endswith("```"):
            text = text[:-3]
        return text

    def _build_path(self, name):
        return os.path.join(self.media_directory, name)

    def _read_file(self, filename):
        with open(self._build_path(filename), "r", encoding="utf-8") as f:
            return f.read()

    def _write_file(self, filename, content):
        with open(self._build_path(filename), "w", encoding="utf-8") as f:
            f.write(content)

    def _remove_file(self, filename):
        if os.path.exists(filename):
            os.remove(filename)

    def delete_transcript(self):
        self._remove_file(self._build_path(self.transcript_filename + ".txt"))

    def delete_generated_quiz(self):
        self._remove_file(self._build_path(self.output_filename + ".txt"))