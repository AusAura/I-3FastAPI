import logging
from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.messages import ACCOUNT_ALREADY_EXISTS, INVALID_EMAIL, EMAIL_NOT_CONFIRMED, INVALID_PASSWORD, \
    VERIFICATION_ERROR, EMAIL_ALREADY_CONFIRMED, EMAIL_CONFIRMED, CHECK_EMAIL, INVALID_REFRESH_TOKEN, USER_IS_BLOCK
from src.repositories import users as repositories_users
from src.schemas.user import UserSchema, TokenSchema, UserResponse, RequestEmail
from src.services.email import send_email
from src.services.auth import auth_service

router = APIRouter(prefix='/auth', tags=['auth'])
get_refresh_token = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema, bt: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)):
    exist_user = await repositories_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=ACCOUNT_ALREADY_EXISTS)
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repositories_users.create_user(body, db)
    bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user


@router.post("/login", response_model=TokenSchema)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await repositories_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_EMAIL)
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=EMAIL_NOT_CONFIRMED)
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=USER_IS_BLOCK)
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_PASSWORD)

    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email, "test": "test"})
    refresh_token2 = await auth_service.create_refresh_token(data={"sub": user.email})
    await repositories_users.update_token(user, refresh_token2, db)
    return {"access_token": access_token, "refresh_token": refresh_token2, "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(credentials: HTTPAuthorizationCredentials = Depends(get_refresh_token),
                 db: AsyncSession = Depends(get_db)):
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repositories_users.get_user_by_email(email, db)

    if user and user.refresh_token == token:
        user.is_active = False
        await repositories_users.update_token(user, None, db)
        user.is_revoked = True
        await db.commit()

        return {"message": "Logged out successfully"}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_REFRESH_TOKEN)


@router.get('/refresh_token', response_model=TokenSchema)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(get_refresh_token),
                        db: AsyncSession = Depends(get_db)):
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user.refresh_token != token or user.is_revoked:
        await repositories_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_REFRESH_TOKEN)

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token2 = await auth_service.create_refresh_token(data={"sub": email})
    await repositories_users.update_token(user, refresh_token2, db)
    return {"access_token": access_token, "refresh_token": refresh_token2, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    email = await auth_service.get_email_from_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=VERIFICATION_ERROR)
    if user.confirmed:
        return {"message": EMAIL_ALREADY_CONFIRMED}
    await repositories_users.confirmed_email(email, db)
    return {"message": EMAIL_CONFIRMED}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: AsyncSession = Depends(get_db)):
    user = await repositories_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": EMAIL_ALREADY_CONFIRMED}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {"message": CHECK_EMAIL}


@router.post("/block_user/{user_id}")
async def block_user(
    user_id: int,
    is_active: bool,
    current_user: UserResponse = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db)
):

    if current_user.role.name != 'admin':
        logger = logging.getLogger(f"User Role: {current_user.role.name}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Permission denied. Admin role required. {logger}")

    user = await repositories_users.get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_active = is_active
    await db.commit()

    return {"message": "User status updated successfully"}

