"""Lesson, retry-based practice, and mock speaking sessions."""

import json
from datetime import datetime, timezone
from pathlib import Path

from document_library import DocumentLibrary
from ollama_agent import OllamaAgent


MODE_GUIDANCE = {
    "lesson": (
        "Teach one beginner-friendly concept at a time. Explain it simply, give a few "
        "short examples, then ask one understanding question. Base grammar teaching "
        "on the supplied material when available."
    ),
    "practice": (
        "Run a one-question-at-a-time practice session. Ask the student to answer in "
        "English. Give a fair chance to retry: after an incorrect or incomplete answer, "
        "kindly explain one issue and give a small hint without revealing the full answer. "
        "Allow up to two attempts before showing a sample answer. If the student says "
        "hint/help, give a hint; if they explicitly ask for the answer, show it. Accept "
        "valid alternative answers and explain corrections simply. Ask the next question "
        "only after reviewing the current answer."
    ),
    "mock": (
        "Run a realistic, supportive spoken roleplay for a beginner. Play the other role "
        "and ask one short question at a time. Let the student finish, respond naturally, "
        "then give brief feedback on one useful language improvement. If they get stuck, "
        "offer a phrase starter or sample answer when requested. Keep the conversation moving."
    ),
}


class EnglishTeacher:
    def __init__(self, agent=None, library=None, progress_path=None):
        self.agent = agent or OllamaAgent()
        self.library = library or DocumentLibrary()
        self.progress_path = (
            Path(progress_path)
            if progress_path
            else Path(__file__).parent / "data" / "progress.json"
        )
        self.mode = None
        self.topic = ""
        self.active = False

    @staticmethod
    def _base_prompt(mode, topic):
        return (
            "You are a patient, encouraging English teacher for absolute beginners. "
            "Use short, plain sentences suitable for speech. Do not shame the student. "
            "Correct gently and focus on meaning as well as grammar; open-ended speaking "
            "can have many correct answers. Keep each turn concise. "
            f"Current session type: {mode}. Topic or scenario: {topic or 'choose a useful beginner topic'}. "
            f"Session instructions: {MODE_GUIDANCE[mode]} "
            "Use the supplied reference excerpts for claims about the books, and mention "
            "the PDF title and page when useful. Do not pretend a source says something "
            "that is not in its excerpts. If the excerpts do not cover the question, say "
            "so briefly, then clearly label any general English guidance as your own explanation."
        )

    def _reference_context(self, query):
        excerpts = self.library.search(query)
        return self.library.format_excerpts(excerpts)

    def start_session(self, mode, topic=""):
        if mode not in MODE_GUIDANCE:
            raise ValueError(f"Unknown teacher session mode: {mode}")
        self.mode = mode
        self.topic = topic.strip() or "beginner English grammar and conversation"
        self.active = True
        self.agent.reset_conversation(self._base_prompt(mode, self.topic))
        request = (
            f"Begin a {mode} session about {self.topic}. Use the references below if relevant. "
            "For practice or mock mode, start by asking one question and then wait for the student."
        )
        return self.agent.get_response(
            request,
            system_prompt=self._base_prompt(mode, self.topic)
            + "\n\nReference excerpts:\n"
            + self._reference_context(self.topic),
        )

    def reply(self, student_text):
        if not self.active:
            return "Choose lesson, practice, or mock to start a session."
        query = f"{self.topic} {student_text}"
        prompt = (
            self._base_prompt(self.mode, self.topic)
            + "\n\nReference excerpts:\n"
            + self._reference_context(query)
        )
        return self.agent.get_response(student_text, system_prompt=prompt)

    def save_progress(self):
        self.progress_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            progress = json.loads(self.progress_path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            progress = {"sessions": 0, "by_mode": {}, "topics": {}, "recent_sessions": []}

        progress["sessions"] = progress.get("sessions", 0) + 1
        progress.setdefault("by_mode", {})[self.mode] = (
            progress.setdefault("by_mode", {}).get(self.mode, 0) + 1
        )
        progress.setdefault("topics", {})[self.topic] = (
            progress.setdefault("topics", {}).get(self.topic, 0) + 1
        )
        recent = progress.setdefault("recent_sessions", [])
        recent.append(
            {
                "mode": self.mode,
                "topic": self.topic,
                "started_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        progress["recent_sessions"] = recent[-20:]
        self.progress_path.write_text(json.dumps(progress, indent=2), encoding="utf-8")

    def progress_summary(self):
        try:
            progress = json.loads(self.progress_path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            return "There is no saved practice progress yet."
        sessions = progress.get("sessions", 0)
        topics = progress.get("topics", {})
        if not sessions:
            return "There is no saved practice progress yet."
        topic_summary = ", ".join(
            f"{topic} ({count})"
            for topic, count in sorted(topics.items(), key=lambda item: item[1], reverse=True)[:5]
        )
        return f"You have started {sessions} lesson or practice sessions. Topics practiced: {topic_summary}."

    def end_session(self):
        self.active = False
        self.mode = None
        self.topic = ""
        self.agent.reset_conversation()
