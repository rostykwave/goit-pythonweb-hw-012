from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request, Body
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from src.schemas import UserCreate, Token, User, RequestEmail
from src.services.auth import create_access_token, Hash, get_email_from_token
from src.services.users import UserService
from src.services.email import send_email, send_password_reset_email
from src.database.db import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user account.
    
    Args:
        body (UserCreate): User registration data including username, email, password
        bt (BackgroundTasks): Background task queue for sending confirmation emails
        request (Request): HTTP request object for generating confirmation URLs
        db (AsyncSession): Database session dependency
        
    Returns:
        UserResponse: Created user information
        
    Raises:
        HTTPException: 409 if email already exists
    """
    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this username already exists",
        )
    user_data.password = Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )
    return new_user

@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """
    User authentication endpoint.
    
    Args:
        body (OAuth2PasswordRequestForm): Login credentials (username/email and password)
        db (AsyncSession): Database session dependency
        
    Returns:
        dict: Access token and token type
        
    Raises:
        HTTPException: 401 if credentials are invalid
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)
    if not user or not Hash().verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email address not confirmed",
        )
    access_token = await create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Confirm user email with verification token.
    
    Args:
        token (str): Email confirmation token
        db (AsyncSession): Database session dependency
        
    Returns:
        dict: Confirmation message
        
    Raises:
        HTTPException: 400 if token is invalid or expired
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await user_service.confirmed_email(email)
    return {"message": "Email confirmed successfully"}

@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Request new email confirmation.
    
    Args:
        body (RequestEmail): Email address for confirmation
        background_tasks (BackgroundTasks): Background task queue
        request (Request): HTTP request object
        db (AsyncSession): Database session dependency
        
    Returns:
        dict: Confirmation message
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user is None:
        return {"message": "Check your email for confirmation"}

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {"message": "Check your email for confirmation"}

@router.post("/forgot-password")
async def forgot_password(
    body: RequestEmail,
    background_tasks: BackgroundTasks,  
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Request password reset email."""
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)
    if user:
        background_tasks.add_task(
            send_password_reset_email, user.email, user.username, request.base_url
        )
    return {"message": "If email exists, password reset link has been sent"}

@router.post("/reset-password/{token}")
async def reset_password(
    token: str,
    new_password: str = Body(...),
    db: AsyncSession = Depends(get_db),
):
    """Reset password using token."""
    email = await get_email_from_token(token, "reset_password")
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid token"
        )
    
    hashed_password = Hash().get_password_hash(new_password)
    await user_service.update_user_password(email, hashed_password)
    return {"message": "Password reset successfully"}