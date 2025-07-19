# Debater

A FastAPI-based debate bot that engages in conversations and evaluates its own persuasiveness.

## Quick Start

```bash
# Install dependencies
make install

# Start the service
make run
```

## API Endpoints

### `/chat` - Main Debate Endpoint
Send a message to start or continue a debate:

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I think remote work is better than office work",
    "conversation_id": "optional-existing-id"
  }'
```

The bot will:
- Detect the debate topic automatically
- Take the opposite position
- Respond with persuasive arguments
- Store conversation in Redis

### `/evaluate-persuasiveness/{conversation_id}` - AI Evaluation
Get an AI-powered analysis of the bot's persuasiveness in a conversation:

```bash
curl "http://localhost:8000/evaluate-persuasiveness/your-conversation-id"
```

Returns scores (1-10) for:
- Logical coherence
- Evidence usage
- Emotional appeal
- Counter-argument handling
- Clarity and structure
- Overall persuasiveness

Plus detailed analysis and improvement suggestions.

### Other Endpoints
- `GET /` - Interactive chat interface for testing
- `GET /health` - Service status

**Interactive API Documentation:**
- Visit `/docs` for Swagger UI to explore and test all endpoints

## Testing

```bash
# Run all tests
make test
```

## Environment

Set `OPENAI_API_KEY` in your environment or `.env` file.

## Tech Stack

- FastAPI
- OpenAI GPT models
- Redis (conversation storage)
- Docker