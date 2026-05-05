from hmac import compare_digest
from typing import Annotated

import jwt
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..config import settings
from ..core.roles import ROLE_ADMIN
from ..db import get_session
from ..models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


async def _resolve_user_from_token(token: str, db: AsyncSession) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        raw_sub = payload.get("sub")
        if not isinstance(raw_sub, str) or not raw_sub.strip():
            raise credentials_exception
        user_id = raw_sub.strip()
    except jwt.PyJWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    return await _resolve_user_from_token(token=token, db=db)


async def get_current_user_or_dify(
    token: Annotated[str | None, Depends(oauth2_scheme_optional)],
    db: Annotated[AsyncSession, Depends(get_session)],
    x_dify_api_key: Annotated[str | None, Header(alias="X-Dify-Api-Key")] = None,
) -> User | None:
    if settings.DIFY_COMPONENT_API_KEY and x_dify_api_key:
        if compare_digest(x_dify_api_key, settings.DIFY_COMPONENT_API_KEY):
            return None

    if token:
        return await _resolve_user_from_token(token=token, db=db)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def require_admin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.role != ROLE_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要知识管理员权限",
        )
    return current_user

