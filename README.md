# Intelligent Conversational AI Chatbot (FastAPI + LangChain + Gemini)

A context-aware chatbot API built on:
- **FastAPI** — HTTP API layer
- **LangChain (`langchain-google-genai`)** — talks to Google Gemini
- **SQLAlchemy** — persists conversations & messages (SQLite by default)
- **Pydantic** — request/response validation

## Project structure
```
chatbot_project/
├── app/
│   ├── __init__.py
│   ├── database.py      # SQLAlchemy engine/session
│   ├── models.py        # Conversation, Message ORM tables
│   ├── schemas.py        # Pydantic request/response models
│   ├── llm_service.py   # LangChain + Gemini call, builds context from history
│   └── main.py           # FastAPI app & routes
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and add your key (same variable name your
   test script used):
   ```
   GEMINI=your-gemini-api-key-here
   ```
   Optional overrides in `.env`:
   ```
   GEMINI_MODEL=gemini-3.6-flash
   DATABASE_URL=sqlite:///./chatbot.db
   ```

## Run

```bash
uvicorn app.main:app --reload
```

The API is now at `http://127.0.0.1:8000`. Interactive docs at
`http://127.0.0.1:8000/docs`.

## Endpoints

| Method | Path                        | Description                          |
|--------|-----------------------------|---------------------------------------|
| POST   | `/chat`                     | Send a message, get a reply           |
| GET    | `/conversations`            | List all conversations                |
| GET    | `/conversations/{id}`       | Get one conversation + full history   |
| DELETE | `/conversations/{id}`       | Delete a conversation                 |

### Start a new conversation
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hi, my name is Sam."}'
```
Response:
```json
{"conversation_id": "3f9c...", "reply": "Hi Sam! Nice to meet you..."}
```

### Continue that conversation (context-aware)
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What'\''s my name?", "conversation_id": "3f9c..."}'
```
The full prior history for that `conversation_id` is loaded from the
database and sent to Gemini on every call, so the model remembers "Sam."

## How context-awareness works
1. `POST /chat` looks up (or creates) a `Conversation` row.
2. All prior `Message` rows for that conversation are loaded, in order.
3. `llm_service.generate_reply()` turns that history into LangChain
   `HumanMessage`/`AIMessage` objects, appends the new user message, and
   calls Gemini via `ChatGoogleGenerativeAI`.
4. Both the user message and the reply are saved back to the database,
   so the next call has the full context again.

## Notes on the original test script
Your `tempCodeRunnerFile.py` confirmed the Gemini key and model load
correctly with `langchain_google_genai`. That same call pattern — including
the `isinstance(response.content, list)` handling for block-style
responses — is reused inside `app/llm_service.py`, just wrapped so it can
serve many conversations with persisted history instead of a single
one-off `invoke()`.

## Extending this project
- Add streaming responses (`llm.stream(...)`) for token-by-token output.
- Add auth (API key or JWT) to protect the endpoints.
- Swap SQLite for Postgres by changing `DATABASE_URL`.
- Add LangChain tools/function calling for web search, DB lookups, etc.
- Build a simple frontend (React/HTML) that calls `/chat`.
