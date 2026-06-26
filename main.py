from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

app = FastAPI()

class Transaction(BaseModel):
    transaction_id: str
    timestamp: str
    type: str
    amount: float
    counterparty: Optional[str] = None
    status: str

class TicketRequest(BaseModel):
    ticket_id: str
    complaint: str
    language: Optional[str] = "en"
    channel: Optional[str] = None
    user_type: Optional[str] = None
    campaign_context: Optional[str] = None
    transaction_history: Optional[List[Transaction]] = []
    metadata: Optional[Dict[str, Any]] = {}

class TicketResponse(BaseModel):
    ticket_id: str
    relevant_transaction_id: Optional[str] = None
    evidence_verdict: str
    case_type: str
    severity: str
    department: str
    agent_summary: str
    recommended_next_action: str
    customer_reply: str
    human_review_required: bool
    confidence: float
    reason_codes: Optional[List[str]] = []

def find_relevant_transaction(complaint: str, history: List[Transaction]):
    if not history:
        return None, "insufficient_data"
    
    complaint_lower = complaint.lower()
    best_match = None
    best_score = 0

    for tx in history:
        score = 0
        amount_str = str(int(tx.amount))
        if amount_str in complaint_lower or abs(tx.amount - 5000) < 1000:
            score += 4
        if tx.type.lower() in complaint_lower:
            score += 2
        if tx.counterparty and any(part in complaint_lower for part in tx.counterparty[-8:]):
            score += 3
        
        if score > best_score:
            best_score = score
            best_match = tx.transaction_id

    verdict = "consistent" if best_score >= 3 else "insufficient_data"
    return best_match, verdict

def classify_case(complaint: str, relevant_tx, verdict, language: str):
    text = complaint.lower()
    
    if any(k in text for k in ["otp", "pin", "password", "অটিপি", "পিন", "verification"]):
        return {
            "case_type": "phishing_or_social_engineering", "severity": "critical", "department": "fraud_risk",
            "human_review": True, "confidence": 0.95, "reason": ["phishing"]
        }
    
    if any(k in text for k in ["wrong number", "wrong person", "ভুল নাম্বার", "wrong account"]):
        return {
            "case_type": "wrong_transfer", "severity": "high", "department": "dispute_resolution",
            "human_review": True, "confidence": 0.90, "reason": ["wrong_transfer"]
        }
    
    if any(k in text for k in ["failed", "deducted", "টাকা কাটা", "balance deducted"]):
        return {
            "case_type": "payment_failed", "severity": "high", "department": "payments_ops",
            "human_review": False, "confidence": 0.85, "reason": ["payment_failed"]
        }
    
    if "agent" in text and ("cash" in text or "ক্যাশ"):
        return {
            "case_type": "agent_cash_in_issue", "severity": "high", "department": "agent_operations",
            "human_review": True, "confidence": 0.85, "reason": ["agent_cash_in"]
        }
    
    return {
        "case_type": "other", "severity": "low", "department": "customer_support",
        "human_review": False, "confidence": 0.65, "reason": ["other"]
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze-ticket", response_model=TicketResponse)
def analyze_ticket(request: TicketRequest):
    relevant_tx, verdict = find_relevant_transaction(request.complaint, request.transaction_history or [])
    case_info = classify_case(request.complaint, relevant_tx, verdict, request.language or "en")
    
    agent_summary = f"Customer reported issue in ticket {request.ticket_id}. Relevant transaction: {relevant_tx or 'None'}."
    recommended = "Route to the assigned department and follow standard dispute/operation workflow."
    
    # Safe customer reply
    if (request.language or "en") == "bn":
        customer_reply = "আমরা আপনার অভিযোগ নথিভুক্ত করেছি। আমাদের টিম এটি পর্যালোচনা করবে এবং অফিসিয়াল চ্যানেলে যোগাযোগ করবে। দয়া করে কারো সাথে পিন বা OTP শেয়ার করবেন না।"
    else:
        customer_reply = "We have noted your concern regarding this transaction. Our team will review the case and contact you through official channels. Please do not share your PIN or OTP with anyone."

    return TicketResponse(
        ticket_id=request.ticket_id,
        relevant_transaction_id=relevant_tx,
        evidence_verdict=verdict,
        case_type=case_info["case_type"],
        severity=case_info["severity"],
        department=case_info["department"],
        agent_summary=agent_summary,
        recommended_next_action=recommended,
        customer_reply=customer_reply,
        human_review_required=case_info["human_review"],
        confidence=case_info["confidence"],
        reason_codes=case_info["reason"]
    )