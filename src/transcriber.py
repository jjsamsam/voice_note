"""
Whisper Transcription Module
Transcribes audio files to text using OpenAI's Whisper.
"""

import whisper


class WhisperTranscriber:
    """Transcribes audio files using OpenAI Whisper."""

    AVAILABLE_MODELS = ["tiny", "base", "small", "medium", "large"]

    def __init__(self, model_name="base"):
        """
        Initialize the transcriber.

        Args:
            model_name: Whisper model size (tiny/base/small/medium/large)
        """
        self.model_name = model_name
        self.model = None

    def load_model(self, model_name=None):
        """
        Load or reload the Whisper model.

        Args:
            model_name: Optional model name to switch to
        """
        if model_name:
            self.model_name = model_name
        self.model = whisper.load_model(self.model_name)

    def transcribe(self, audio_path, language=None):
        """
        Transcribe an audio file.

        Args:
            audio_path: Path to the audio file
            language: Optional language code (e.g., 'en', 'ko', 'ja')
                     If None, Whisper auto-detects the language.

        Returns:
            dict with keys:
                - text: Full transcription text
                - language: Detected/specified language
                - segments: List of segment dicts with start, end, text
        """
        if self.model is None:
            self.load_model()

        options = {}
        if language:
            options["language"] = language

        result = self.model.transcribe(str(audio_path), **options)

        segments = []
        for seg in result.get("segments", []):
            segments.append({
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip(),
            })

        return {
            "text": result["text"].strip(),
            "language": result.get("language", language or "unknown"),
            "segments": segments,
        }

    def get_model_name(self):
        """Return the current model name."""
        return self.model_name

    def is_loaded(self):
        """Check if the model is loaded."""
        return self.model is not None
