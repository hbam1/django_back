from rest_framework.permissions import BasePermission
from .models import Goal

class GoalOwnershipPermission(BasePermission):
    def has_permission(self, request, view):
        goal_id = view.kwargs.get('goal_id')
        try:
            goal = Goal.objects.get(pk=goal_id)
            return request.user == goal.user
        except Goal.DoesNotExist:
            return False