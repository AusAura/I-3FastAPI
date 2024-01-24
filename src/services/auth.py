from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt # noqa

from src.database.db import get_db
from src.repositories import users as repository_users
from src.conf.config import config
from src.messages import INVALID_SCOPES, NOT_VALID_CREDENTIALS, INVALID_TOKEN


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = config.SECRET_KEY_JWT
    ALGORITHM = config.ALGORITHM_JWT

    def verify_password(self, plain_password, hashed_password):
        """
        Verify hashed password with plain text password. Return True if password is correct else False.

        :param plain_password: plain text password from request body
        :param hashed_password: hashed password from database
        :return: True if password is correct else False

        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Hash password with bcrypt.

        :param password: plain text password from request body
        :return: hashed password

        """
        return self.pwd_context.hash(password)

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

    # define a function to generate a new access token
    async def create_access_token(
            self, data: dict, expires_delta: Optional[float] = None
    ):
        """
        Create access token for user.

        :param data: user data: email, password, etc.
        :param expires_delta: access token expiration time in seconds
        :return: encoded access token

        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=100)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"}
        )
        encoded_access_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_access_token

    # define a function to generate a new refresh token
    async def create_refresh_token(
            self, data: dict, expires_delta: Optional[float] = None
    ):
        """
        Create refresh token for user.

        :param data: user data: email, password, etc.
        :param expires_delta: refresh token expiration time in seconds
        :return: encoded refresh token

        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"}
        )
        encoded_refresh_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        Decode refresh token.

        :param refresh_token: refresh token from request body
        :return: email from refresh token

        """
        try:
            payload = jwt.decode(
                refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
            if payload["scope"] == "refresh_token":
                email = payload["sub"]
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=INVALID_SCOPES,
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=NOT_VALID_CREDENTIALS,
            )

    async def get_current_user(
            self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
    ):
        """
        Get current user.

        :param token: access token from request body: str
        :param db: database session: AsyncSession
        :return: current user: User

        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=NOT_VALID_CREDENTIALS,
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "access_token":
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = await repository_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception

        return user

    def create_email_token(self, data: dict):
        """
        Create email token.

        :param data: user data: email, password, etc.
        :return: encoded email token

        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=1)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """
        Get email from token.

        :param token: email token from request body
        :return: email from email token

        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError:

            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=INVALID_TOKEN,
            )


auth_service = Auth()
