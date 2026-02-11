from rest_framework import serializers
from localapi.models import LocalPlayer


class LocalPlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalPlayer
        fields = ["killer_bi_id", "big_payload", "synced_at"]