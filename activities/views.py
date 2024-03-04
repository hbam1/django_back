from rest_framework import viewsets, status
from .models import MemberAuthentication, Post
from .serializers import MemberAuthenticationSerializer, AuthLogSerializer, FreeBoardPostSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rooms.models import Room
from rooms.permissions import RoomAttendancePermission
from rest_framework.exceptions import PermissionDenied

#인증 제출
class MemberAuthCreateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MemberAuthenticationSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

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

    # pk = room_id
    def get(self, request, pk):
        room = Room.objects.get(pk=pk)
        auth_logs = MemberAuthentication.objects.filter(room=room).filter(is_completed=True).order_by('-created_date')
        serializer = AuthLogSerializer(auth_logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# 자유게시판
class FreeBoardViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, RoomAttendancePermission]
    serializer_class = FreeBoardPostSerializer

    def get_queryset(self):
        # 요청에 포함된 방의 ID를 가져옵니다.
        room_id = self.kwargs.get('room_id')
        # 해당 방에 속한 게시글만 필터링하여 반환합니다.
        return Post.objects.filter(room__id=room_id).order_by('-created_date')

    def perform_create(self, serializer):
        room_id = self.kwargs.get('room_id')
        room = Room.objects.get(pk=room_id)

        # 요청된 방의 master가 현재 사용자가 아닌 경우 에러 처리
        if room.master != self.request.user and serializer.validated_data.get('notice', False):
            raise PermissionDenied("공지를 만들 권한이 없습니다.")

        serializer.save(author=self.request.user, room=room)

    def perform_destroy(self, instance):
        # 글 작성자만 삭제할 수 있도록 확인
        if instance.author != self.request.user:
            raise PermissionDenied("글 작성자만 삭제할 수 있습니다.")

        instance.delete()
