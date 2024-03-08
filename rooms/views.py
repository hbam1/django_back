from rest_framework import viewsets, status
from rooms.models import Room
from alarms.models import Alarm
from goals.models import Goal
from activities.models import UserActivityInfo
from .serializers import RoomCreateSerializer, GoalListSerializer, RoomListSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import RoomAdminPermission
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Sum
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Method import
from elasticsearch_dsl import Search, Q

# 방 생성 시 목표 조회
class GoalListAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        # 로그인된 유저 정보
        user = request.user
        # user가 생성한 목표 리스트
        goals = Goal.objects.filter(user=user, is_in_group=False, is_completed=False).order_by('-title')
        serializer = GoalListSerializer(goals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 방 생성
class RoomCreateAPI(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["방 생성"],
        request_body=RoomCreateSerializer,
        manual_parameters=[
            openapi.Parameter('goal_id', openapi.IN_QUERY, description="Goal ID", type=openapi.TYPE_INTEGER, required=True)
        ],
        responses={
            status.HTTP_400_BAD_REQUEST: "Goal Does Not Exist",
            status.HTTP_403_FORBIDDEN: "Deposit not allowed",
            status.HTTP_201_CREATED: "Room Created"
        }
    )
    def post(self, request):
        goal_id = request.data.pop('goal_id', None)
        serializer = RoomCreateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                goal = Goal.objects.get(id=goal_id)
            except ObjectDoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            # 방장의 보증금 확인
            if request.user.coin < request.data.get("deposit"):
                return Response(status=status.HTTP_403_FORBIDDEN)

            # goal로부터 태그들 갖고 옴
            tags = goal.tags.all()
            activity_tags = goal.activity_tags.all()

            room = serializer.save(master=request.user)
            # 방 객체를 저장한 후에 ManyToMany 필드에 연결된 모델의 인스턴스를 추가
            room.tags.add(*tags)
            room.activity_tags.add(*activity_tags)
            room.members.add(request.user)
            goal.is_in_group = True
            goal.belonging_group_id = room.id

            # 유저 활동 정보 생성
            user_activity_info = UserActivityInfo.objects.create(
                user=request.user,
                room=room,
                deposit_left=room.deposit
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# 유저 추천
class MemberRecommendationAPI(APIView):
    # Custom Permission추가 / 기존의 room_admin_required 데코레이터 + get_object_or_404 기능을 대체함
    permission_classes = [IsAuthenticated, RoomAdminPermission]

    def get(self, request, room_id):
        room = Room.objects.get(pk=room_id)
        tag_ids = [tag.id for tag in room.tags.all()]
        activity_tags_ids = [tag.id for tag in room.activity_tags.all()]
        alarms = Alarm.objects.filter(room__pk=room_id).exclude(goal=None)
        is_pending = [alarm.goal.pk for alarm in alarms]

        must_queries = []
        should_queries = []
        must_not_queries = []

        # 최소조건 명시 : 분류 태그 중 하나는 같아야 함(사실 이는 원시태그로 한정되긴 함)
        # group에 가입되지 않은 목표여야 함 
        at_least = Q('nested', path='tags', query=Q('terms', **{'tags.tag_id': tag_ids}), boost=0)
        in_group_check_query = Q('term', is_in_group = False)
        
        # 아직 완료되지 않은 목표여야 함
        is_completed_query = Q('term', is_completed=False)
        must_queries.append(at_least)
        must_queries.append(in_group_check_query)
        must_queries.append(is_completed_query)

        # 가중 조건 : 검색결과에 점수를 추가적으로 부여하는 로직들
        for tag_id in tag_ids:
            tag_query = Q('nested', path='tags', query=Q('terms', **{'tags.tag_id': [tag_id]}), boost=3)
            should_queries.append(tag_query)

        for activity_tag_id in activity_tags_ids:
            activity_tag_query = Q('nested', path='activity_tags', query=Q('terms', **{'activity_tags.tag_id': [activity_tag_id]}), boost=3)
            should_queries.append(activity_tag_query)

        # favor_offline이 일치하면 높은 점수
        offline_boost_query = Q('term', favor_offline={'value': room.favor_offline, 'boost': 2})
        should_queries.append(offline_boost_query)

        # region, region_detail에서 겹치는 단어가 많으면 높은 점수
        if room.favor_offline:
            region_boost_query = Q('match', user__region={'query': room.master.region, 'boost': 2})
            detail_boost_query = Q('match', user__region_detail={'query': room.master.region_detail, 'boost': 2})
            should_queries.append(region_boost_query)
            should_queries.append(detail_boost_query)

        # title, detail-content에서 겹치는 단어가 많으면 높은 점수
        title_boost_query = Q('match', title={'query': room.title, 'boost': 2})
        content_boost_query = Q('match', content={'query': room.detail, 'boost': 2})
        should_queries.append(title_boost_query)
        should_queries.append(content_boost_query)

        # 방장 자신의 Goal이 아니어야 함
        master_detecting_query = Q('term', **{'user.id': room.master.pk})
        must_not_queries.append(master_detecting_query)

        final_query = Q('bool', must=must_queries, should=should_queries, must_not=must_not_queries)
        s = Search(index='goals').query(final_query)

        # 내림차순 정렬
        s = s.sort({'_score': {'order': 'desc'}})
        response = s.execute()

        # Score 내림차순 정렬 상태를 유지하며 인스턴스화
        hit_scores = {hit.meta.id: hit.meta.score for hit in response if int(hit.meta.id) not in is_pending}
        goals = sorted(Goal.objects.filter(pk__in=hit_scores.keys()), key=lambda goal: hit_scores[str(goal.pk)], reverse=True)
        
        # 직렬화
        serializer = GoalListSerializer(goals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# 방 활성화
class RoomActivateAPI(APIView):
    permission_classes = [IsAuthenticated, RoomAdminPermission]
    def post(self, request, room_id):
        room = Room.objects.get(pk=room_id)
        room.is_active = True
        room.closing_date = timezone.now() + room.duration
        return Response(status=status.HTTP_200_OK)

# 방 활동종료 및 삭제
class RoomClosureAPI(APIView):
    permission_classes = [IsAuthenticated, RoomAdminPermission]
    def delete(self, request, room_id):
        try:
            room = Room.objects.get(pk=room_id)

            # 징수한 벌금을 인증 성과에 따라 분배
            if room.cert_required:
                distribute_reward(room)

            # 폐쇄에 따른 로직 => 모든 멤버의 Goal 정보 수정 및 초기화
            members = room.members.all()
            for member in members:
                target_goal = member.goal.get(belonging_group_id=room_id)
                target_goal.is_in_group = False
                target_goal.belonging_group_id = None
                target_goal.save()

            room.delete()
            # return data는 없고, front에서 status=204 응답을 받으면 컴포넌트 삭제
            return Response(status=204)
        except Exception:
            return Response(status=400)

# 보상금을 분배하는 로직
def distribute_reward(room: Room):
    activity_infos_in_room = room.activity_infos.all()
    total_count = activity_infos_in_room.aggregate(total_count=Sum('authentication_count'))['total_count']
    # 한 건의 인증도 이루어지지 않음 / ZeroDivision 예외 방지
    if total_count == 0:
        return
    for activity_info in activity_infos_in_room:
        user = activity_info.user
        activity_count = activity_info.authentication_count
        penalty_bank = room.penalty_bank
        reward = (penalty_bank * activity_count) / total_count
        user.coin += int(reward)
        user.coin += activity_info.deposit_left
        user.save()

# 그룹 리스트
class RoomListAPI(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['그룹 리스트 조회'],
        operation_summary='그룹 리스트 조회',
        responses={status.HTTP_200_OK: RoomListSerializer(many=True)}
    )
    def get(self, request):
        rooms = Room.objects.filter(members=request.user)
        serializer = RoomListSerializer(rooms, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
