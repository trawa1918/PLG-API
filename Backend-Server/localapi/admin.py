from django.contrib import admin
from .models import LocalPlayer


@admin.register(LocalPlayer)
class LocalPlayerAdmin(admin.ModelAdmin):
    list_display = ("killer_bi_id", "synced_at")
    search_fields = ("killer_bi_id",)


