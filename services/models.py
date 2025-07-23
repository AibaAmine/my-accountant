import uuid
from django.db import models
from accounts.models import User


class Service(models.Model):

    service_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    accountant_id = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="services_offered"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    service_type = models.CharField(
        max_length=100,
        choices=[
            ("tax_preparation", "Tax Preparation"),
            ("bookkeeping", "Bookkeeping"),
            ("financial_consulting", "Financial Consulting"),
            ("audit", "Audit"),
            ("payroll", "Payroll"),
            ("business_setup", "Business Setup"),
            ("other", "Other"),
        ],
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "service"
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return self.title
