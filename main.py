import string

from ollama_agent import OllamaAgent
from speech_processing import SpeechProcessor


class MainApp:
    def __init__(self):
        self.speech_processor = SpeechProcessor()
        self.ollama_agent = OllamaAgent()

    def run(self):
        print("Voice assistant ready. Say 'exit' or 'quit' to stop.")
        while True:
            command = self.speech_processor.listen()
            normalized_command = command.strip().casefold().rstrip(string.punctuation)

            if normalized_command in {"exit", "quit", "stop", "goodbye"}:
                self.speech_processor.speak("Goodbye!")
                print("Exiting...")
                break

            if not command:
                continue

            answer = self.ollama_agent.get_response(command)
            self.speech_processor.speak(answer)
            print(f"Assistant: {answer}")


if __name__ == "__main__":
    MainApp().run()
