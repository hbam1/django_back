import pytest
from users.models import User
from rest_framework.test import APIClient
from rest_framework import status

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
def test_user_login(api_client):
    # 테스트에 필요한 사용자 생성
    email = "test@example.com"
    password = "testpassword"
    nickname= "1234"
    User.objects.create_user(email=email, password=password, nickname=nickname)

    # 올바른 이메일과 비밀번호로 로그인을 시도합니다.
    response = api_client.post("http://127.0.0.1:8000/api/users/auth/", {"email": email, "password": password})

    # 응답이 올바른지 확인합니다.
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data["token"]
    assert "refresh" in response.data["token"]

    # 잘못된 비밀번호로 로그인을 시도합니다.
    response = api_client.post("http://127.0.0.1:8000/api/users/auth/", {"email": email, "password": "wrongpassword"})
    # 응답이 올바른지 확인합니다.
    assert response.status_code == status.HTTP_400_BAD_REQUEST
