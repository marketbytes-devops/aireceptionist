import uuid
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, TimestampMixin, GUID

if TYPE_CHECKING:
    from backend.app.models.doctor import Doctor
    from backend.app.models.appointment import Appointment
    from backend.app.models.call_log import CallLog
    from backend.app.models.user import User


class Clinic(Base, TimestampMixin):
    __tablename__ = "clinics"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Kolkata", nullable=False)
    knowledge_base: Mapped[str] = mapped_column(Text, nullable=True)

    # Relationships
    doctors: Mapped[List["Doctor"]] = relationship(
        "Doctor", back_populates="clinic", cascade="all, delete-orphan"
    )
    appointments: Mapped[List["Appointment"]] = relationship(
        "Appointment", back_populates="clinic", cascade="all, delete-orphan"
    )
    call_logs: Mapped[List["CallLog"]] = relationship(
        "CallLog", back_populates="clinic", cascade="all, delete-orphan"
    )
    users: Mapped[List["User"]] = relationship(
        "User", back_populates="clinic", cascade="all, delete-orphan"
    )

