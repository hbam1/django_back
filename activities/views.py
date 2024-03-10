from rest_framework import viewsets, status
from .models import MemberAuthentication, Post, Comment, Authentication
from .serializers import MemberAuthenticationSerializer, AuthLogSerializer, FreeBoardPostSerializer, CommentSerializer, AuthListSerializer
from users.serializers import MemberListSerializer, UserSearchResultSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rooms.models import Room
from goals.models import Goal
from users.models import User 
from rooms.permissions import RoomAttendancePermission, RoomAdminPermission
from rest_framework.exceptions import PermissionDenied
from .tasks import create_periodic_task
from django.db.models import Case, When, Value, IntegerField

class MemberListAPI(APIView):
    permission_classes = [IsAuthenticated, RoomAttendancePermission]
    
    def get(self, request, room_id):
        room = Room.objects.get(id=room_id)
        members_ordered = room.members.annotate(
        is_master=Case(
        When(id=room.master.id, then=Value(0)),
            default=Value(1),
            output_field=IntegerField(),
        )).order_by('is_master')
        serializer = MemberListSerializer(members_ordered, many=True)

        member_data_dict = []
        for member_data_origin in serializer.data:
            member_data = member_data_origin.copy()
            member_data['deposit_left'] = room.activity_infos.get(user__id=member_data['id']).deposit_left
            member_data['goal'] = Goal.objects.filter(user__id=member_data['id']).get(belonging_group_id=room_id).title
            member_data_dict.append(member_data)
        
        return Response(member_data_dict, status=status.HTTP_200_OK)


# 그룹장이 만드는 인증 Viewset
class AuthenticationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated] 
    serializer_class = AuthListSerializer
    queryset = Authentication.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        data = self.request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

    def perform_destroy(self, instance):
        auth_id = self.kwargs['pk']
        try:
            authentication = Authentication.objects.get(id=auth_id)
            authentication.delete()
            return Response(status=204)
        except Authentication.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


