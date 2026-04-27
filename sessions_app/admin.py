from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from .models import Session


class SessionAdminForm(ModelForm):
    class Meta:
        model = Session
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        client = cleaned_data.get('client')
        package = cleaned_data.get('package')

        if client and package and package.client != client:
            raise ValidationError("The selected package does not belong to this client.")

        return cleaned_data


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    form = SessionAdminForm
    list_display = ('client', 'package', 'scheduled_date', 'scheduled_time', 'status', 'duration_minutes')
    list_filter = ('status', 'scheduled_date')
    search_fields = ('client__full_name',)