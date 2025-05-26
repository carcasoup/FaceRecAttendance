from sqlalchemy import Column, Integer, String, Date, DateTime, func
from datetime import datetime, timezone
from server.db import Base

class AttendanceRecord(Base):
    __tablename__ = 'attendance'

    id           = Column(Integer, primary_key=True, index=True)
    student_name = Column(String(128), nullable=False, index=True)
    classroom    = Column(String(64), nullable=False, index=True)
    date         = Column(Date, default=func.current_date(), nullable=False, index=True)
    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    event        = Column(String(16), nullable=False)