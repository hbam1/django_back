from django.shortcuts import render
from rest_framework import viewsets, status
from .models import Authentication, MemberAuthentication
from .serializers import AuthenticationSerializer, MemberAuthenticationSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rooms.models import Room

#인증 제출
class MemberAuthCreateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MemberAuthenticationSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        auth = serializer.save(user=request.user)
        return Response(MemberAuthenticationSerializer(auth), status=status.HTTP_201_CREATED)
    

#인증 수락
class MemberAuthAcceptAPI(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        auth = MemberAuthentication.objects.get(id=pk)
        room = auth.room
        if room.master != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        auth.is_auth = True
        auth.is_completed = True
        auth.save()

        return Response(status=status.HTTP_200_OK)
    

#인증 거절
class MemberAuthRejectAPI(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        auth = MemberAuthentication.objects.get(id=pk)
        room = auth.room
        if room.master != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        auth.is_completed = True
        auth.save()

        return Response(status=status.HTTP_200_OK)
    

#로그 list
class LogListAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, room_id):
        room = Room.objects.get(pk=room_id)
        auth_logs = MemberAuthentication.objects.filter(room=room).filter(is_completed=True).order_by('-created_date')
        serializer = MemberAuthenticationSerializer(auth_logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
