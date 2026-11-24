import json, re, hmac
from django.conf import settings as S
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_POST
from .admin import export_csv
from .models import Entry, Supporter, Track

TIERS = [(100, "Friend of the club", False), (200, "Supporter", True), (250, "Champion", False)]

def site(request):
    import os
    st = S.BASE_DIR / "core" / "static"
    v = int(max(os.path.getmtime(st / "css" / "site.css"), os.path.getmtime(st / "js" / "app.js")))
    return {"S": S, "V": v, "TIERS": [{"amt": a, "name": n, "pop": p} for a, n, p in TIERS]}

def phone_norm(p):
    d = re.sub(r"\D", "", p or "")
    d = "254" + d[1:] if d.startswith("0") else "254" + d if len(d) == 9 else d
    return d if re.fullmatch(r"254[17]\d{8}", d) else None

def signed_url(key, filename=None, minutes=60):
    if S.R2_BUCKET:
        import boto3
        from botocore.config import Config
        c = boto3.client("s3", region_name="auto", endpoint_url=f"https://{S.R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
                         aws_access_key_id=S.R2_KEY, aws_secret_access_key=S.R2_SECRET, config=Config(signature_version="s3v4"))
        p = {"Bucket": S.R2_BUCKET, "Key": key}
        if filename: p["ResponseContentDisposition"] = f'attachment; filename="{filename}"'
        return c.generate_presigned_url("get_object", Params=p, ExpiresIn=minutes * 60)
    return S.MEDIA_URL + key  # local development fallback

def intasend():
    from intasend import APIService
    return APIService(token=S.INTASEND_TOKEN, publishable_key=S.INTASEND_PUB_KEY, test=S.INTASEND_TEST)

def apply_state(s, state, reason=""):
    if state == "COMPLETE" and s.status != "paid":
        s.status, s.paid_at = "paid", timezone.now()
    elif state == "FAILED" and s.status == "pending":
        s.status, s.reason = "failed", (reason or "Payment was not completed")[:200]
    s.save()

@ensure_csrf_cookie
def home(request):
    return render(request, "core/home.html", {"previews": Track.objects.filter(kind="preview")})

def about(request):
    return render(request, "core/about.html", {"history": Entry.objects.filter(kind="history"), "projects": Entry.objects.filter(kind="project")})

@require_POST
def pay(request):
    try: d = json.loads(request.body)
    except ValueError: return JsonResponse({"error": "Something went wrong. Please try again."}, status=400)
    phone = phone_norm(d.get("phone"))
    try: amount = int(d.get("amount"))
    except (TypeError, ValueError): amount = 0
    if not phone: return JsonResponse({"error": "Please enter a valid Safaricom number, like 0712 345 678."}, status=400)
    if amount not in {a for a, _, _ in TIERS} and amount < S.CUSTOM_MIN:
        return JsonResponse({"error": f"Please choose a tier, or give KES {S.CUSTOM_MIN} or more."}, status=400)
    recent = Supporter.objects.filter(phone=phone, status="pending", created__gt=timezone.now() - timezone.timedelta(minutes=2)).count()
    if recent >= 2: return JsonResponse({"error": "We've already sent you a prompt. Please check your phone."}, status=429)
    s = Supporter.objects.create(phone=phone, amount=amount, name=(d.get("name") or "")[:120], email=(d.get("email") or "")[:200])
    if S.DEMO_MODE:
        apply_state(s, "COMPLETE"); return JsonResponse({"ref": str(s.api_ref)})
    try:
        svc, kw = intasend(), dict(phone_number=phone, email=s.email or "supporter@example.com", amount=amount, narrative=f"{S.CLUB_NAME} support")
        try: r = svc.collect.mpesa_stk_push(api_ref=str(s.api_ref), **kw)
        except TypeError: r = svc.collect.mpesa_stk_push(**kw)
        s.invoice_id = (r.get("invoice") or {}).get("invoice_id", ""); s.save()
    except Exception:
        apply_state(s, "FAILED", "Could not reach M-Pesa"); return JsonResponse({"error": "We couldn't send the M-Pesa prompt. Please try again in a moment."}, status=502)
    return JsonResponse({"ref": str(s.api_ref)})

def check(request, ref):
    s = get_object_or_404(Supporter, api_ref=ref)
    if s.status == "pending" and s.invoice_id:  # fallback in case the webhook is slow
        try:
            r = intasend().collect.status(invoice_id=s.invoice_id); inv = r.get("invoice") or r
            apply_state(s, inv.get("state"), inv.get("failed_reason") or "")
        except Exception: pass
    return JsonResponse({"status": s.status, "reason": s.reason, "url": f"/album/{s.token}/" if s.status == "paid" else None})

@csrf_exempt
@require_POST
def hook(request):
    try: p = json.loads(request.body)
    except ValueError: return HttpResponseForbidden()
    if S.INTASEND_CHALLENGE and not hmac.compare_digest(str(p.get("challenge", "")), S.INTASEND_CHALLENGE): return HttpResponseForbidden()
    s = Supporter.objects.filter(invoice_id=p.get("invoice_id") or "-").first()
    if not s and p.get("api_ref"):
        try: s = Supporter.objects.filter(api_ref=p["api_ref"]).first()
        except Exception: s = None
    if s: apply_state(s, p.get("state"), p.get("failed_reason") or "")
    return JsonResponse({"ok": True})

@require_POST
def find(request):
    phone = phone_norm(request.POST.get("phone"))
    try: amount = int(request.POST.get("amount"))
    except (TypeError, ValueError): amount = 0
    s = Supporter.objects.filter(phone=phone, amount=amount, status="paid").first() if phone else None
    return redirect("album", token=s.token) if s else render(request, "core/home.html", {"previews": Track.objects.filter(kind="preview"), "find_error": True})

def album(request, token):
    s = get_object_or_404(Supporter, token=token, status="paid")
    return render(request, "core/album.html", {"s": s, "tracks": Track.objects.filter(kind="album"), "zips": Track.objects.filter(kind="zip")})

def fetch(request, token, tid):
    s = get_object_or_404(Supporter, token=token, status="paid"); t = get_object_or_404(Track, pk=tid, kind__in=["album", "zip"])
    if request.GET.get("dl"):
        if s.downloads >= S.MAX_DOWNLOADS: return HttpResponseForbidden("Download limit reached. Please contact the club and we'll sort you out.")
        s.downloads += 1; s.save(update_fields=["downloads"])
        return redirect(signed_url(t.key, filename=t.key.rsplit("/", 1)[-1]))
    return redirect(signed_url(t.key))

def listen(request, tid):
    return redirect(signed_url(get_object_or_404(Track, pk=tid, kind="preview").key))

@staff_member_required
def dashboard(request):
    paid = Supporter.objects.filter(status="paid")
    tot = paid.aggregate(n=Count("id"), total=Sum("amount"))
    return render(request, "core/dashboard.html", {"tot": tot, "by": paid.values("amount").annotate(n=Count("id"), sum=Sum("amount")).order_by("amount"),
        "recent": Supporter.objects.all()[:60], "pending": Supporter.objects.filter(status="pending").count(), "failed": Supporter.objects.filter(status="failed").count()})

@staff_member_required
def dashboard_csv(request):
    return export_csv(None, request, Supporter.objects.all())
