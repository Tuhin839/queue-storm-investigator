# QueueStorm Investigator - SUST CSE Carnival 2026

## Project Overview
Rule-based ticket investigation service for bKash support team. Analyzes customer complaint along with transaction history.

## Endpoints
- `GET /health` — Service health check
- `POST /analyze-ticket` — Main analysis endpoint

## Live Deployment
- **Platform:** Render.com
- **Live URL:** https://queue-storm-investigator.onrender.com

## Safety Features
- Never asks for PIN, OTP, password or any sensitive information
- Uses safe and neutral language in customer replies
- Escalates phishing and high-risk cases to human review

## How to Run Locally
```bash
pip install -r requirements.txt
uvicorn main:app --reload
Sample Request
JSON
{
  "ticket_id": "TKT-001",
  "complaint": "I sent 5000 taka to a wrong number around 2pm today. The number was supposed to be 01712345678 but I think I typed it wrong. Please help me get my money back.",
  "language": "en",
  "transaction_history": [
    {
      "transaction_id": "TXN-9101",
      "timestamp": "2026-04-14T14:08:22Z",
      "type": "transfer",
      "amount": 5000,
      "counterparty": "+8801719876543",
      "status": "completed"
    }
  ]
}
Team

Member: Tuhin Kumar Datta and Tuhin Biswas
LLM Used: No (Rule-based logic)
Known Limitations: Basic amount and keyword matching. Can be improved further.