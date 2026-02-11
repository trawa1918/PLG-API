from django.db import models


class PlayerRecord(models.Model):
    id = models.BigAutoField(primary_key=True)
    external_player_id = models.CharField(max_length=64, db_index=True)
    # other columns you want to return...Do zrobienia

    class Meta:
        managed = False
        db_table = "player_records"  # adjust (optionally schema-qualified)
