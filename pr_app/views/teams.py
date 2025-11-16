from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers

from ..serializers import (TeamSerializer, TeamMemberSerializer, TeamDeactivateUsersRequestSerializer,
                           TeamDeactivateUsersResponseSerializer)
from ..services import create_team_with_members, get_team_with_members, deactivate_team_users
from ..exceptions import DomainError, BadRequestError
from .utils import domain_error_to_response


class TeamAddRequestSerializer(serializers.Serializer):
    team_name = serializers.CharField()
    members = TeamMemberSerializer(many=True)


class TeamAddView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = TeamAddRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            team = create_team_with_members(team_name=data["team_name"], members=data["members"])
        except DomainError as exc:
            return domain_error_to_response(exc)
        response_serializer = TeamSerializer(team)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class TeamGetView(APIView):
    def get(self, request, *args, **kwargs):
        team_name = request.query_params.get("team_name")
        if not team_name:
            return domain_error_to_response(BadRequestError("team_name is required"))
        try:
            team = get_team_with_members(team_name=team_name)
        except DomainError as exc:
            return domain_error_to_response(exc)

        serializer = TeamSerializer(team)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeamDeactivateUsersView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = TeamDeactivateUsersRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            result = deactivate_team_users(team_name=data["team_name"], user_ids=data["user_ids"])
        except DomainError as exc:
            return domain_error_to_response(exc)
        response_data = {"team": result["team"], "deactivated_user_ids": result["deactivated_user_ids"],
                         "changes": result["changes"]}
        response_serializer = TeamDeactivateUsersResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
