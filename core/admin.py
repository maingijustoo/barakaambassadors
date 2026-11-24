import csv
from django.contrib import admin
from django.http import HttpResponse
from .models import Entry, Supporter, Track

@admin.action(description="Export selected to CSV")
def export_csv(modeladmin, request, qs):
    r = HttpResponse(content_type="text/csv"); r["Content-Disposition"] = "attachment; filename=supporters.csv"
    w = csv.writer(r); w.writerow(["Date", "Name", "Phone", "Email", "Amount", "Status", "M-Pesa code", "Downloads"])
    for s in qs: w.writerow([s.created.strftime("%Y-%m-%d %H:%M"), s.name, s.phone, s.email, s.amount, s.status, s.receipt, s.downloads])
    return r

@admin.register(Supporter)
class SupporterAdmin(admin.ModelAdmin):
    list_display = ("created", "name", "phone", "amount", "status", "receipt", "downloads")
    list_filter = ("status", "amount"); search_fields = ("name", "phone", "email", "invoice_id", "receipt")
    readonly_fields = ("api_ref", "token", "invoice_id", "raw", "created", "paid_at"); actions = [export_csv]
    date_hierarchy = "created"

admin.site.register(Track, list_display=("title", "kind", "key", "order"))
admin.site.register(Entry, list_display=("title", "kind", "order"))
admin.site.site_header = "Album launch admin"
