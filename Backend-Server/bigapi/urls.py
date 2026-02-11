from django.urls import path
from .views import PlayerCacheAPIView

urlpatterns = [
    path("", PlayerCacheAPIView.as_view(), name="player-cache"),
]