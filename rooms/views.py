from django.shortcuts import render
from rest_framework import viewsets, status
from goals.models import Tag, ActivityTag
from rooms.models import Room
from alarms.models import Alarm
from goals.models import Goal
from activities.models import UserActivityInfo
from .serializers import RoomSerializer
from goals.serializers import GoalDefaultSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import RoomAdminPermission
from rest_framework.response import Response
from rest_framework.views import APIView

# Method import
from elasticsearch_dsl import Search, Q

# 방 생성
class RoomCreateAPI(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            room = serializer.save(master=request.user)

            # 태그 입력
            try:
                tag_names = request.data.get("tags")  # str을 가진 list 반환
            except tag_names.DoesNotExist():
                return Response(status=status.HTTP_400_BAD_REQUEST)

            for tag_name in tag_names:
                tag = Tag.objects.get(tag_name=tag_name)
                serializer.instance.tags.add(tag)

            # 활동 태그 입력
            try:
                activity_tag_names = request.data.get("activity_tags")  # str을 가진 list 반환
            except activity_tag_names.DoesNotExists():
                return Response(status=status.HTTP_400_BAD_REQUEST)

            for activity_tag_name in activity_tag_names:
                activity_tag = ActivityTag.objects.get(tag_name=activity_tag_name)
                serializer.instance.activity_tags.add(activity_tag)

            # 방장의 보증금 확인
            if request.user.coin < room.deposit:
                return Response(status=status.HTTP_403_FORBIDDEN)

            # 유저 활동 정보 생성
            user_activity_info = UserActivityInfo.objects.create(
                user=request.user,
                room=room,
                deposit_left=room.deposit
            )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MemberRecommendationAPI(APIView):
    # Custom Permission추가 / 기존의 room_admin_required 데코레이터 + get_object_or_404 기능을 대체함
    permission_classes = [IsAuthenticated, RoomAdminPermission]

    def get(self, request, room_id):
        room = Room.objects.get(pk=room_id)
        tag_ids = [tag.id for tag in room.tags.all()]
        activity_tags_ids = [tag.id for tag in room.activityTags.all()]
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
            activity_tag_query = Q('nested', path='activityTags', query=Q('terms', **{'activityTags.tag_id': [activity_tag_id]}), boost=3)
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
        hit_scores = {hit.meta.id: hit.meta.score for hit in response if hit.meta.id not in is_pending}
        goals = sorted(Goal.objects.filter(pk__in=hit_scores.keys()), key=lambda goal: hit_scores[str(goal.pk)], reverse=True)
        
        # 직렬화
        serializer = GoalDefaultSerializer(goals, many=True)
        return Response(serializer.data, status=200)