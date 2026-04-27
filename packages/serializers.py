from rest_framework import serializers
from .models import Package


class PackageSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.full_name', read_only=True)
    client_email = serializers.CharField(source='client.email', read_only=True)
    client_phone = serializers.CharField(source='client.phone', read_only=True)

    client_street = serializers.CharField(source='client.street', read_only=True)
    client_city = serializers.CharField(source='client.city', read_only=True)
    client_state = serializers.CharField(source='client.state', read_only=True)
    client_zip_code = serializers.CharField(source='client.zip_code', read_only=True)

    class Meta:
        model = Package
        fields = [
            'id',
            'client',
            'client_name',
            'client_email',
            'client_phone',
            'client_street',
            'client_city',
            'client_state',
            'client_zip_code',
            'total_sessions',
            'sessions_used',
            'total_price',
            'billing_type',
            'installment_count',
            'start_date',
            'end_date',
            'status',
            'created_at',
        ]