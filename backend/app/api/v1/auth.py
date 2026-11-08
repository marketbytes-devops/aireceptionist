import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.core.security import verify_password, get_password_hash, create_access_token
from backend.app.models.user import User, UserRole
from backend.app.models.clinic import Clinic
from backend.app.schemas.auth import Token, LoginRequest, UserCreate, UserResponse
from backend.app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
async def login_json(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """JSON-based login endpoint for web frontend dashboard."""
    stmt = select(User).where(User.email == login_data.email)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is deactivated"
        )

    access_token = create_access_token(
        subject=user.id,
        role=user.role.value,
        clinic_id=str(user.clinic_id) if user.clinic_id else None
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        clinic_id=user.clinic_id,
        role=user.role,
        full_name=user.full_name,
        email=user.email,
    )


@router.post("/token", response_model=Token, include_in_schema=False)
async def login_oauth2_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Swagger OAuth2 password form compatibility."""
    stmt = select(User).where(User.email == form_data.username)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        subject=user.id,
        role=user.role.value,
        clinic_id=str(user.clinic_id) if user.clinic_id else None
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        clinic_id=user.clinic_id,
        role=user.role,
        full_name=user.full_name,
        email=user.email,
    )


@router.post("/register", response_model=UserResponse)
async def register_clinic_admin(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Register a new user (Super Admin or Clinic Admin)."""
    # Check if user already exists
    stmt = select(User).where(User.email == user_in.email)
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )

    # If clinic_id provided, verify clinic exists
    if user_in.clinic_id:
        clinic_stmt = select(Clinic).where(Clinic.id == user_in.clinic_id)
        c_res = await db.execute(clinic_stmt)
        if not c_res.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Clinic ID does not exist."
            )

    new_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        clinic_id=user_in.clinic_id,
        is_active=True
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get profile of current logged-in user."""
    return current_user

