from django.urls import reverse
from rest_framework import status
import pytest
from rooms.models import Room

@pytest.mark.django_db
def test_room_create(authenticated_client, create_goal):
    # 유효한 room 생성 요청 데이터
    valid_room_data = {
        "goal_id": create_goal.id,
        "title": "title",
        "detail": "detail",
        "duration": "14 days",
        "favor_offline": True,
        "cert_required": True,
        "cert_detail": "cert detail",
        "penalty_value": 5,
        "deposit": 100
    }

    response = authenticated_client.post(('http://127.0.0.1:8000/api/rooms/create/'), valid_room_data, format='json')

    assert response.status_code == status.HTTP_201_CREATED

    # 잘못된 room 생성 요청 데이터 (보증금이 부족한 경우)
    invalid_room_data = {
        "goal_id": create_goal.id,
        "title": "title",
        "detail": "detail",
        "duration": "14 days",
        "favor_offline": True,
        "cert_required": True,
        "cert_detail": "cert detail",
        "penalty_value": 5,
        "deposit": 100000
    }

    response = authenticated_client.post(('http://127.0.0.1:8000/api/rooms/create/'), invalid_room_data, format='json')

    assert response.status_code == status.HTTP_403_FORBIDDEN

    # 잘못된 room 생성 요청 데이터 (goal이 존재하지 않는 경우)
    invalid_goal_id_room_data = {
        "goal_id": 1000,
        "title": "title",
        "detail": "detail",
        "duration": "14 days",
        "favor_offline": True,
        "cert_required": True,
        "cert_detail": "cert detail",
        "penalty_value": 5,
        "deposit": 100000
    }

    response = authenticated_client.post(('http://127.0.0.1:8000/api/rooms/create/'), invalid_goal_id_room_data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST