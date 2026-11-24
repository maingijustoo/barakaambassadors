import uuid
from django.db import models

class Track(models.Model):
    KINDS = [("preview", "Public preview (other songs)"), ("album", "Album track (paid)"), ("zip", "Album ZIP (paid)")]
    title = models.CharField(max_length=120)
    key = models.CharField(max_length=300, help_text="File path/key in the R2 bucket, e.g. album/01-title.mp3")
    kind = models.CharField(max_length=10, choices=KINDS, default="album")
    order = models.PositiveIntegerField(default=0)
    class Meta: ordering = ["order", "id"]
    def __str__(self): return f"{self.title} ({self.kind})"

class Entry(models.Model):
    KINDS = [("history", "Our history"), ("project", "Future project")]
    kind = models.CharField(max_length=10, choices=KINDS)
    title = models.CharField(max_length=120, help_text="e.g. a year, or a project name")
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)
    class Meta: ordering = ["order", "id"]; verbose_name_plural = "entries"
    def __str__(self): return self.title

class Supporter(models.Model):
    name = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    amount = models.PositiveIntegerField()
    status = models.CharField(max_length=10, default="pending", choices=[("pending", "Pending"), ("paid", "Paid"), ("failed", "Failed")])
    api_ref = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    invoice_id = models.CharField(max_length=100, blank=True)
    reason = models.CharField(max_length=200, blank=True)
    downloads = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    class Meta: ordering = ["-created"]
    def __str__(self): return f"{self.phone} KES {self.amount} {self.status}"
