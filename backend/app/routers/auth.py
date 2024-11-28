from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from auth.auth_utils import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
import os
import logging
import traceback

router = APIRouter()
logger = logging.getLogger(__name__)

def get_user_credentials():
    username = os.getenv("AUTH_USERNAME")
    password_hash = os.getenv("AUTH_PASSWORD_HASH")
    
    if not username or not password_hash:
        logger.error("Missing authentication credentials in environment variables")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication configuration error"
        )
    
    return {
        "username": username,
        "password": password_hash
    }

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        logger.info(f"Login attempt for user: {form_data.username}")
        logger.info(f"Received password length: {len(form_data.password)}")
        
        # Get credentials from environment
        user_credentials = get_user_credentials()
        
        # Verify username
        if form_data.username != user_credentials["username"]:
            logger.error("Username mismatch")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        logger.info("Username matched, attempting password verification")
        verification_result = verify_password(form_data.password, user_credentials["password"])
        logger.info(f"Password verification result: {verification_result}")
        
        if not verification_result:
            logger.error("Password verification failed")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        logger.info("Creating access token")
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": form_data.username}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )