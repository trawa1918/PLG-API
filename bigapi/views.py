from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import PlayerRecord
from .serializers import LocalPlayerSerializer
from localapi.models import LocalPlayer


class PlayerSyncViewSet(viewsets.ViewSet):
    """
    GET /players/sync/?killer_bi_id=XYZ
    - reads PlayerRecord from BIG (Postgres)
    - upserts LocalPlayer in SQLite
    - returns the SQLite record (with cached big_payload)
    """

    @action(detail=False, methods=["get"], url_path="sync")
    def sync(self, request):
        killer_bi_id = request.query_params.get("killer_bi_id")
        if not killer_bi_id:
            return Response({"detail": "killer_bi_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        big_row = (
            PlayerRecord.objects.using("big")
            .filter(killer_bi_id=killer_bi_id)
            .values()
            .first()
        )
        if not big_row:
            return Response({"detail": "Not found in big database"}, status=status.HTTP_404_NOT_FOUND)

        obj, _created = LocalPlayer.objects.update_or_create(
            killer_bi_id=killer_bi_id,
            defaults={"big_payload": big_row},
        )

        return Response(LocalPlayerSerializer(obj).data, status=status.HTTP_200_OK)