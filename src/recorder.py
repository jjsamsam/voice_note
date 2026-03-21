"""
Audio Recorder Module
Records audio from the microphone and saves to various formats.
"""

import os
import threading
import tempfile
import numpy as np
import sounddevice as sd
import soundfile as sf
from pydub import AudioSegment


class AudioRecorder:
    """Records audio from the default microphone."""

    def __init__(self, sample_rate=44100, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.is_recording = False
        self._frames = []
        self._stream = None
        self._lock = threading.Lock()

    def _audio_callback(self, indata, frames, time_info, status):
        """Callback for audio stream."""
        if status:
            print(f"Recording status: {status}")
        with self._lock:
            self._frames.append(indata.copy())

    def start(self):
        """Start recording audio."""
        if self.is_recording:
            return
        self._frames = []
        self.is_recording = True
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
            callback=self._audio_callback,
        )
        self._stream.start()

    def stop(self):
        """Stop recording audio and return the recorded data."""
        if not self.is_recording:
            return None
        self.is_recording = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        with self._lock:
            if not self._frames:
                return None
            audio_data = np.concatenate(self._frames, axis=0)
            self._frames = []
        return audio_data

    def save(self, audio_data, file_path, output_format="wav"):
        """
        Save recorded audio data to a file.

        Args:
            audio_data: numpy array of audio data
            file_path: output file path
            output_format: 'wav', 'mp3', or 'mp4' (m4a)
        """
        if audio_data is None or len(audio_data) == 0:
            raise ValueError("No audio data to save")

        # Always save as WAV first
        temp_wav = None
        try:
            if output_format.lower() == "wav":
                sf.write(file_path, audio_data, self.sample_rate)
            else:
                # Save temporary WAV, then convert
                temp_fd, temp_wav = tempfile.mkstemp(suffix=".wav")
                os.close(temp_fd)
                sf.write(temp_wav, audio_data, self.sample_rate)

                audio_segment = AudioSegment.from_wav(temp_wav)

                if output_format.lower() == "mp3":
                    audio_segment.export(file_path, format="mp3")
                elif output_format.lower() in ("mp4", "m4a"):
                    audio_segment.export(file_path, format="mp4")
                else:
                    raise ValueError(f"Unsupported format: {output_format}")
        finally:
            if temp_wav and os.path.exists(temp_wav):
                os.remove(temp_wav)

    def get_duration(self, audio_data):
        """Get the duration of audio data in seconds."""
        if audio_data is None:
            return 0.0
        return len(audio_data) / self.sample_rate

    @staticmethod
    def get_input_devices():
        """List available input audio devices."""
        devices = sd.query_devices()
        input_devices = []
        for i, dev in enumerate(devices):
            if dev["max_input_channels"] > 0:
                input_devices.append({"index": i, "name": dev["name"], "channels": dev["max_input_channels"]})
        return input_devices
