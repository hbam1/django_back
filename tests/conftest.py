import pytest
from rest_framework.test import APIClient
from users.models import User
from goals.models import Tag, ActivityTag

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticated_client(api_client):
    client = api_client  # 함수 호출을 수정함
    user = User.objects.create_user(username='test_user', email='test@example.com', password='testpassword', nickname="testnickname")
    client.force_authenticate(user=user)
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