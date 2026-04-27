from django.contrib import admin
from .models import Package


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = (
        'client',
        'total_sessions',
        'sessions_used',
        'total_price',
        'billing_type',
        'status',
        'start_date',
        'end_date',
    )
