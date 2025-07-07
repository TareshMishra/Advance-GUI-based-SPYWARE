import sounddevice as sd
import numpy as np
from pathlib import Path
from datetime import datetime
from utils.logger import setup_logging
import wave
import os

class AudioRecorder:
    """Class to record audio from the default microphone."""
    
    def __init__(self):
        self.fs = 44100  # Sample rate
        self.channels = 2  # Stereo
        self.recording = None
        self.is_recording_flag = False
        self.stream = None
        self.audio_file = Path(__file__).parent.parent / 'data' / 'audio_recording.wav'
        self.audio_file.parent.mkdir(exist_ok=True)
        self.logger = setup_logging('audio_recorder')
        
    def callback(self, indata, frames, time, status):
        """Callback function for audio stream."""
        if status:
            self.logger.warning(f"Audio stream status: {status}")
        self.recording.append(indata.copy())

    def start(self, duration=None):
        """Start audio recording."""
        if not self.is_recording_flag:
            try:
                self.recording = []
                self.stream = sd.InputStream(
                    samplerate=self.fs,
                    channels=self.channels,
                    callback=self.callback,
                    dtype='float32'
                )
                self.stream.start()
                self.is_recording_flag = True
                self.logger.info("Audio recording started")
                
                if duration is not None:
                    import time
                    time.sleep(duration)
                    self.stop()
                    
            except Exception as e:
                self.logger.error(f"Error starting audio recording: {e}")
                raise

    def stop(self):
        """Stop audio recording and save to file."""
        if self.is_recording_flag and self.stream:
            try:
                self.stream.stop()
                self.stream.close()
                self.is_recording_flag = False
                
                if self.recording:
                    # Convert recording to numpy array
                    audio_data = np.concatenate(self.recording, axis=0)
                    
                    # Save as WAV file
                    self.save_to_file(audio_data)
                    self.logger.info(f"Audio recording saved to {self.audio_file}")
                else:
                    self.logger.warning("Audio recording stopped but no data was captured")
                    
            except Exception as e:
                self.logger.error(f"Error stopping audio recording: {e}")
                raise

    def save_to_file(self, audio_data):
        """Save audio data to WAV file."""
        try:
            # Scale to 16-bit PCM range
            scaled = np.int16(audio_data * 32767)
            
            with wave.open(str(self.audio_file), 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 2 bytes for 16-bit samples
                wf.setframerate(self.fs)
                wf.writeframes(scaled.tobytes())
                
        except Exception as e:
            self.logger.error(f"Error saving audio file: {e}")
            raise

    def is_recording(self):
        """Check if recording is in progress."""
        return self.is_recording_flag

    def get_recording_duration(self):
        """Get duration of current recording in seconds."""
        if self.recording:
            return len(self.recording) * len(self.recording[0]) / self.fs
        return 0