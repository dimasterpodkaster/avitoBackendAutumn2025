from rest_framework import serializers


class ErrorDetailsSerializer(serializers.Serializer):
    code = serializers.CharField()
    message = serializers.CharField()


class ErrorResponseSerializer(serializers.Serializer):
    error = ErrorDetailsSerializer()
