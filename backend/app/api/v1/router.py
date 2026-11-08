from fastapi import APIRouter
from backend.app.api.v1 import (
    auth,
    clinics,
    doctors,
    appointments,
    tools,
    telephony,
    webhooks,
    analytics,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(clinics.router)
api_router.include_router(doctors.router)
api_router.include_router(appointments.router)
api_router.include_router(tools.router)
api_router.include_router(telephony.router)
api_router.include_router(webhooks.router)
api_router.include_router(analytics.router)

