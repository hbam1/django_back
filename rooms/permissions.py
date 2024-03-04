from rest_framework.permissions import BasePermission
from rooms.models import Room

class RoomAdminPermission(BasePermission):
    def has_permission(self, request, view):
        room_id = view.kwargs.get('room_id')
        try:
            room = Room.objects.get(pk=room_id)
            return request.user == room.master
        except Room.DoesNotExist:
            return False

# 게시판 글을 쓸 수 있는 멤버인지 확인
class RoomAttendancePermission(BasePermission):
    def has_permission(self, request, view):
        room_id = view.kwargs.get('room_id')
        try:
            room = Room.objects.get(pk=room_id)
            # 방의 members 필드에 현재 사용자가 포함되어 있는지 확인
            return request.user in room.members.all()
        except Room.DoesNotExist:
            return False
