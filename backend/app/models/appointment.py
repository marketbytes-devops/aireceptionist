import enum
import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, TimestampMixin, GUID

if TYPE_CHECKING:
    from backend.app.models.clinic import Clinic
    from backend.app.models.doctor import Doctor
    from backend.app.models.call_log import CallLog


class AppointmentStatus(str, enum.Enum):
    BOOKED = "booked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class Appointment(Base, TimestampMixin):
    __tablename__ = "appointments"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    clinic_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("clinics.id", ondelete="CASCADE"), index=True, nullable=False
    )
    doctor_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("doctors.id", ondelete="CASCADE"), index=True, nullable=False
    )
    patient_name: Mapped[str] = mapped_column(String(255), nullable=False)
    patient_phone: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    patient_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    appointment_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus, name="appointment_status_enum", values_callable=lambda obj: [e.value for e in obj]),
        default=AppointmentStatus.BOOKED,
        nullable=False
    )
    treatment_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    call_transcript: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    clinic: Mapped["Clinic"] = relationship("Clinic", back_populates="appointments")
    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="appointments")
    call_log: Mapped[Optional["CallLog"]] = relationship("CallLog", back_populates="appointment", uselist=False)

