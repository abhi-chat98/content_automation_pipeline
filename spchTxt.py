# Python program to translate
# speech to text and text to speech


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