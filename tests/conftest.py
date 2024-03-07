import pytest
from rest_framework.test import APIClient
from users.models import User
from goals.models import Tag, ActivityTag,Goal

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticated_user():
    user = User.objects.create_user(username='test_user', email='test@example.com', password='testpassword', nickname="testnickname")
    return user

@pytest.fixture
def authenticated_client(api_client, authenticated_user):
    client = api_client  # 함수 호출을 수정함
    client.force_authenticate(user=authenticated_user)
    return client

@pytest.fixture
def create_tags():
    # 부모 태그 생성
    parent_tag = Tag.objects.create(tag_name='parent_tag')

    # 자식 태그 생성
    child_tag1 = Tag.objects.create(tag_name='child_tag1', parent_tag=parent_tag)
    child_tag2 = Tag.objects.create(tag_name='child_tag2', parent_tag=parent_tag)

    # 활동 태그 생성
    activity_tag1 = ActivityTag.objects.create(tag_name='activity_tag1')
    activity_tag2 = ActivityTag.objects.create(tag_name='activity_tag2')

    return {
        'parent_tag': parent_tag,
        'child_tag1': child_tag1,
        'child_tag2': child_tag2,
        'activity_tag1': activity_tag1,
        'activity_tag2': activity_tag2
    }

@pytest.fixture
def create_goal(authenticated_user, create_tags):
    # create_tags fixture로부터 생성된 태그 객체에 접근하여 데이터 생성
    parent_tag = create_tags['parent_tag']
    child_tag1 = create_tags['child_tag1']
    activity_tag1 = create_tags['activity_tag1']

    test_goal = Goal.objects.create(
        id=1,
        user=authenticated_user,
        title="Test Goal",
        content="Test Content",
        favor_offline=False,
        is_in_group=False,
        is_completed=False,
        belonging_group_id=None
    )

    # ManyToManyField에 대한 값을 설정
    test_goal.tags.set([parent_tag, child_tag1])
    test_goal.activity_tags.set([activity_tag1])

    return test_goal