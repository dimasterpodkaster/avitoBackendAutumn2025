from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ..serializers import (PullRequestSerializer, PullRequestCreateSerializer, PullRequestMergeSerializer,
                           PullRequestReassignSerializer)
from ..services import (create_pull_request, merge_pull_request, reassign_reviewer)
from ..exceptions import DomainError
from .utils import domain_error_to_response


class PullRequestCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PullRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            pr = create_pull_request(pull_request_id=data["pull_request_id"],
                                     pull_request_name=data["pull_request_name"], author_id=data["author_id"])
        except DomainError as exc:
            return domain_error_to_response(exc)
        response_serializer = PullRequestSerializer(pr)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class PullRequestMergeView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PullRequestMergeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            pr = merge_pull_request(pull_request_id=data["pull_request_id"])
        except DomainError as exc:
            return domain_error_to_response(exc)
        response_serializer = PullRequestSerializer(pr)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class PullRequestReassignView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PullRequestReassignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            pr, old_reviewer, new_reviewer = reassign_reviewer(pull_request_id=data["pull_request_id"],
                                                               old_user_id=data["old_user_id"])
        except DomainError as exc:
            return domain_error_to_response(exc)
        response_serializer = PullRequestSerializer(pr)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    