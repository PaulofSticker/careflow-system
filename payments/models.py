from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from packages.models import Package


class Installment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('card', 'Card'),
        ('zelle', 'Zelle'),
        ('cash', 'Cash'),
    ]

    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='installments')
    installment_number = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    paid_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['package', 'installment_number']
        constraints = [
            models.UniqueConstraint(
                fields=['package', 'installment_number'],
                name='unique_installment_number_per_package'
            )
        ]

    def clean(self):
        super().clean()

        if self.amount <= 0:
            raise ValidationError("Installment amount must be greater than zero.")

    def update_status(self):
        today = timezone.localdate()

        if self.paid_date:
            self.status = 'paid'
        elif self.due_date < today:
            self.status = 'overdue'
        else:
            self.status = 'pending'

    @property
    def is_overdue(self):
        return self.status != 'paid' and self.due_date < timezone.localdate()

    def save(self, *args, **kwargs):
        self.update_status()
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Installment {self.installment_number} - {self.package}"