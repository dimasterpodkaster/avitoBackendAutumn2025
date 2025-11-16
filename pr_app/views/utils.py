from rest_framework.response import Response
from rest_framework import status

from ..exceptions import DomainError
from ..serializers import ErrorResponseSerializer


def domain_error_to_response(exc: DomainError) -> Response:
    code = getattr(exc, "code", "UNKNOWN")
    if code == "NOT_FOUND":
        http_status = status.HTTP_404_NOT_FOUND
    elif code in {"PR_MERGED", "PR_EXISTS", "NOT_ASSIGNED", "NO_CANDIDATE"}:
        http_status = status.HTTP_409_CONFLICT
    else:
        http_status = status.HTTP_400_BAD_REQUEST
    payload = {"error": {"code": code, "message": exc.message}}
    serializer = ErrorResponseSerializer(payload)
    return Response(serializer.data, status=http_status)
