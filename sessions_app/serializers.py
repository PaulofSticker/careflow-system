from rest_framework import serializers
from .models import Session


class SessionSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.full_name', read_only=True)
    package_info = serializers.CharField(source='package.__str__', read_only=True)

    class Meta:
        model = Session
        fields = '__all__'