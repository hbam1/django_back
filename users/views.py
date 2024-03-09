import jwt
from rest_framework.views import APIView
from .serializers import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework import status, viewsets
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.conf import settings
import random
import string
from goals.models import Goal
from rest_framework.permissions import IsAuthenticated


# 회원가입
class RegisterAPI(APIView):
    # 인증 필수
    def get_permissions(self):
        if self.request.method == 'PATCH':
            return [IsAuthenticated()]
        return []

    def post(self, request):
        # 이메일 중복이면 생성불가
        if User.objects.filter(email=request.data['email']).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSignUpSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # 랜덤한 닉네임 생성
            nickname = ''.join(random.choice(string.ascii_lowercase) for _ in range(8))
            serializer.validated_data["nickname"] = nickname
            # password2 제거
            serializer.validated_data.pop("password2")
            # user 생성
            user = User.objects.create_user(**serializer.validated_data)

            # jwt 토큰 접근
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            res = Response(
                {
                    "message": "register successs",
                    "token": {
                        "access": access_token,
                        "refresh": refresh_token,
                    },
                },
                status=status.HTTP_200_OK,
            )

            return res
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 회원가입 후 닉네임, 사는 지역 업데이트
    def patch(self, request):
        user = request.user
        serializer = UserSignupDetailSerializer(user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthAPIView(APIView):
    # 인증 필수
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return []

    # 메인 페이지 유저 정보 확인
    def get(self, request):
        user = request.user
        goals = Goal.objects.filter(user=user)
        # 목표의 수
        all_goals = goals.count()
        # 달성 목표
        completed_goals = goals.filter(is_completed=True).count()

        # 사용자 정보와 목표 수를 직렬화하여 데이터 생성
        data = {
            'nickname': user.nickname,
            'fuel': user.fuel,
            'all_goals': all_goals,
            'completed_goals': completed_goals,
        }
        serializer = UserMainInfoSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # 로그인
    def post(self, request):
    	# 유저 인증
        user = authenticate(
            email=request.data.get("email"), password=request.data.get("password")
        )
        # 이미 회원가입 된 유저일 때
        if user is not None:
            # jwt 토큰 접근
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            res = Response(
                {
                    "message": "login success",
                    "token": {
                        "access": access_token,
                        "refresh": refresh_token,
                    },
                },
                status=status.HTTP_200_OK,
            )
            return res
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


# 마이페이지용 회원정보조회
class UserDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get(self, request):
        try:
            user_instance = self.get_object()
            serializer = UserDetailInfoSerializer(user_instance, context={'request': request})
            serialized_data = serializer.data
            return Response(serialized_data, status=status.HTTP_200_OK)
        except Exception as e:
            error_message = str(e)
            print(f"Error in UserDetailAPI: {error_message}")
            # Internal erro 수정 필요
            return Response({"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request):
        # JWT에서 인증된 사용자 정보를 가져옵니다.
        token = request.headers.get('Authorization').split(' ')[1]
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = decoded_token.get('user_id')

        # 해당 사용자 정보를 가져옵니다.
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response("사용자를 찾을 수 없습니다.", status=status.HTTP_404_NOT_FOUND)

        # 전달된 데이터로 사용자 정보를 업데이트합니다.
        serializer = UserDetailInfoSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            # 후에 리턴값은 변경
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
