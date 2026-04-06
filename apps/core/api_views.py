from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import fetch_github_issues


class DevTrackingAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        issues, api_error = fetch_github_issues()
        page = int(request.query_params.get("page", 1))
        per_page = 10
        start = (page - 1) * per_page
        end = start + per_page
        total = len(issues)

        return Response(
            {
                "results": issues[start:end],
                "count": total,
                "page": page,
                "total_pages": (total + per_page - 1) // per_page,
                "api_error": api_error,
            }
        )
