from rest_framework import viewsets, status
from .models import MemberAuthentication, Post, Comment
from .serializers import MemberAuthenticationSerializer, AuthLogSerializer, FreeBoardPostSerializer, CommentSerializer
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