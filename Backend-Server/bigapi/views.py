import json
import os
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings

from .serializers import LocalPlayerSerializer
from localapi.models import LocalPlayer


class PlayerCacheAPIView(APIView):
    """
    GET /api/?killer_bi_id=XYZ

    External API contract:
    - GET {EXTERNAL_API_BASE_URL}/players?killer_bi_id=XYZ
    - returns a JSON LIST ([])
    """

    def get(self, request):
        provided_key = request.headers.get("X-API-Key", "")
        if not settings.API_KEY or provided_key != settings.API_KEY:
            return Response({"detail": "Invalid or missing API key"}, status=status.HTTP_403_FORBIDDEN)

        killer_bi_id = request.query_params.get("killer_bi_id")
        if not killer_bi_id:
            return Response({"detail": "killer_bi_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        ttl = int(os.environ.get("CACHE_TTL_SECONDS", "3600"))
        now = int(time.time())

        cached = LocalPlayer.objects.filter(killer_bi_id=killer_bi_id).first()
        if cached and cached.big_payload:
            synced_at_ts = int(cached.synced_at.timestamp())
            if now - synced_at_ts <= ttl:
                return Response(LocalPlayerSerializer(cached).data, status=status.HTTP_200_OK)

        base_url = os.environ.get("EXTERNAL_API_BASE_URL")
        if not base_url:
            return Response({"detail": "EXTERNAL_API_BASE_URL is not set"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        timeout = int(os.environ.get("EXTERNAL_API_TIMEOUT_SECONDS", "5"))
        query = urlencode({"killer_bi_id": killer_bi_id})
        external_url = urljoin(base_url.rstrip("/") + "/", "players") + "?" + query

        try:
            req = Request(external_url, headers={"Accept": "application/json"})
            with urlopen(req, timeout=timeout) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except HTTPError as e:
            if e.code == 404:
                return Response({"detail": "Not found in external API"}, status=status.HTTP_404_NOT_FOUND)
            return Response({"detail": "External API error", "status_code": e.code}, status=status.HTTP_502_BAD_GATEWAY)
        except URLError as e:
            return Response({"detail": "External API unreachable", "error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)
        except Exception as e:
            return Response(
                {"detail": "Failed to fetch/parse external API response", "error": str(e)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if not isinstance(payload, list):
            return Response(
                {"detail": "Unexpected external API response format (expected list)"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if len(payload) == 0:
            return Response({"detail": "Not found in external API"}, status=status.HTTP_404_NOT_FOUND)

        # Find exact match in list (safest), otherwise take first element if list is already filtered server-side.
        matched = None
        for item in payload:
            if isinstance(item, dict) and str(item.get("killer_bi_id", "")) == str(killer_bi_id):
                matched = item
                break

        if matched is None:
            # If the external API guarantees filtering by killer_bi_id, you can uncomment the next line:
            # matched = payload[0]
            return Response(
                {"detail": "External API returned list but no matching killer_bi_id"},
                status=status.HTTP_404_NOT_FOUND,
            )

        obj, _created = LocalPlayer.objects.update_or_create(
            killer_bi_id=killer_bi_id,
            defaults={"big_payload": matched},
        )
        return Response(LocalPlayerSerializer(obj).data, status=status.HTTP_200_OK)