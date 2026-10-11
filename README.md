# Voice Assistant and English Teacher

A Python voice assistant that listens to speech, sends it to an Ollama model, and speaks the response. It also has an English teacher mode with lessons, guided practice, and mock conversations based on PDFs in `docs/`.

## Features

- Voice input through `SpeechRecognition` and Google's online speech recognition service.
- Spoken responses using Edge neural text-to-speech and `pygame` audio playback.
- Regular assistant chat with recent conversation context.
- English lessons, beginner practice with retries and hints, and spoken roleplay sessions.
- Search over PDF text in `docs/`, with relevant excerpts and source page references supplied to the teacher.
- A small local progress summary recording session counts and topics.

## Requirements

- Python 3.10 or newer
- A working microphone and speakers
- Internet access for speech recognition and Edge neural text-to-speech
- Ollama Cloud credentials or a local Ollama server and an available model

On macOS, grant microphone access to the terminal or editor running the app. Installing `PyAudio` may require PortAudio. On Linux, audio playback may require system SDL/audio libraries for `pygame`.

## Setup

Create and activate a virtual environment, then install the dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Copy the sample settings and edit `.env`:

```bash
cp .env.example .env
```

For Ollama Cloud, configure `OLLAMA_HOST`, `OLLAMA_MODEL`, and `OLLAMA_API_KEY`. For a local Ollama server, set `OLLAMA_HOST=http://localhost:11434`, select an installed model, and leave the API key blank. `.env` is excluded by `.gitignore`; do not commit API keys.

Put text-based, searchable PDF learning materials in `docs/`. The app extracts and searches them locally, then includes matching page excerpts in prompts sent to your configured Ollama server. If you use Ollama Cloud, those excerpts are sent to that service. Scanned/image-only PDFs need OCR before the app can search them. Keep only materials you are permitted to use.

## Run

```bash
python main.py
```

Say `teacher mode` to open the English teacher menu. You can also start a session directly from regular chat by saying a session command.

### Teacher voice commands

| Say | What happens |
| --- | --- |
| `lesson on present tense` | Starts a short guided lesson on the topic. |
| `practice on articles` | Starts question-by-question practice. The teacher gives hints and retry opportunities before showing a sample answer. |
| `mock ordering food` | Starts a roleplay in the requested situation. |
| `hint` or `help` | Ask for a hint during practice or mock conversation. |
| `show answer` | Ask to hear a sample answer. |
| `repeat question` | Ask the teacher to repeat or rephrase. |
| `progress` | Hear how many sessions were started and which topics were practiced. |
| `end session` or `back to menu` | End the current session and return to the teacher menu. |
| `back` or `assistant` | Return to regular assistant chat. |
| `exit` | Close the application. |

In practice, the teacher tries to let the student answer before revealing a sample answer. For open-ended speaking and mock conversations, it accepts different valid answers and focuses on a small number of helpful corrections at a time.

## Configuration

See `.env.example` for the full list. Main settings:

| Variable | Default | Purpose |
| --- | --- | --- |
| `OLLAMA_HOST` | `https://ollama.com` | Ollama server URL. |
| `OLLAMA_MODEL` | `gemma4:31b-cloud` | Model used for assistant and teacher responses. |
| `OLLAMA_API_KEY` | unset | Cloud API key; not needed for local Ollama. |
| `CONVERSATION_HISTORY_TURNS` | `10` | Recent chat exchanges retained in memory. |
| `SPEECH_RECOGNITION_LANGUAGE` | `en-US` | Language code used for speech recognition. |
| `SPEECH_TIMEOUT` | `5` | Seconds to wait for a spoken phrase to begin. |
| `TTS_VOICE` | `en-US-AriaNeural` | Edge neural voice name. |
| `TTS_RATE` | `+0%` | Speech rate adjustment, such as `-10%` or `+10%`. |

Teacher progress is stored in `data/progress.json` and excluded from version control. Conversation history is held in memory and resets when the app closes.

## Current limitations

- Speech recognition and spoken output both require internet access.
- PDF search uses text extracted from pages. Scanned PDFs require OCR, and search is page-based rather than a full chapter index.
- Progress currently records sessions and topics, not a detailed score or pronunciation assessment. Speech recognition transcribes words but does not reliably grade pronunciation.
