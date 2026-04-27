from django.contrib import admin
from .models import Installment


@admin.register(Installment)
class InstallmentAdmin(admin.ModelAdmin):
    list_display = ('package', 'installment_number', 'amount', 'due_date', 'paid_date', 'status', 'created_at')
    list_filter = ('status', 'due_date')
    search_fields = ('package__client__full_name',)