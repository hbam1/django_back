from celery import Celery
from celery.schedules import crontab
from datetime import datetime, timedelta
from .models import Authentication
from rooms.models import Room
from celery.result import AsyncResult
from celery import shared_task

app = Celery()

# 인증을 생성
@shared_task
def create_authentication(room_id, user_id, day_of_week, auth_duration):
    # 현재 시간을 가져옵니다.
    current_time = datetime.now()

    # 현재 시간이 방의 수명을 넘었으면 인증 생성하지 않음
    closing_date = Room.objects.get(id=room_id).closing_date
    if current_time > closing_date:
        # 만료된 스케줄을 삭제합니다.
        revoke_schedules(room_id, user_id, day_of_week, auth_duration)
        return

    # 인증 객체를 생성합니다.
    end_time = current_time + timedelta(minutes=auth_duration)  # auth_duration을 분 단위로 설정
    authentication = Authentication.objects.create(
        room=room_id,
        user=user_id,
        start=current_time,
        end=end_time
    )

# 만료된 스케줄을 삭제하는 함수
@shared_task
def revoke_schedules(room_id, user_id, day_of_week, auth_duration):
    # 해당 작업을 스케줄링하는 스케줄이 있는지 확인합니다.
    task_name = f'create-authentication-{room_id}-{user_id}-{day_of_week}-{auth_duration}'
    try:
        # AsyncResult를 사용하여 스케줄링된 작업을 가져옵니다.
        result = AsyncResult(task_name)
        # 스케줄링된 작업을 취소합니다.
        result.revoke(terminate=True)
    except Exception as e:
        # 오류가 발생한 경우 처리합니다.
        print(f"Failed to revoke schedule {task_name}: {e}")

# 인증을 생성하는 시간을 스케줄링
def schedule_authentication(room_id, user_id, day_of_week, hour, minute, auth_duration):
    # Celery Beat 스케줄에 작업을 추가합니다.
    app.conf.beat_schedule = {
        'create-authentication': {
            'task': 'tasks.create_authentication',
            'schedule': crontab(hour=hour, minute=minute, day_of_week=day_of_week),
            'args': (room_id, user_id, day_of_week, auth_duration),
        },
    }
