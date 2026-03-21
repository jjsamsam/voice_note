"""
Audio Utility Functions
File format detection, conversion, and ffmpeg helpers.
Supports bundled ffmpeg when running as a PyInstaller executable.
"""

import os
import sys
import shutil
from pydub import AudioSegment
from pydub.utils import which


def get_bundled_ffmpeg_dir():
    """
    Get the path to the bundled ffmpeg directory.
    When running as a PyInstaller bundle, ffmpeg is in the _MEIPASS temp dir.
    """
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        base_path = sys._MEIPASS
        ffmpeg_dir = os.path.join(base_path, "ffmpeg")
        if os.path.isdir(ffmpeg_dir):
            return ffmpeg_dir
    return None


def setup_ffmpeg():
    """
    Configure pydub to use bundled ffmpeg if available.
    Call this once at app startup.
    """
    bundled_dir = get_bundled_ffmpeg_dir()
    if bundled_dir:
        # Set pydub to use bundled ffmpeg
        ffmpeg_path = os.path.join(bundled_dir, "ffmpeg")
        ffprobe_path = os.path.join(bundled_dir, "ffprobe")

        if sys.platform == "win32":
            ffmpeg_path += ".exe"
            ffprobe_path += ".exe"

        if os.path.exists(ffmpeg_path):
            AudioSegment.converter = ffmpeg_path
        if os.path.exists(ffprobe_path):
            AudioSegment.ffprobe = ffprobe_path

        # Also add to PATH for whisper
        os.environ["PATH"] = bundled_dir + os.pathsep + os.environ.get("PATH", "")
        return True

    return check_ffmpeg()


def get_supported_formats():
    """Return list of supported audio file formats."""
    return [
        "wav", "mp3", "mp4", "m4a", "flac",
        "ogg", "wma", "aac", "webm",
    ]


def get_file_filter():
    """Return a file dialog filter string for supported audio formats."""
    formats = get_supported_formats()
    extensions = " ".join(f"*.{fmt}" for fmt in formats)
    return f"Audio Files ({extensions});;All Files (*.*)"


def get_audio_info(file_path):
    """
    Get basic info about an audio file.

    Returns:
        dict with keys: duration, channels, sample_rate, format
    """
    try:
        audio = AudioSegment.from_file(file_path)
        return {
            "duration": len(audio) / 1000.0,  # seconds
            "channels": audio.channels,
            "sample_rate": audio.frame_rate,
            "format": os.path.splitext(file_path)[1].lstrip(".").lower(),
        }
    except Exception as e:
        return {"error": str(e)}


def convert_audio(input_path, output_path, output_format=None):
    """
    Convert audio file to a different format.

    Args:
        input_path: Source audio file path
        output_path: Destination file path
        output_format: Target format (inferred from output_path if None)
    """
    if output_format is None:
        output_format = os.path.splitext(output_path)[1].lstrip(".").lower()

    audio = AudioSegment.from_file(input_path)
    audio.export(output_path, format=output_format)


def check_ffmpeg():
    """Check if ffmpeg is available on the system."""
    return shutil.which("ffmpeg") is not None


def format_duration(seconds):
    """Format duration in seconds to MM:SS or HH:MM:SS string."""
    seconds = int(seconds)
    if seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
