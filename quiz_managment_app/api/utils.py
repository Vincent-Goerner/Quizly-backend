import os
import yt_dlp
import re

from dotenv import load_dotenv


load_dotenv()

def get_client():
    """
    Initializes and returns a Google Gemini API client using the
    'GEMINI_API_KEY' from environment variables.
    """
    from google import genai
    api_key = os.getenv("GEMINI_API_KEY")
    return genai.Client(api_key=api_key)


class QuizGenerator:
    """
    Class to generate quizzes from YouTube video URLs by downloading
    audio, transcribing it, and generating a quiz via an AI model.
    """
    def __init__(self):
        """
        Initializes file paths and ensures the media directory exists.
        """
        self.media_dir = "media"
        self.audio_file = "audio_track.wav"
        self.transcript_file = "transcript.txt"
        self.output_file = "quiz_output.txt"
        os.makedirs(self.media_dir, exist_ok=True)

    def fetch_audio_from_url(self, url):
        """
        Downloads audio from the provided YouTube URL as a WAV file
        using yt_dlp and returns the full file path.
        """

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
        """
        Uses the Whisper model to transcribe the audio file to text,
        removes the audio file afterward, and saves the transcript to a file.
        """
        import whisper
        model = whisper.load_model("small", device="cpu")
        audio_path = self.build_path(self.audio_file)
        result = model.transcribe(audio_path)
        self.remove_file(audio_path)

        text = result["text"]
        self.write_file(self.transcript_file, text)
        return text

    def generate_quiz(self):
        """
        Generates a quiz JSON from the transcript using the Gemini AI model.
        Saves the raw output to a file and returns it as a string.
        """
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
        """
        Cleans the quiz output file by removing any Markdown code blocks
        and extracting valid JSON, then saves the cleaned content.
        """
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
        """
        Constructs the full file path for a file inside the media directory.
        """
        return os.path.join(self.media_dir, filename)

    def read_file(self, filename):
        """
        Reads and returns the contents of a file inside the media directory.
        """
        with open(self.build_path(filename), "r", encoding="utf-8") as f:
            return f.read()

    def write_file(self, filename, content):
        """
        Writes content to a file inside the media directory.
        """
        with open(self.build_path(filename), "w", encoding="utf-8") as f:
            f.write(content)

    def remove_file(self, filepath):
        """
        Deletes a file if it exists.
        """
        if os.path.exists(filepath):
            os.remove(filepath)

    def cleanup(self):
        """
        Removes all temporary files used during quiz generation
        (audio, transcript, and output files).
        """
        for file in [self.audio_file, self.transcript_file, self.output_file]:
            self.remove_file(self.build_path(file))