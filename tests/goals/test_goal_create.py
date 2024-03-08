import pytest
from rest_framework import status
from goals.models import Goal

@pytest.mark.django_db
def test_goal_create(authenticated_client, create_tags):
    # create_tags fixture로부터 생성된 태그 객체에 접근하여 데이터 생성
    parent_tag = create_tags['parent_tag']
    child_tag1 = create_tags['child_tag1']
    activity_tag1 = create_tags['activity_tag1']

    # 유효한 goal 데이터
    valid_goal_data = {
        "title": "Test Goal",
        "content": "This is a test goal",
        "tags": [parent_tag.tag_name, child_tag1.tag_name],  # 태그 이름 리스트
        "activity_tags": [activity_tag1.tag_name]  # 활동 태그 이름 리스트
    }

    response = authenticated_client.post('http://127.0.0.1:8000/api/goals/', valid_goal_data, format='json')

    assert response.status_code == status.HTTP_201_CREATED

    # 생성된 goal이 데이터베이스에 있는지 확인
    assert Goal.objects.filter(title="Test Goal").exists()

    # 잘못된 goal 데이터 (태그 없음)
    invalid_goal_data = {
        "title": "Invalid Test Goal",
        "content": "This is an invalid test goal"
    }

    response = authenticated_client.post('http://127.0.0.1:8000/api/goals/', invalid_goal_data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST