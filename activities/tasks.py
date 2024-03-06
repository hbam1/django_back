from celery import Celery
from datetime import timedelta
from django.db import transaction
from users.models import User
from .models import Authentication
from rooms.models import Room
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from django.utils.timezone import now

app = Celery()

# 인증을 생성
@app.task
def create_authentication(room_id, user_id, day_of_week, auth_duration, **kwargs):
    # 현재 시간을 가져옵니다.
    current_time = now()

    # 현재 시간이 방의 수명을 넘었으면 인증 생성하지 않음
    closing_date = Room.objects.get(id=room_id).closing_date
    if current_time > closing_date:
        # 만료된 스케줄을 삭제합니다.
        revoke_schedules(room_id, user_id, day_of_week, auth_duration)
        return

    # 인증 객체를 생성합니다.
    end_time = current_time + timedelta(minutes=auth_duration)  # auth_duration을 분 단위로 설정
    room = Room.objects.get(id=room_id)
    user = User.objects.get(id=user_id)
    authentication = Authentication.objects.create(
        room=room,
        user=user,
        start=current_time,
        end=end_time
    )

# 만료된 스케줄을 삭제하는 함수
@app.task
def revoke_schedules(room_id, user_id, day_of_week, auth_duration):
    # 해당 작업을 스케줄링하는 스케줄이 있는지 확인합니다.
    task_name = f'create-authentication-{room_id}-{user_id}-{day_of_week}-{auth_duration}'
    try:
        # AsyncResult를 사용하여 스케줄링된 작업을 가져옵니다.
        result = PeriodicTask.objects.get(task_name)
        # 스케줄링된 작업을 취소합니다.
        result.delete()
    except Exception as e:
        # 오류가 발생한 경우 처리합니다.
        print(f"Failed to revoke schedule {task_name}: {e}")



@transaction.atomic # db작업 동기적으로 처리
@app.task
def create_periodic_task(room_id, user_id, day_of_week, hour, minute, auth_duration):
    # 기존의 CrontabSchedule 레코드를 가져옵니다.
    crontab, _ = CrontabSchedule.objects.get_or_create(hour=hour, minute=minute, day_of_week=day_of_week)

    # 주기적 작업을 생성합니다.
    periodic_task, _ = PeriodicTask.objects.get_or_create(
        name=f'create-authentication-{room_id}-{user_id}-{day_of_week}-{auth_duration}',  # 주기적 작업 이름
        task='activities.tasks.create_authentication',  # 실행할 작업 (Celery 작업의 이름)
        crontab=crontab,  # 스케줄
        args=[room_id, user_id, day_of_week, auth_duration]  # 작업에 전달할 인수
    )

    return periodic_task
