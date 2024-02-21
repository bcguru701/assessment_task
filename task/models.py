# models.py
from django.db import models
from django.utils import timezone

class Currency(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3)
    rate = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
