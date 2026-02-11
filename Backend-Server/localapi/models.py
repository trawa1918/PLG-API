from django.db import models


class LocalPlayer(models.Model):
    killer_bi_id = models.CharField(max_length=64, unique=True, db_index=True)

    # cache selected fields from BIG DB (you can replace/expand these)
    big_payload = models.JSONField(default=dict, blank=True)

    synced_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.killer_bi_id

