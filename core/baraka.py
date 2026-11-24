"""Client for the Baraka payments API (Baraka calls Safaricom Daraja for us)."""
import logging
import requests
from django.conf import settings as S

log = logging.getLogger(__name__)
DONE = {"completed", "complete", "success", "succeeded", "paid"}
FAILED = {"failed", "cancelled", "canceled", "expired", "timeout", "timed_out", "rejected"}

FRIENDLY = {"1": "There wasn’t enough M-Pesa balance.", "1001": "Another M-Pesa request is already open on this phone. Please wait a minute and try again.",
            "1019": "The prompt expired before it was answered.", "1032": "The request was cancelled.",
            "1037": "The prompt timed out before a PIN was entered.", "1038": "No PIN was entered, so the prompt timed out.",
            "2001": "The PIN entered was incorrect."}

def _headers(extra=None):
    h = {"Authorization": f"Bearer {S.BARAKA_API_TOKEN}", "Accept": "application/json", "Content-Type": "application/json"}
    h.update(extra or {})
    return h

def payment_id(j):
    j = j or {}
    return j.get("id") or (j.get("data") or {}).get("id") or j.get("payment_id") or (j.get("data") or {}).get("payment_id")

def stk_push(phone, amount, idempotency_key, callback_url):
    """Asks Baraka to send the M-Pesa prompt. Returns (payment_id, raw_response)."""
    r = requests.post(f"{S.BARAKA_API_URL}/stk-pushes", headers=_headers({"Idempotency-Key": idempotency_key}), timeout=20, json={
        "phone": phone, "amount": int(amount), "fund_id": S.BARAKA_FUND_ID, "account_ref": S.BARAKA_ACCOUNT_REF,
        "description": S.BARAKA_DESCRIPTION, "callback_url": callback_url})
    r.raise_for_status()
    j = r.json()
    pid = payment_id(j)
    if not pid:
        raise RuntimeError("Baraka returned no payment id")
    return pid, j

def status(pid):
    """Returns (state, reason, receipt, raw): state is COMPLETE, FAILED or PENDING."""
    r = requests.get(f"{S.BARAKA_API_URL}/stk-pushes/{pid}", headers=_headers(), timeout=15)
    r.raise_for_status()
    raw = r.json()
    j = raw.get("data", raw) if isinstance(raw, dict) else {}
    word = str(j.get("status") or j.get("state") or "").lower()
    receipt = str(j.get("receipt") or j.get("mpesa_receipt") or j.get("receipt_number") or j.get("mpesa_receipt_number") or "")
    reason = str(j.get("failure_reason") or j.get("reason") or j.get("result_desc") or "")
    rc = j.get("result_code")  # Safaricom's own verdict: 0 = paid, anything else = not paid, empty = still waiting
    if rc not in (None, ""):
        return ("COMPLETE", "", receipt, raw) if str(rc) == "0" else ("FAILED", FRIENDLY.get(str(rc), "The payment didn’t go through."), receipt, raw)
    if word in DONE: return "COMPLETE", "", receipt, raw
    if word in FAILED: return "FAILED", reason, receipt, raw
    if word not in {"", "pending", "processing", "queued", "initiated", "sent"}:
        log.warning("Unrecognised Baraka status word: %r", word)
    return "PENDING", "", receipt, raw
