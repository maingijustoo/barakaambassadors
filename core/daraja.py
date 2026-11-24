"""Safaricom Daraja: M-Pesa Express (STK Push) and status query."""
import base64
import requests
from django.conf import settings as S
from django.utils import timezone

def _base():
    return "https://sandbox.safaricom.co.ke" if S.DARAJA_SANDBOX else "https://api.safaricom.co.ke"

def _token():
    r = requests.get(f"{_base()}/oauth/v1/generate?grant_type=client_credentials", auth=(S.DARAJA_KEY, S.DARAJA_SECRET), timeout=15)
    r.raise_for_status()
    return r.json()["access_token"]

def _auth():
    ts = timezone.localtime().strftime("%Y%m%d%H%M%S")  # East Africa Time
    pw = base64.b64encode(f"{S.DARAJA_SHORTCODE}{S.DARAJA_PASSKEY}{ts}".encode()).decode()
    return ts, pw

def stk_push(phone, amount, callback_url):
    ts, pw = _auth()
    body = {"BusinessShortCode": S.DARAJA_SHORTCODE, "Password": pw, "Timestamp": ts, "TransactionType": S.DARAJA_TXN_TYPE,
            "Amount": int(amount), "PartyA": phone, "PartyB": S.DARAJA_PARTYB or S.DARAJA_SHORTCODE, "PhoneNumber": phone,
            "CallBackURL": callback_url, "AccountReference": S.DARAJA_ACCOUNT_REF[:12], "TransactionDesc": "Album support"}
    r = requests.post(f"{_base()}/mpesa/stkpush/v1/processrequest", json=body, headers={"Authorization": f"Bearer {_token()}"}, timeout=20)
    r.raise_for_status()
    j = r.json()
    if str(j.get("ResponseCode")) != "0":
        raise RuntimeError(j.get("ResponseDescription", "STK push rejected"))
    return j["CheckoutRequestID"]

def query(checkout_id):
    """Returns (state, reason): COMPLETE / FAILED / PENDING."""
    ts, pw = _auth()
    r = requests.post(f"{_base()}/mpesa/stkpushquery/v1/query", json={"BusinessShortCode": S.DARAJA_SHORTCODE, "Password": pw,
        "Timestamp": ts, "CheckoutRequestID": checkout_id}, headers={"Authorization": f"Bearer {_token()}"}, timeout=15)
    try: j = r.json()
    except ValueError: return "PENDING", ""
    if j.get("ResultCode") is None: return "PENDING", ""   # "still being processed" comes back as an error body
    return ("COMPLETE", "") if int(j["ResultCode"]) == 0 else ("FAILED", j.get("ResultDesc", ""))

def parse_callback(p):
    """Returns (checkout_id, result_code, desc, receipt, amount)."""
    cb = (p.get("Body") or {}).get("stkCallback") or {}
    items = {i.get("Name"): i.get("Value") for i in (cb.get("CallbackMetadata") or {}).get("Item", [])}
    return cb.get("CheckoutRequestID"), cb.get("ResultCode"), cb.get("ResultDesc", ""), str(items.get("MpesaReceiptNumber") or ""), items.get("Amount")
