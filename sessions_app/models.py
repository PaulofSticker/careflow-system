from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from clients.models import Client
from packages.models import Package


class Session(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No-show'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='sessions')
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='sessions')

    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True, null=True)
    duration_minutes = models.PositiveIntegerField(default=60)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['scheduled_date', 'scheduled_time']

    def clean(self):
        super().clean()

        if self.package_id and self.client_id and self.package.client_id != self.client_id:
            raise ValidationError("The selected package does not belong to this client.")

        if self.package_id:
            if self.package.status != 'active':
                raise ValidationError("Cannot schedule with an inactive package.")

            if self.package.is_expired:
                raise ValidationError("Cannot schedule with an expired package.")

            if self.package.billing_type == 'installment' and self.package.has_overdue_installments:
                raise ValidationError("Cannot schedule new sessions while there are overdue installments.")

            if self.package.sessions_available_to_schedule <= 0:
                raise ValidationError("This package has no available sessions remaining.")

        now = timezone.localtime()
        current_date = now.date()
        current_time = now.time().replace(second=0, microsecond=0)

        if self.scheduled_date < current_date:
            raise ValidationError("Cannot schedule in the past.")

        if self.scheduled_date == current_date and self.scheduled_time < current_time:
            raise ValidationError("Cannot schedule past time.")

        if self.scheduled_time.minute not in [0, 15, 30, 45]:
            raise ValidationError("Time must be in 15-minute intervals.")

        if self.scheduled_time.hour < 5 or self.scheduled_time.hour > 23:
            raise ValidationError("Time must be between 05:00 and 23:45.")

        if self.duration_minutes <= 0:
            raise ValidationError("Duration must be greater than zero.")

        start = datetime.combine(self.scheduled_date, self.scheduled_time)
        end = start + timedelta(minutes=self.duration_minutes)

        sessions = Session.objects.filter(
            scheduled_date=self.scheduled_date,
            status='scheduled'
        ).exclude(id=self.id)

        for s in sessions:
            s_start = datetime.combine(s.scheduled_date, s.scheduled_time)
            s_end = s_start + timedelta(minutes=s.duration_minutes)

            if start < s_end and end > s_start:
                raise ValidationError("Time slot already booked.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        self.package.recalculate_usage()

    def delete(self, *args, **kwargs):
        package = self.package
        super().delete(*args, **kwargs)
        package.recalculate_usage()

    def __str__(self):
        return f"{self.client.full_name} - {self.scheduled_date} {self.scheduled_time}"
    
