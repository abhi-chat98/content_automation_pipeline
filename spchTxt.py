
import whisper
import threading
import queue
import time
import wave
import pyaudio
import tempfile
import os

class SpeechToText:
    def __init__(self):
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.text_result = ""
        self.thread = None
        self.model = whisper.load_model("base")

        # Audio settings
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.RECORD_SECONDS = 5  # You can tweak this for responsiveness
        self.p = pyaudio.PyAudio()

    def start_listening(self):
        if not self.is_listening:
            self.is_listening = True
            self.text_result = ""
            self.thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.thread.start()
            print("Started listening...")

    def stop_listening(self):
        self.is_listening = False
        print("Stopped listening...")

    def _listen_loop(self):
        print("Listening for audio input...")
        while self.is_listening:
            frames = []
            stream = self.p.open(format=self.FORMAT,
                                 channels=self.CHANNELS,
                                 rate=self.RATE,
                                 input=True,
                                 frames_per_buffer=self.CHUNK)

            print("Recording...")
            for _ in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
                data = stream.read(self.CHUNK)
                frames.append(data)

            stream.stop_stream()
            stream.close()
            print("Finished recording.")
            
            self.audio_queue.put(b"".join(frames))
            self.process_audio()

    def process_audio(self):
        while not self.audio_queue.empty():
            audio_data = self.audio_queue.get()
            try:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                    temp_wav_path = temp_wav.name
                    with wave.open(temp_wav, 'wb') as wf:
                        wf.setnchannels(self.CHANNELS)
                        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
                        wf.setframerate(self.RATE)
                        wf.writeframes(audio_data)

                print("Transcribing using Whisper...")
                result = self.model.transcribe(temp_wav_path)
                text = result["text"].strip()
                print(f"Recognized text: {text}")
                self.text_result += text + " "

                os.unlink(temp_wav_path)
            except Exception as e:
                print(f"Error in Whisper transcription: {e}")

    def get_text(self, clear=True):
        result = self.text_result.strip()
        if clear:
            self.text_result = ""
        return result





