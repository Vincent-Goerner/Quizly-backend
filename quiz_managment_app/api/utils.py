import os
import yt_dlp

from dotenv import load_dotenv
from google import genai


load_dotenv()

def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    return genai.Client(api_key=api_key)


class AudioQuizGenerator:
    def __init__(self):
        self.media_dir = "media"
        self.audio_name = "audio_track"
        self.transcript_name = "transcribed_text"
        self.output_name = "generated_text"
        os.makedirs(self.media_dir, exist_ok=True)

    def download_audio(self, url):
        output_path = os.path.join(self.media_dir, self.audio_name)

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

    def transcribe_whisper(self):
        import whisper
        model = whisper.load_model("small", device="cpu")

        audio_file = self._path(self.audio_name + ".wav")
        result = model.transcribe(audio_file)

        self._delete_file(audio_file)

        self._write(self.transcript_name + ".txt", result["text"])

    def generate_questions_gemini(self):
        client = get_client()
        transcript = self._read(self.transcript_name + ".txt")

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

        self._write(self.output_name + ".txt", response.text)

    def edge_cleaner_text(self):
        filename = self.output_name + ".txt"
        content = self._read(filename)

        content = self._clean_markdown(content.strip())
        self._write(filename, content)

        return content

    def _clean_markdown(self, text):
        if text.startswith("```json"):
            text = text[len("```json"):]
        if text.endswith("```"):
            text = text[:-3]
        return text

    def _path(self, name):
        return os.path.join(self.media_dir, name)

    def _read(self, filename):
        with open(self._path(filename), "r", encoding="utf-8") as f:
            return f.read()

    def _write(self, filename, content):
        with open(self._path(filename), "w", encoding="utf-8") as f:
            f.write(content)

    def _delete_file(self, filename):
        if os.path.exists(filename):
            os.remove(filename)

    def delete_transcribed_text(self):
        self._delete_file(self._path(self.transcript_name + ".txt"))

    def delete_generated_text(self):
        self._delete_file(self._path(self.output_name + ".txt"))