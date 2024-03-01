from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.core.validators import MinValueValidator


# 헬퍼 클래스
class UserManager(BaseUserManager):
    def create_user(self, email, password, nickname, **kwargs):
        """
        주어진 이메일, 비밀번호 등 개인정보로 User 인스턴스 생성
        """
        if not email:
            raise ValueError('Users must have an email address')
        # 생성 시 nickname 중복 여부도 원칙적으로는 처리해줘야하지만, 랜덤의 경우가 상당히 크기 때문에 일단 보류.
        user = self.model(
            email=email,
            nickname=nickname,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, password=None, **extra_fields):
        """
        주어진 이메일, 비밀번호 등 개인정보로 User 인스턴스 생성
        단, 최상위 사용자이므로 권한을 부여
        """
        superuser = self.create_user(
            email=email,
            password=password,
            nickname=email, # superuser 만들 때 create_user를 부르기 때문에 nickname도 넘겨줘야됨
        )

        superuser.is_staff = True
        superuser.is_superuser = True
        superuser.is_active = True

        superuser.save(using=self._db)
        return superuser

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=False, blank=False, help_text="이메일")
    # null=True일 경우 nickname의 unique 여부를 판단할 때 null은 해당하지 않음.
    nickname = models.CharField(max_length=30, blank=True, null=True, unique=True, help_text="닉네임")
    profile = models.CharField(max_length=255, null=True, blank=True, help_text="소개글")
    profile_image = models.ImageField(upload_to='profile_images/%Y/%m/%d/', null=True, blank=True, help_text="프로필 이미지")
    region = models.CharField(max_length=30, null=True, blank=True, help_text="사는 도시")
    region_detail = models.CharField(max_length=30, null=True, blank=True, help_text="상세 주소")
    fuel = models.FloatField(null=True, blank=True, default=0, validators=[MinValueValidator(0)], help_text="연료")
    new = models.BooleanField(default=True, help_text="신규 회원")
    coin = models.PositiveIntegerField(default=5000, help_text="재화")

    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 헬퍼 클래스 사용
    objects = UserManager()

    # 사용자의 username field는 email으로 설정 (이메일로 로그인)
    USERNAME_FIELD = 'email'