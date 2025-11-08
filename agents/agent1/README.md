# Text Summarizer Agent with Google Gemini

A ready-to-use text summarization agent powered by Google Gemini AI.

## Features

- Summarizes text into 2-4 bullet points
- RESTful API endpoints
- Health check endpoint
- Error handling

## Requirements

- Python 3.7+
- Google Gemini API key

## Installation

1. Install required packages:
```bash
pip install google-generativeai fastapi uvicorn python-dotenv
```

2. Set up your Google Gemini API key in the `.env` file:
```
GEMINI_API_KEY=your_api_key_here
```

## Usage

1. Start the server:
```bash
uvicorn summarizer_agent_gemini:app --reload --host 0.0.0.0 --port 8000
```

2. The API will be available at `http://localhost:8000`

## API Endpoints

- `GET /health` - Health check endpoint
- `POST /call` - Summarization endpoint

### Summarization Endpoint

Send a POST request to `/call` with the following JSON payload:

```json
{
  "input": {
    "text": "Your text to summarize here..."
  }
}
```

Response:
```json
{
  "status": "ok",
  "result": {
    "summary": "Bullet point summary of the text"
  },
  "meta": {
    "agent": "summarizer-gemini"
  }
}
```

## Example

```python
import requests

payload = {
    "input": {
        "text": "Artificial intelligence (AI) is intelligence demonstrated by machines..."
    }
}

response = requests.post("http://localhost:8000/call", json=payload)
print(response.json())
```