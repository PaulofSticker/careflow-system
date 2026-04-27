from django.contrib import admin
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'city', 'state', 'status', 'created_at')
    search_fields = ('full_name', 'email', 'phone', 'city', 'state')
    list_filter = ('status', 'state', 'created_at')
