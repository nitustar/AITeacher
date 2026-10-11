"""Ollama chat client with short-lived, in-memory conversation history."""

import os

import ollama
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = (
    "You are a voice assistant. Answer directly in simple, concise language that is "
    "comfortable to hear aloud. Keep responses under about 30 seconds unless the "
    "user asks for detail. Do not introduce yourself unless asked."
)


class OllamaAgent:
    def __init__(self, model_name=None, host=None, api_key=None, max_history_turns=None):
        self.model_name = model_name or os.getenv("OLLAMA_MODEL", "gemma4:31b-cloud")
        self.host = host or os.getenv("OLLAMA_HOST", "https://ollama.com")
        self.api_key = api_key if api_key is not None else os.getenv("OLLAMA_API_KEY")
        self.max_history_turns = max(
            1,
            int(max_history_turns or os.getenv("CONVERSATION_HISTORY_TURNS", "10")),
        )

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        self.client = ollama.Client(host=self.host, headers=headers or None)
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    def create_chat_completion(self, messages):
        try:
            response = self.client.chat(model=self.model_name, messages=messages)
            return response.message.content
        except Exception as error:
            print(f"LLM generation failed: {error}")
            return "Sorry, I couldn't reach the language model. Please check your Ollama settings and try again."

    def get_response(self, command, system_prompt=None):
        if system_prompt:
            self.messages[0] = {"role": "system", "content": system_prompt}
        self.messages.append({"role": "user", "content": command})
        assistant_reply = self.create_chat_completion(self.messages)

        # Keep the system prompt plus the latest N user/assistant turns in memory.
        self.messages.append({"role": "assistant", "content": assistant_reply})
        max_messages = self.max_history_turns * 2
        self.messages = [self.messages[0]] + self.messages[-max_messages:]
        return assistant_reply

    def reset_conversation(self, system_prompt=SYSTEM_PROMPT):
        """Forget prior turns and optionally set a different system prompt."""
        self.messages = [{"role": "system", "content": system_prompt}]
