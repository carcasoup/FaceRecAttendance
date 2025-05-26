import os, shutil, time, cv2, numpy as np
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, date

from server.db import SessionLocal, engine, Base
from server.models import AttendanceRecord
from server.recognition import face_recognizer
from server.config import STUDENTS_DIR

# 🎯 Создаём схему (таблицу attendance) единожды при старте
Base.metadata.create_all(bind=engine)

router = APIRouter()

# Dependency для базы
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post('/collect')
async def collect_data(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    class_name: str = Form(...)
):
    """
    Сохраняем новое фото в папку class_name и дообучаем модель.
    """
    target_dir = os.path.join(STUDENTS_DIR, class_name)
    os.makedirs(target_dir, exist_ok=True)
    filename = f"{int(time.time())}.jpg"
    path = os.path.join(target_dir, filename)
    with open(path, 'wb') as buf:
        shutil.copyfileobj(file.file, buf)
    # Запускаем обновление модели (последовательное встраивание новых эмбеддингов)
    background_tasks.add_task(face_recognizer.build_embedding_db, class_name)
    return {'status': 'ok', 'path': path}

@router.post('/recognize')
async def recognize_and_mark(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    class_name: str = Form(...)
):
    """
    Распознаём лица на кадре, возвращаем результаты и фоново логируем событие 'enter'.
    """
    data = await file.read()
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(400, 'Invalid image format')

    results = face_recognizer.predict(img)
    today = date.today()

    def record_entry():
        session = SessionLocal()
        try:
            for item in results:
                name = item.get('name')
                if not name or name.lower() == 'unknown':
                    continue
                rec = AttendanceRecord(
                    student_name=name,
                    classroom=class_name,
                    date=today,
                    timestamp=datetime.utcnow(),
                    event='enter'
                )
                session.add(rec)
                session.commit()
        finally:
            session.close()

    background_tasks.add_task(record_entry)
    return {'recognized': results}

@router.post('/mark')
def mark_entry(
    student_name: str,
    classroom: str,
    db: Session = Depends(get_db)
):
    """
    Ручная отметка входа: всегда event='enter'.
    """
    now = datetime.utcnow()
    rec = AttendanceRecord(
        student_name=student_name,
        classroom=classroom,
        date=now.date(),
        timestamp=now,
        event='enter'
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return {'status': 'ok', 'student_name': student_name, 'classroom': classroom, 'event': rec.event, 'timestamp': rec.timestamp.isoformat()}