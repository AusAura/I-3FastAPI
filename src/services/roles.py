from fastapi import Request, Depends, HTTPException, status

from src.database.models import Role, User
from src.messages import FORBIDDEN
from src.services.auth import auth_service


class RoleAccess:
    def __init__(self, allowed_roles: list[Role]):
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, user: User = Depends(auth_service.get_current_user)):
        """
        Check user role. If user role not in allowed roles, raise HTTPException.
        :param request: request object: request object from FastAPI
        :param user: user object: user object from database
        :return: user object from database

        """
        print(user.role, self.allowed_roles)
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=FORBIDDEN
            )
