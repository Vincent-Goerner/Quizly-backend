import os
import yt_dlp
import re

from dotenv import load_dotenv


load_dotenv()

def get_client():
    from google import genai
    api_key = os.getenv("GEMINI_API_KEY")
    return genai.Client(api_key=api_key)


class QuizGenerator:
    def __init__(self):
        self.media_dir = "media"
        self.audio_file = "audio_track.wav"
        self.transcript_file = "transcript.txt"
        self.output_file = "quiz_output.txt"
        os.makedirs(self.media_dir, exist_ok=True)

    def fetch_audio_from_url(self, url):
        output_path = os.path.join(self.media_dir, "audio_track")

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

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)

        return self.build_path(self.audio_file)

    def transcribe_audio(self):
        import whisper
        model = whisper.load_model("small", device="cpu")
        audio_path = self.build_path(self.audio_file)
        result = model.transcribe(audio_path)
        self.remove_file(audio_path)

        text = result["text"]
        self.write_file(self.transcript_file, text)
        return text

    def generate_quiz(self):
        client = get_client()
        transcript = self.read_file(self.transcript_file)

        prompt = f"""
        Erstelle ein Quiz basierend auf folgendem Transkript.

        Gib die Antwort **AUSSCHLIESSLICH** als gültiges JSON im folgenden Format zurück.
        Keinen zusätzlichen Text, keine Erklärungen, keinen Markdown, keine ```-Codeblöcke.

        Beispiel des genauen erwarteten JSON-Formats:

        {{
        "title": "string",
        "description": "string",
        "questions": [
            {{
            "question_title": "string",
            "question_options": ["A", "B", "C", "D"],
            "answer": "string"
            }}
        ]
        }}

        Hier ist das Transkript:
        {transcript[:10000]}
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        text = response.text.strip()

        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            text = match.group(0)
        self.write_file(self.output_file, text)
        return text

    def clean_quiz_text(self):
        content = self.read_file(self.output_file)

        content = content.replace("```json", "")
        content = content.replace("```", "")

        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            content = match.group(0)

        content = content.strip()
        self.write_file(self.output_file, content)
        return content

    def build_path(self, filename):
        return os.path.join(self.media_dir, filename)

    def read_file(self, filename):
        with open(self.build_path(filename), "r", encoding="utf-8") as f:
            return f.read()

    def write_file(self, filename, content):
        with open(self.build_path(filename), "w", encoding="utf-8") as f:
            f.write(content)

    def remove_file(self, filepath):
        if os.path.exists(filepath):
            os.remove(filepath)

    def cleanup(self):
        for file in [self.audio_file, self.transcript_file, self.output_file]:
            self.remove_file(self.build_path(file))