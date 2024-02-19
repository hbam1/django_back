from django.shortcuts import render
from rest_framework import viewsets, status
from .models import Alarm
from .serializers import AlarmSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


# 알람 생성
class AlarmCreateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AlarmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # 예외가 발생했을 때 에러를 발생시켜라
        alarm = serializer.save(from_to=request.user)
        return Response(AlarmSerializer(alarm), status=status.HTTP_201_CREATED)