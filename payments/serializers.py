from rest_framework import serializers
from .models import Installment


class InstallmentSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='package.client.full_name', read_only=True)
    package_info = serializers.SerializerMethodField()

    class Meta:
        model = Installment
        fields = '__all__'

    def get_package_info(self, obj):
        return str(obj.package)