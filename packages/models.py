from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from clients.models import Client


class Package(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]

    PACKAGE_TYPE_CHOICES = [
        ('single', 'Single'),
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
    ]

    BILLING_TYPE_CHOICES = [
        ('full', 'Full'),
        ('installment', 'Installment'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('card', 'Card'),
        ('zelle', 'Zelle'),
        ('cash', 'Cash'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='packages')
    package_type = models.CharField(max_length=20, choices=PACKAGE_TYPE_CHOICES)
    total_sessions = models.PositiveIntegerField()
    sessions_used = models.PositiveIntegerField(default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    billing_type = models.CharField(max_length=20, choices=BILLING_TYPE_CHOICES)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    installment_count = models.PositiveIntegerField(default=1)

    start_date = models.DateField()
    end_date = models.DateField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        super().clean()

        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError("End date cannot be earlier than start date.")

        if self.total_sessions <= 0:
            raise ValidationError("Total sessions must be greater than zero.")

        if self.sessions_used > self.total_sessions:
            raise ValidationError("Sessions used cannot exceed total sessions.")

        if self.total_price <= 0:
            raise ValidationError("Total price must be greater than zero.")

        if self.billing_type == 'full' and self.installment_count != 1:
            raise ValidationError("Full payment must have exactly 1 installment.")

        if self.billing_type == 'installment' and self.installment_count < 2:
            raise ValidationError("Installment payment must have at least 2 installments.")

        if self.package_type == 'bronze' and self.total_sessions != 4:
            raise ValidationError("Bronze package must have 4 sessions.")

        if self.package_type == 'silver' and self.total_sessions != 8:
            raise ValidationError("Silver package must have 8 sessions.")

        if self.package_type == 'single' and self.total_sessions not in [1, 2, 3]:
            raise ValidationError("Single package must have 1 to 3 sessions.")

        if self.package_type == 'gold' and self.total_sessions not in [10, 11, 12]:
            raise ValidationError("Gold package must have 10 to 12 sessions.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def consumed_sessions(self):
        return self.sessions.filter(status__in=['completed', 'no_show']).count()

    @property
    def reserved_sessions(self):
        return self.sessions.exclude(status='cancelled').count()

    @property
    def sessions_remaining(self):
        return max(self.total_sessions - self.consumed_sessions, 0)

    @property
    def sessions_available_to_schedule(self):
        return max(self.total_sessions - self.reserved_sessions, 0)

    @property
    def is_expired(self):
        return self.end_date < timezone.localdate()

    @property
    def has_overdue_installments(self):
        return self.installments.filter(status='overdue').exists()

    def recalculate_usage(self):
        self.sessions_used = self.consumed_sessions

        if self.status == 'cancelled':
            self.save(update_fields=['sessions_used'])
            return

        if self.sessions_used >= self.total_sessions:
            self.status = 'completed'
        elif self.is_expired:
            self.status = 'expired'
        else:
            self.status = 'active'

        self.save(update_fields=['sessions_used', 'status'])

    def __str__(self):
        return f"{self.client.full_name} - {self.get_package_type_display()}"