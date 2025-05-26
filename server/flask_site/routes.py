from flask import Blueprint, render_template, abort
from datetime import datetime, timezone, timedelta
from server.db import SessionLocal
from server.models import AttendanceRecord
from server.config import STUDENTS_DIR
import os

bp = Blueprint(
    'site', __name__,
    static_folder='static',
    template_folder='templates'
)


@bp.route('/')
def index():
    session = SessionLocal()
    try:
        # Список уникальных аудиторий
        rooms = [r[0] for r in session.query(AttendanceRecord.classroom).distinct().all()]
    finally:
        session.close()
    return render_template('index.html', classrooms=rooms)


@bp.route('/attendance/<classroom>')
def attendance(classroom):

    # Часовой пояс GMT+3 и сегодняшняя дата в нём
    tz = timezone(timedelta(hours=3))
    today = datetime.now(tz).date()

    session = SessionLocal()
    try:
        # Берём единственную самую раннюю запись за сегодня
        first_entry = (
            session.query(AttendanceRecord)
                   .filter_by(classroom=classroom, date=today)
                   .order_by(AttendanceRecord.timestamp.asc())
                   .first()
        )
    finally:
        session.close()

    logs = []
    if first_entry:
        # Конвертируем время в GMT+3 и форматируем
        local_dt = first_entry.timestamp.astimezone(tz)
        first_entry.local_time = local_dt.strftime('%Y-%m-%d %H:%M:%S')
        logs = [first_entry]
    for entry in logs:
        # если timestamp naive:
        ts_utc = entry.timestamp
        if ts_utc.tzinfo is None:
            ts_utc = ts_utc.replace(tzinfo=timezone.utc)
        entry.local_time = ts_utc.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')
    return render_template(
        'attendance.html',
        classroom=classroom,
        logs=logs
    )