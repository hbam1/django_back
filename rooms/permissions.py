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