"""Microphone input and spoken output for the voice assistant."""

import asyncio
import os
import tempfile
import time
from pathlib import Path

import edge_tts
import pygame
import speech_recognition as sr
from dotenv import load_dotenv

load_dotenv()


class SpeechProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognition_language = os.getenv("SPEECH_RECOGNITION_LANGUAGE", "en-US")
        self.tts_voice = os.getenv("TTS_VOICE", "en-US-AriaNeural")
        self.tts_rate = os.getenv("TTS_RATE", "+0%")

        # Initialize the audio mixer once and reuse it for every response.
        pygame.mixer.init()

    def listen(self):
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Listening...")
                try:
                    audio = self.recognizer.listen(
                        source,
                        timeout=float(os.getenv("SPEECH_TIMEOUT", "5")),
                    )
                except sr.WaitTimeoutError:
                    print("Listening timed out while waiting for speech.")
                    return ""
        except (OSError, AttributeError) as error:
            print(f"Microphone unavailable: {error}")
            return ""

        try:
            print("Recognizing...")
            text = self.recognizer.recognize_google(
                audio,
                language=self.recognition_language,
            )
            print(f"Recognized: {text}")
            return text
        except sr.UnknownValueError:
            print("Could not understand audio.")
        except sr.RequestError as error:
            print(f"Speech recognition service error: {error}")
        return ""

    def speak(self, text):
        if not text:
            return

        audio_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as audio_file:
                audio_path = Path(audio_file.name)

            asyncio.run(
                edge_tts.Communicate(
                    text,
                    voice=self.tts_voice,
                    rate=self.tts_rate,
                ).save(str(audio_path))
            )

            pygame.mixer.music.load(str(audio_path))
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.05)
            pygame.mixer.music.unload()
        except Exception as error:
            print(f"Could not speak response: {error}")
        finally:
            if audio_path is not None:
                audio_path.unlink(missing_ok=True)
