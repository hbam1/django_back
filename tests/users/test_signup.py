import pytest
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User

@pytest.mark.django_db
class RegisterAPITest(APITestCase):
    def test_register_success(self):
        data = {
            'email': 'test@example.com',
            'password': 'testpassword',
            'password2': 'testpassword',  # 패스워드 확인
            'nickname': 'testuser',  # 닉네임 추가
        }

        response = self.client.post('http://127.0.0.1:8000/api/users/register/', data, format='json')  # 회원가입 요청 보내기
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # 응답 상태코드 확인

        # 회원가입이 성공했는지 확인
        self.assertTrue('token' in response.data)
        self.assertTrue('access' in response.data['token'])
        self.assertTrue('refresh' in response.data['token'])

        # 등록된 사용자가 있는지 확인
        self.assertTrue(User.objects.filter(email=data['email']).exists())

    def test_register_duplicate_email(self):
        # 이미 등록된 이메일로 회원가입을 시도할 경우의 테스트
        User.objects.create_user(email='existing@example.com', password='testpassword', nickname="testname")
        data = {
            'email': 'existing@example.com',
            'password': 'testpassword',
            'password2': 'testpassword',  # 패스워드 확인
            'nickname': 'testuser2',  # 닉네임 추가
        }

        response = self.client.post('http://127.0.0.1:8000/api/users/register/', data, format='json')  # 회원가입 요청 보내기
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # 응답 상태코드 확인

    def test_register_password_mismatch(self):
        data = {
            'email': 'test@example.com',
            'password': 'testpassword',
            'password2': 'differentpassword',  # 다른 패스워드
            'nickname': 'testuser',  # 닉네임 추가
        }

        response = self.client.post('http://127.0.0.1:8000/api/users/register/', data, format='json')  # 회원가입 요청 보내기
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # 응답 상태코드 확인
