from django.shortcuts import render
from rest_framework import viewsets, status
from .models import Alarm
from .serializers import AlarmSerializer, AlarmListSerializer
from activities.models import UserActivityInfo
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


# 알람 list
class AlarmListAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        alarms = Alarm.objects.get(alarm_to=request.user).order_by('-id')
        serializer = AlarmListSerializer(alarms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 알람 세부사항 조회
class AlarmRetrieveAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            alarm = Alarm.objects.get(id=pk)
            # 보안. 알람의 수신자가 아니면 접근할 수 없음
            if alarm.alarm_to != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
        except Alarm.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = AlarmListSerializer(alarm)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 알람 수락
class AlarmAcceptAPI(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            alarm = Alarm.objects.get(id=pk)
            # 알람 수신자 확인
            if alarm.alarm_to != request.user:
                return Response(status=status.HTTP_404_NOT_FOUND)
        except Alarm.DoesNotExist:
            return Response(self, status=status.HTTP_404_NOT_FOUND)

        # 수신자가 추천 유저일 때
        if alarm.goal.user == request.user:
            # 알람의 목표와 request의 목표가 일치하는지 확인
            if alarm.goal != request.data.get("goal"):
                return Response(status=status.HTTP_400_BAD_REQUEST)
            alarm.room.members.add(request.user)
            alarm.goal.is_in_group = True
            alarm.goal.belonging_group_id = request.data.get("room")

            # 보증금을 낼 수 있어야 가입
            if request.user.coin < alarm.room.deposit:
                return Response(status=status.HTTP_403_FORBIDDEN)

            # 유저 활동 정보 생성
            user_activity_info = UserActivityInfo.objects.create(
                user=request.user,
                room=alarm.room,
                deposit_left=alarm.room.deposit
            )
        else:
            # 알람의 방과 request의 방이 일치하는지 확인
            if alarm.room != request.data.get("room"):
                return Response(status=status.HTTP_400_BAD_REQUEST)
            alarm.room.members.add(alarm.from_to) # 수신자가 방장일 때
            alarm.goal.is_in_group = True
            alarm.goal.belonging_group_id = request.data.get("room")

            # 보증금을 낼 수 있어야 가입
            if alarm.alarm_from.coin <alarm.room.deposit:
                return Response(status=status.HTTP_403_FORBIDDEN)

            # 유저 활동 정보 생성
            user_activity_info = UserActivityInfo.objects.create(
                user=alarm.alarm_from,
                room=alarm.room,
                deposit_left=alarm.room.deposit
            )

        alarm.delete() # 알람 삭제
        return Response(status=status.HTTP_204_NO_CONTENT)


# 알람 거절
class AlarmRejectAPI(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            alarm = Alarm.objects.get(id=pk)
            if alarm.alarm_to != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
        except Alarm.DoesNotExist:
            return Response(self, status=status.HTTP_404_NOT_FOUND)

        alarm.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
