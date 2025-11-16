from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ..services import get_reviewer_stats
from ..serializers import ReviewerStatsSerializer


class ReviewerStatsView(APIView):
    def get(self, request, *args, **kwargs):
        users = get_reviewer_stats()
        serializer = ReviewerStatsSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
