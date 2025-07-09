
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






        # Python program to translate
# speech to text and text to speech

'''
import speech_recognition as sr
import threading
import queue
import time

class SpeechToText:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.text_result = ""
        self.thread = None
        
    def start_listening(self):
        """Start listening to microphone input"""
        if not self.is_listening:
            self.is_listening = True
            self.text_result = ""
            self.thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.thread.start()
            print("Started listening...")
        
    def stop_listening(self):
        """Stop listening to microphone input"""
        if self.is_listening:
            self.is_listening = False
            if self.thread:
                self.thread.join(timeout=1)
            print("Stopped listening...")
        
    def _listen_loop(self):
        """Background thread for listening to microphone"""
        try:
            with sr.Microphone() as source:
                print("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Ready to listen!")
                
                while self.is_listening:
                    try:
                        print("Listening...")
              #          audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                        audio = self.recognizer.listen(source)
                        print("Got audio, processing...")
                        self.audio_queue.put(audio)
                    except sr.WaitTimeoutError:
                        continue
                    except Exception as e:
                        print(f"Error in listen loop: {str(e)}")
                        break
        except Exception as e:
            print(f"Error with microphone: {str(e)}")
            self.is_listening = False
            
    def process_audio(self):
        """Process any audio in the queue and return recognized text"""
        try:
            while not self.audio_queue.empty():
                audio = self.audio_queue.get()
                try:
                    print("Recognizing speech...")
                    text = self.recognizer.recognize_google(audio)
                    print(f"Recognized text: {text}")
                    self.text_result += text + " "
                except sr.UnknownValueError:
                    print("Could not understand audio")
                except sr.RequestError as e:
                    print(f"Could not request results; {str(e)}")
        except Exception as e:
            print(f"Error processing audio: {str(e)}")
            
        return self.text_result.strip()

    def get_text(self, clear=True):
        result = self.text_result.strip()
        if clear:
            self.text_result = ""
        return result

'''