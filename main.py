import string

from english_teacher import EnglishTeacher
from ollama_agent import OllamaAgent
from speech_processing import SpeechProcessor


def normalize(text):
    return text.strip().casefold().rstrip(string.punctuation)


def parse_session_command(command):
    """Return (mode, topic) for a spoken teacher session command, if present."""
    normalized = normalize(command)
    for prefix, mode in (
        ("start lesson", "lesson"),
        ("lesson", "lesson"),
        ("start practice", "practice"),
        ("practice session", "practice"),
        ("practice", "practice"),
        ("start mock", "mock"),
        ("mock session", "mock"),
        ("mock", "mock"),
    ):
        if normalized == prefix:
            return mode, ""
        if normalized.startswith(prefix + " "):
            return mode, normalized[len(prefix):].strip()
    return None


class MainApp:
    def __init__(self):
        self.speech_processor = SpeechProcessor()
        self.ollama_agent = OllamaAgent()
        self.english_teacher = EnglishTeacher()
        self.teacher_menu = False

    def _say(self, text):
        print(text)
        self.speech_processor.speak(text)

    def _begin_teacher_session(self, mode, topic):
        opening = self.english_teacher.start_session(mode, topic)
        self.english_teacher.save_progress()
        self.teacher_menu = True
        self._say(opening)

    def _handle_teacher_command(self, command, normalized):
        if normalized in {"back", "assistant", "chat mode", "normal chat"}:
            if self.english_teacher.active:
                self.english_teacher.end_session()
            self.teacher_menu = False
            self._say("Back to assistant chat. What would you like to talk about?")
            return

        if normalized in {"progress", "my progress", "show progress"}:
            self._say(self.english_teacher.progress_summary())
            return

        session_command = parse_session_command(command)
        if session_command:
            mode, topic = session_command
            self._begin_teacher_session(mode, topic)
            return

        if normalized in {"end", "end session", "finish", "done", "back to menu"}:
            self.english_teacher.end_session()
            self._say("Session ended. Say lesson, practice, mock, progress, or back.")
            return

        if self.english_teacher.active:
            self._say(self.english_teacher.reply(command))
            return

        self._say(
            "Say lesson followed by a topic, practice followed by a topic, mock followed "
            "by a situation, progress, or back. For example, say practice on present tense."
        )

    def run(self):
        self._say(
            "Voice assistant ready. Say teacher mode for English lessons and practice, "
            "or say exit to stop. You can also say lesson, practice, or mock followed by a topic."
        )
        while True:
            command = self.speech_processor.listen()
            if not command:
                continue
            normalized = normalize(command)

            if normalized in {"exit", "quit", "stop", "goodbye"}:
                self._say("Goodbye!")
                break

            if normalized in {"teacher", "teacher mode", "english teacher", "english practice"}:
                self.teacher_menu = True
                self._say(
                    "English teacher mode. Say lesson followed by a topic, practice followed "
                    "by a topic, mock followed by a situation, progress, or back."
                )
                continue

            session_command = parse_session_command(command)
            if session_command:
                self._begin_teacher_session(*session_command)
                continue

            if self.teacher_menu:
                self._handle_teacher_command(command, normalized)
            else:
                answer = self.ollama_agent.get_response(command)
                self._say(answer)


if __name__ == "__main__":
    MainApp().run()
