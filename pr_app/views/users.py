from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ..serializers import (UserSerializer, SetIsActiveSerializer, UserReviewResponseSerializer)
from ..services import set_user_is_active, get_user_reviews
from ..exceptions import DomainError, BadRequestError
from .utils import domain_error_to_response


class SetIsActiveView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SetIsActiveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            user = set_user_is_active(user_id=data["user_id"], is_active=data["is_active"])
        except DomainError as exc:
            return domain_error_to_response(exc)
        response_serializer = UserSerializer(user)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class GetReviewView(APIView):
    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get("user_id")
        if not user_id:
            return domain_error_to_response(BadRequestError("user_id is required"))
        try:
            user, prs = get_user_reviews(user_id=user_id)
        except DomainError as exc:
            return domain_error_to_response(exc)
        response_data = {"user_id": user.user_id, "pull_requests": prs}
        serializer = UserReviewResponseSerializer(response_data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    