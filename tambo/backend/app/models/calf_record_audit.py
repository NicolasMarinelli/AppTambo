from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CalfRecordAudit(Base):
    __tablename__ = "calf_records_audit"

    id: Mapped[int] = mapped_column(primary_key=True)
    calf_record_id: Mapped[int] = mapped_column(ForeignKey("calf_records.id"), nullable=False, index=True)
    previous_state: Mapped[dict] = mapped_column(JSON, nullable=False)
    edited_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    edited_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
