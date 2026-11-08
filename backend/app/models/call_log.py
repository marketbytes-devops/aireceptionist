import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, TimestampMixin, GUID

if TYPE_CHECKING:
    from backend.app.models.clinic import Clinic
    from backend.app.models.appointment import Appointment


class CallLog(Base, TimestampMixin):
    __tablename__ = "call_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    clinic_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("clinics.id", ondelete="CASCADE"), index=True, nullable=False
    )
    call_sid: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    caller_phone: Mapped[str] = mapped_column(String(50), nullable=False)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    recording_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    transcript: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sentiment: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    outcome: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    appointment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID(), ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    clinic: Mapped["Clinic"] = relationship("Clinic", back_populates="call_logs")
    appointment: Mapped[Optional["Appointment"]] = relationship("Appointment", back_populates="call_log")

