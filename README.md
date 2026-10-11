# Voice Assistant with Ollama

A small Python voice assistant that listens through your microphone, turns speech into text, sends the text to an Ollama model, and reads the model's answer aloud.

## How it works

1. `SpeechRecognition` captures microphone audio and uses Google's speech recognition service to transcribe it.
2. `OllamaAgent` sends the transcript and recent conversation to the configured Ollama model.
3. Microsoft Edge's neural text-to-speech service creates speech, and `pygame` plays it through the computer's audio output.

Conversation context is kept in memory while the program runs. The latest exchanges are limited by `CONVERSATION_HISTORY_TURNS`; restarting the app clears the history.

## Requirements

- Python 3.10 or newer
- A working microphone and speakers
- Internet access for Google's speech recognition service
- Internet access for Edge neural text-to-speech
- Either an Ollama Cloud account and API key, or a local Ollama installation with the chosen model available

On macOS, you may need to grant microphone access to the terminal or editor running the app. `PyAudio` may also require PortAudio to be installed before it can be installed with pip.

## Setup

Create and activate a virtual environment, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Create your local configuration file:

```bash
cp .env.example .env
```

Edit `.env` and choose one Ollama configuration:

### Ollama Cloud

Set `OLLAMA_HOST` to `https://ollama.com`, select a cloud model in `OLLAMA_MODEL`, and set `OLLAMA_API_KEY` to your Ollama API key.

### Local Ollama

Set `OLLAMA_HOST=http://localhost:11434`, choose a model installed locally, and leave `OLLAMA_API_KEY` blank. For example, you can use `OLLAMA_MODEL=llama3.2` if that model is available in your Ollama installation.

Never commit `.env`; it may contain a private API key. The repository's `.gitignore` excludes it.

## Run

```bash
python main.py
```

Speak after the app prints `Listening...`. Say “exit”, “quit”, “stop”, or “goodbye” to close the app.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `OLLAMA_HOST` | `https://ollama.com` | Ollama server URL; use `http://localhost:11434` for a local server. |
| `OLLAMA_MODEL` | `gemma4:31b-cloud` | Model name sent to Ollama. |
| `OLLAMA_API_KEY` | unset | Optional for local Ollama; required by Ollama Cloud. |
| `CONVERSATION_HISTORY_TURNS` | `10` | Number of recent user/assistant exchanges retained. |
| `SPEECH_RECOGNITION_LANGUAGE` | `en-US` | Language code passed to Google's speech recognition service. |
| `SPEECH_TIMEOUT` | `5` | Seconds to wait for speech to begin. |
| `TTS_VOICE` | `en-US-AriaNeural` | Edge neural voice name, such as `en-US-GuyNeural`. |
| `TTS_RATE` | `+0%` | Speech speed adjustment, for example `+10%` or `-10%`. |

## Notes

- Speech transcription currently relies on Google's online service, so it is not offline and audio recognition requires network access.
- Spoken output uses Edge's online neural TTS service. It provides more natural voices and works across operating systems, but needs internet access.
- Conversation history is held only in the running process and is not saved to disk.
