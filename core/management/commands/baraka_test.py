import time, uuid
from django.conf import settings as S
from django.core.management.base import BaseCommand, CommandError
from core import baraka

class Command(BaseCommand):
    help = "Send a test M-Pesa prompt through Baraka and watch its status.  Usage: baraka_test 0712345678 1 https://webhook.site/your-id"
    def add_arguments(self, p):
        p.add_argument("phone"); p.add_argument("amount", type=int); p.add_argument("callback_url")
    def handle(self, phone, amount, callback_url, **o):
        if not (S.BARAKA_API_TOKEN and S.BARAKA_FUND_ID): raise CommandError("Set BARAKA_API_TOKEN and BARAKA_FUND_ID first.")
        pid, raw = baraka.stk_push(phone, amount, f"test-{uuid.uuid4()}", callback_url)
        self.stdout.write(f"Accepted. Payment id: {pid}\n{raw}\nCheck your phone and enter your PIN...")
        for _ in range(18):
            time.sleep(5)
            state, why, receipt, raw = baraka.status(pid)
            self.stdout.write(f"{state}  {receipt}  {why}   raw={raw}")
            if state != "PENDING": break