#인증 제출 및 인증 리스트
class MemberAuthAPI(APIView):
    permission_classes = [IsAuthenticated, RoomAttendancePermission]

    def get(self, request, room_id):
        auths = Authentication.objects.filter(room__id=room_id)
        serializer = AuthListSerializer(auths, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        serializer = MemberAuthenticationSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

#인증 수락
class MemberAuthAcceptAPI(APIView):
    permission_classes = [IsAuthenticated, RoomAdminPermission]

    def put(self, request, room_id, pk):
        auth = MemberAuthentication.objects.get(id=pk)
        auth.is_auth = True
        auth.is_completed = True
        auth.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
    

#인증 거절
class MemberAuthRejectAPI(APIView):
    permission_classes = [IsAuthenticated, RoomAdminPermission]

    def put(self, request, room_id, pk):
        auth = MemberAuthentication.objects.get(id=pk)
        auth.is_completed = True
        auth.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


#인증 리스트
class AuthListAPI(APIView):
    permission_classes = [IsAuthenticated,RoomAttendancePermission]

    def get(self, request, room_id):
        auths = Authentication.objects.filter(room__id=room_id)
        serializer = AuthListSerializer(auths, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

#로그 list
class LogListAPI(APIView):
    permission_classes = [IsAuthenticated, RoomAttendancePermission]

    def get(self, request, room_id):
        room = Room.objects.get(id=room_id)
        auth_logs = MemberAuthentication.objects.filter(room=room).filter(is_completed=True).order_by('-created_date')
        serializer = AuthLogSerializer(auth_logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# 인증 관리 페이지 -> 인증 리스트
class UncompletedAuthListAPI(APIView):
    permission_classes = [IsAuthenticated, RoomAdminPermission]

    def get(self, request, room_id):
        auths = MemberAuthentication.objects.filter(room__id=room_id).filter(is_completed=False)
        serializer = AuthLogSerializer(auths, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# 직접 초대 -> 검색 기능
class SearchUsersAPI(APIView):
    def get(self, request, room_id):
        nickname = request.GET.get('nickname')
        room_members = Room.objects.get(pk=room_id).members.all()
        users = User.objects.filter(nickname__icontains=nickname).exclude(pk__in=room_members.values_list('pk', flat=True))
        serializer = UserSearchResultSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# 자유게시판
class FreeBoardViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, RoomAttendancePermission]
    serializer_class = FreeBoardPostSerializer

    def get_queryset(self):
        # 요청에 포함된 방의 ID를 가져옵니다.
        room_id = self.kwargs.get('room_id')
        # 해당 방에 속한 게시글만 필터링하여 반환합니다.
        return Post.objects.filter(room__id=room_id).order_by('-created_at')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        user_id = request.user.id
        data = serializer.data
        # 프론트에서 현재 로그인한 유저의 정보를 토대로 좋아요의 상태를 설정
        data['current_user_id'] = user_id
        return Response(data, status=status.HTTP_200_OK)

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

    def perform_update(self, serializer):
        instance = self.get_object()

        # 작성자만 수정할 수 있도록 확인
        if instance.author != self.request.user:
            raise PermissionDenied("글 작성자만 업데이트할 수 있습니다.")

        serializer.save()


# 자유게시판 게시글 댓글
class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, RoomAttendancePermission]
    serializer_class = CommentSerializer

    def get_queryset(self):
        # 요청에 포함된 게시글의 ID를 가져옵니다.
        post_id = self.kwargs.get('post_id')
        # 해당 게시글에 속한 댓글만 필터링하여 반환합니다.
        return Comment.objects.filter(post__id=post_id).order_by('-created_at')

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = Post.objects.get(pk=post_id)

        serializer.save(author=self.request.user, post=post)

    def perform_destroy(self, instance):
        # 댓글 작성자만 삭제할 수 있도록 확인
        if instance.author != self.request.user:
            raise PermissionDenied("댓글 작성자만 삭제할 수 있습니다.")

        instance.delete()

    def perform_update(self, serializer):
        instance = self.get_object()

        # 작성자만 수정할 수 있도록 확인
        if instance.author != self.request.user:
            raise PermissionDenied("댓글 작성자만 수정할 수 있습니다.")

        serializer.save()


class LikePostAPI(APIView):
    permission_classes = [IsAuthenticated, RoomAttendancePermission]

    def patch(self, request):
        post_id = request.data.get('post_id')
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # 본인이 작성한 글에는 좋아요 불가
        if post.author == self.request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        user = self.request.user
        if user in post.voter.all():
            post.voter.remove(user)  # 이미 좋아요를 한 경우, 좋아요 취소
        else:
            post.voter.add(user)  # 좋아요를 하지 않은 경우, 좋아요 추가

        return Response(status=status.HTTP_200_OK)


class LikeCommentAPI(APIView):
    permission_classes = [IsAuthenticated, RoomAttendancePermission]

    def patch(self, request):
        comment_id = request.data.get('comment_id')
        try:
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        # 본인이 작성한 글에는 좋아요 불가
        if comment.author == self.request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        user = self.request.user
        if user in comment.voter.all():
            comment.voter.remove(user)  # 이미 좋아요를 한 경우, 좋아요 취소
        else:
            comment.voter.add(user)  # 좋아요를 하지 않은 경우, 좋아요 추가

        return Response(status=status.HTTP_200_OK)


# 그룹 관리 관련 API
    
# 추방
class ExpelMemberAPI(APIView):
    permission_classes = [IsAuthenticated, RoomAdminPermission]

    def put(self, request, room_id, member_id):
        try:
            room = Room.objects.get(pk=room_id)
            member = room.members.get(pk=member_id)

            # 추방에 따른 로직 => 관련 정보 수정 및 초기화
            target_goal = member.goal.filter(belonging_group_id=room_id).first()
            target_goal.is_in_group = False
            target_goal.belonging_group_id = None
            target_goal.save()

            # 필드에서 삭제
            room.members.remove(member)

            # User Activity Info에 따라 로직 처리
            user_info = room.activity_infos.all().get(user=member)

            # 강퇴시 전액 환급
            member.coin += room.deposit
            member.save()
            room.penalty_bank -= (room.deposit - user_info.deposit_left)
            room.save()

            # User Activity Info도 삭제
            user_info.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except Room.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

# 관리권한 이전 
class TransferMasterAPI(APIView):
    permission_classes = [IsAuthenticated, RoomAdminPermission]

    def put(self, request, room_id, member_id):
        try:
            room = Room.objects.get(pk=room_id)
            new_master = room.members.get(pk=member_id)
            room.master = new_master
            room.save()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except Room.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


# 방의 주기적인 인증 생성
class CreateAutoAuthenticationAPI(APIView):
    permission_classes = [IsAuthenticated, RoomAdminPermission]

    def post(self, request, room_id):
        user_id = self.request.user.id
        day_of_week = request.data.get('day_of_week')
        hour = request.data.get('hour')
        minute = request.data.get('minute')
        auth_duration = request.data.get('auth_duration')

        # Schedule the authentication task using Celery
        create_periodic_task(room_id, user_id, day_of_week, hour, minute, auth_duration)

        return Response({'message': 'Authentication scheduled successfully.'}, status=status.HTTP_200_OK)
