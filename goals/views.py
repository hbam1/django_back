from django.http import Http404
from rest_framework import viewsets, status
from .serializers import *
from rooms.serializers import RoomListSerializer
from .models import *
from alarms.models import Alarm
from rooms.models import Room
from rest_framework.permissions import IsAuthenticated
from .permissions import GoalOwnershipPermission
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


# Method import
from elasticsearch_dsl import Search, Q

# 목표 viewset
class GoalViewSet(viewsets.ModelViewSet):
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer

    def get_permissions(self):
        if self.action == 'delete':
            permission_classes = [IsAuthenticated, GoalOwnershipPermission]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING),
                'content': openapi.Schema(type=openapi.TYPE_STRING),
                'tags': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                'activity_tags': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING))
            }
        ),
        responses={
            201: 'Created',
            400: 'Bad Request'
        },
        tags=['목표 생성']
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # 태그 입력
        tag_names = request.data.get("tags")  # str을 가진 list 반환
        if tag_names is not None:
            for tag_name in tag_names:
                try:
                    tag = Tag.objects.get(tag_name=tag_name)
                    serializer.instance.tags.add(tag)
                except Tag.DoesNotExist:
                    # 태그를 찾지 못할 때 에러 처리
                    return Response({"error": f"Tag '{tag_name}' does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # tag_names가 None일 때 처리
            return Response({"error": "Tag names are missing"}, status=status.HTTP_400_BAD_REQUEST)

        # 활동 태그 입력
        activity_tag_names = request.data.get("activity_tags")  # str을 가진 list 반환
        if activity_tag_names is not None:
            for activity_tag_name in activity_tag_names:
                try:
                    activity_tag = ActivityTag.objects.get(tag_name=activity_tag_name)
                    serializer.instance.activity_tags.add(activity_tag)
                except ActivityTag.DoesNotExist:
                    # 활동 태그를 찾지 못할 때 에러 처리
                    return Response({"error": f"Activity tag '{activity_tag_name}' does not exist"},
                                    status=status.HTTP_400_BAD_REQUEST)
        else:
            # activity_tag_names가 None일 때 처리
            return Response({"error": "Activity tag names are missing"}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        # 현재 유저를 저장
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        tags=["목표 리스트"],
        responses={
            status.HTTP_200_OK: GoalSerializer(many=True)
        }
    )
    def list(self, request):
        user = request.user
        goals = Goal.objects.filter(user=user).order_by('-id')
        serializer = self.get_serializer(goals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, goal_id):
        goal = Goal.objects.get(pk=goal_id)
        goal.delete()
        return Response(status=204)

# 태그 조회
class ParentTagListAPI(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['태그 조회'],
        operation_summary='부모 태그 목록 조회',
        responses={status.HTTP_200_OK: TagSerializer(many=True)}
    )
    def get(self, request):
        tags = Tag.objects.filter(parent_tag=None)
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubTagListAPI(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['태그 조회'],
        operation_summary='부모 태그에 속하는 하위 태그 목록 조회',
        responses={status.HTTP_200_OK: TagSerializer(many=True)}
    )
    def get(self, request, pk):
        tags = Tag.objects.filter(parent_tag__id=pk)
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)   

# 활동 태그 조회
class ActivityTagListAPI(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['활동 태그 조회'],
        operation_summary='활동 태그 목록 조회',
        responses={status.HTTP_200_OK: ActivityTagSerializer(many=True)}
    )
    def get(self, request):
        activity_tags = ActivityTag.objects.all()
        serializer = ActivityTagSerializer(activity_tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 그룹 추천
class GroupRecommendationAPI(APIView):
    # Custom Permission추가 / 기존의 goal_ownership_required 데코레이터 + get_object_or_404 기능을 대체함
    permission_classes = [IsAuthenticated, GoalOwnershipPermission]

    def get(self, request, goal_id):
        goal = Goal.objects.get(pk=goal_id)
        tag_ids = [tag.id for tag in goal.tags.all()]
        activity_tag_ids = [tag.id for tag in goal.activity_tags.all()]
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
            activity_tag_query = Q('nested', path='activity_tags', query=Q('terms', **{'activity_tags.tag_id': [activity_tag_id]}), boost=3)
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
        hit_scores = {hit.meta.id : hit.meta.score for hit in response if int(hit.meta.id) not in is_pending}
        rooms = sorted(Room.objects.filter(pk__in=hit_scores.keys()), key=lambda room: hit_scores[str(room.pk)], reverse=True)
        
        # 직렬화
        serializer = RoomListSerializer(rooms, many=True)
        return Response(serializer.data, status=200)


# 달성 보고 리스트
class AchievementReportListAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        achievement_reports = AchievementReport.objects.all().order_by('-pk')
        serializer = AchievementReportSerializer(achievement_reports, many = True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

# 달성 보고 디테일
class AchievementReportDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return AchievementReport.objects.get(pk=pk)
        except AchievementReport.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        achievement_report = self.get_object(pk)
        serializer = AchievementReportSerializer(achievement_report)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# 달성보고 생성
class AchievementReportCreateAPI(APIView):
    permission_classes = [IsAuthenticated, GoalOwnershipPermission]

    def post(self, request, goal_id):
        goal = Goal.objects.get(pk=goal_id)
        if goal.is_completed:
            return Response({'error': '이미 보고가 작성된 목표입니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = AchievementReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(goal=goal)
            goal.is_completed = True
            goal.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

