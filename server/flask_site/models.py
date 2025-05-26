from sqlalchemy import Column, Integer, String, Date, DateTime, UniqueConstraint, func
from flask_site.extensions import db

class AttendanceRecord(db.Model):
    __tablename__ = 'attendance'

    id           = Column(Integer, primary_key=True, index=True)
    student_name = Column(String(128), nullable=False, index=True)
    classroom    = Column(String(64),  nullable=False, index=True)
    date         = Column(Date, default=func.current_date(), nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint('student_name', 'classroom', 'date', name='uix_student_classroom_date'),
    )
