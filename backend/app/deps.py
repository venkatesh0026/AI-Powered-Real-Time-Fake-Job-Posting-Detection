"""
FastAPI Dependencies

This module provides dependency injection for:
- Authentication/Authorization
- Token validation
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

# Security scheme for Swagger UI
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """
    Validate Bearer token from Authorization header.
    
    For now, just checks if token is present.
    TODO: Implement actual Supabase JWT validation.
    
    Args:
        credentials: Bearer token from request header
        
    Returns:
        Token string if valid
        
    Raises:
        HTTPException: If token is missing
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is missing!",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # TODO: Validate token with Supabase
    # try:
    #     payload = jwt.decode(token, settings.SUPABASE_KEY, algorithms=["HS256"])
    #     return payload
    # except jwt.JWTError:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Token is invalid!",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )
    
    return token


async def optional_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """
    Optional authentication - doesn't fail if no token provided.
    Useful for endpoints that work with or without auth.
    """
    if credentials is None:
        return None
    return credentials.credentials
