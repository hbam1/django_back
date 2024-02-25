from urllib import request
from rest_framework import viewsets, status
from .serializers import *
from rooms.serializers import RoomDefaultSerializer
from .models import Goal
from alarms.models import Alarm
from rooms.models import Room
from rest_framework.permissions import IsAuthenticated
from .permissions import GoalOwnershipPermission
from rest_framework.views import APIView
from rest_framework.response import Response

# Method import
from elasticsearch_dsl import Search, Q

# 목표 viewset
class GoalViewSet(viewsets.ModelViewSet):
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # 태그 입력
        tag_names = request.data.get("tags")  # str을 가진 list 반환
        for tag_name in tag_names:
            tag = Tag.objects.get(tag_name=tag_name)
            serializer.instance.tags.add(tag)

        # 활동 태그 입력
        activity_tag_names = request.data.get("activity_tags")  # str을 가진 list 반환
        for activity_tag_name in activity_tag_names:
            activity_tag = ActivityTag.objects.get(tag_name=activity_tag_name)
            serializer.instance.activity_tags.add(activity_tag)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        # 현재 유저를 저장
        serializer.save(user=self.request.user)


# 태그 조회
class TagListAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        tags = Tag.objects.all().order_by('-tag_name')
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 활동 태그 조회
class ActivityTagListAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        activity_tags = ActivityTag.objects.all()
        serializer = ActivityTagSerializer(activity_tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 방 생성 시 목표 조회
class GoalListAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        # 로그인된 유저 정보
        user = request.user
        # user가 생성한 목표 리스트
        goals = Goal.objects.filter(user=user).order_by('-title')
        serializer = GoalListSerializer(goals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# 그룹 추천
class GroupRecommendationAPI(APIView):
    # Custom Permission추가 / 기존의 goal_ownership_required 데코레이터 + get_object_or_404 기능을 대체함
    permission_classes = [IsAuthenticated, GoalOwnershipPermission]

    def get(self, request, goal_id):
        goal = Goal.objects.get(pk=goal_id)
        tag_ids = [tag.id for tag in goal.tags.all()]
        activity_tag_ids = [tag.id for tag in goal.activityTags.all()]
        alarms = Alarm.objects.filter(goal__pk=goal_id)
        is_pending = [alarm.room.pk for alarm in alarms]

        must_queries = []
        should_queries = []
        must_not_queries = []

        # 최소조건 명시: 분류 태그 중 하나는 같아야 함
        at_least_tag = Q('nested', path='tags', query=Q('terms', **{'tags.tag_id': tag_ids}), boost=0)
        must_queries.append(at_least_tag)

        # 가중 조건: 검색결과에 점수를 추가적으로 부여하는 로직들
        for tag_id in tag_ids:
            tag_query = Q('nested', path='tags', query=Q('terms', **{'tags.tag_id': [tag_id]}), boost=3)
            should_queries.append(tag_query)

        for activity_tag_id in activity_tag_ids:
            activity_tag_query = Q('nested', path='activityTags', query=Q('terms', **{'activityTags.tag_id': [activity_tag_id]}), boost=3)
            should_queries.append(activity_tag_query)

        # favor_offline이 같을 경우 높은 점수
        offline_boost_query = Q('term', favor_offline={'value': goal.favor_offline, 'boost': 2})
        should_queries.append(offline_boost_query)
        
        # region, region_detail에서 겹치는 단어가 많으면 높은 점수
        if goal.favor_offline:
            region_boost_query = Q('match', master__region={'query': goal.user.region, 'boost': 2})
            detail_boost_query = Q('match', master__region_detail={'query': goal.user.region_detail, 'boost': 2})
            should_queries.append(region_boost_query)
            should_queries.append(detail_boost_query)

        # title, detail-content에서 겹치는 단어가 많으면 높은 점수
        title_boost_query = Q('match', title={'query': goal.title, 'boost': 2})
        content_boost_query = Q('match', detail={'query': goal.content, 'boost': 2})
        should_queries.append(title_boost_query)
        should_queries.append(content_boost_query)

        # is_active가 False일때만 추천 목록에 반영 
        is_active_query = Q('term', is_active=False)
        must_queries.append(is_active_query)

        # Goal의 user는 Room의 master가 아니여야함. 즉 자기자신이 개설한 방에 대해서는 목록에 반영하지 않음.
        user_master_mismatch_query = Q('term', master__id=goal.user.id)
        must_not_queries.append(user_master_mismatch_query)

        final_query = Q('bool', must=must_queries, should=should_queries, must_not=must_not_queries)
        s = Search(index='rooms').query(final_query)
        
        # 내림차순 정렬
        s = s.sort({'_score': {'order': 'desc'}})
        response = s.execute()

        # Score 내림차순 정렬 상태를 유지하며 인스턴스화
        hit_scores = {hit.meta.id : hit.meta.score for hit in response if hit.meta.id not in is_pending}
        rooms = sorted(Room.objects.filter(pk__in=hit_scores.keys()), key=lambda room: hit_scores[str(room.pk)], reverse=True)
        
        # 직렬화
        serializer = RoomDefaultSerializer(rooms, many=True)
        return Response(serializer.data, status=200)
