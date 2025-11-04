"""
User routes module
"""
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from fastapi.responses import StreamingResponse
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import uuid
import base64
import os
import io

from PIL import Image, ImageOps, ImageDraw

from auth_service import AuthService
from database import UserInDB
from models import UserProfileResponse, UserProfileUpdate

logger = logging.getLogger(__name__)
router = APIRouter()
auth_service = AuthService()

# Placeholder for database dependency - this would be injected in a real implementation
db = None

async def get_current_user():
    """Get current user - placeholder implementation"""
    user = UserInDB(
        id=uuid.uuid4(),
        email="user@example.com",
        name="Test User",
        role="user",
        password_hash="",
        created_at=datetime.utcnow(),
        is_active=True
    )
    return user

@router.get("/api/user/profile", response_model=UserProfileResponse)
async def get_user_profile(current_user: UserInDB = Depends(get_current_user)):
    """Get current user's profile"""
    try:
        user_response = UserProfileResponse(
            id=current_user.id,
            email=current_user.email,
            name=current_user.name,
            role=current_user.role,
            created_at=current_user.created_at,
            is_active=current_user.is_active
        )
        return user_response
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile"
        )

@router.post("/api/user/profile")
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    """Update current user's profile"""
    try:
        # In a real implementation, you would update the user profile in the database
        return {"success": True, "message": "Profile updated successfully"}
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )

@router.post("/api/user/profile/picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_user)
):
    """Upload current user's profile picture"""
    try:
        allowed_types = {"image/jpeg", "image/png", "image/webp"}
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Ungültiges Format. Nur JPEG, PNG, WebP erlaubt."
            )

        contents = await file.read()

        # Validate file size (2MB max)
        if len(contents) > 2 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="Datei zu groß. Maximum 2MB."
            )

        try:
            image = Image.open(io.BytesIO(contents))
            image.verify()

            image = Image.open(io.BytesIO(contents))
            image = ImageOps.exif_transpose(image)
            if image.mode != 'RGBA':
                image = image.convert('RGBA')

            width, height = image.size
            min_edge = min(width, height)
            left = (width - min_edge) // 2
            top = (height - min_edge) // 2
            right = left + min_edge
            bottom = top + min_edge
            image = image.crop((left, top, right, bottom))
            image = image.resize((400, 400), Image.Resampling.LANCZOS)

            mask = Image.new('L', (400, 400), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, 400, 400), fill=255)
            output_image = Image.new('RGBA', (400, 400))
            output_image.paste(image, (0, 0), mask)

            output = io.BytesIO()
            output_image.save(output, format='PNG', optimize=True)
            output.seek(0)
            picture_data = base64.b64encode(output.read()).decode('utf-8')

        except Exception as e:  # pillow exceptions collapse here
            logger.error(f"Error processing profile picture: {e}")
            raise HTTPException(
                status_code=400,
                detail="Ungültige Bilddatei. Bitte eine gültige Bilddatei hochladen."
            )

        # In a real implementation, you would save this to the database
        # await db.set_profile_picture(current_user.id, picture_data)

        return {
            "success": True,
            "profile_picture": f"data:image/png;base64,{picture_data}"
        }
    except Exception as e:
        logger.error(f"Error uploading profile picture: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload profile picture"
        )

@router.get("/api/user/profile/picture")
async def get_profile_picture(current_user: UserInDB = Depends(get_current_user)):
    """Get current user's profile picture"""
    try:
        # In a real implementation, you would get this from the database
        # picture_data = await db.get_profile_picture(current_user.id)
        picture_data = None
        
        if not picture_data:
            # Return default avatar
            default_avatar_path = "/root/static/default-avatar.svg"
            if os.path.exists(default_avatar_path):
                with open(default_avatar_path, "rb") as f:
                    default_avatar_data = base64.b64encode(f.read()).decode('utf-8')
                return {
                    "success": True,
                    "profile_picture": f"data:image/svg+xml;base64,{default_avatar_data}"
                }
            else:
                # Fallback to simple default avatar data
                return {
                    "success": True,
                    "profile_picture": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj48Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSI1MCIgZmlsbD0iI2NjY2NjYyIvPjxjaXJjbGUgY3g9IjUwIiBjeT0iNDAiIHI9IjE1IiBmaWxsPSIjZmZmZmZmIi8+PHBhdGggZD0iTTUwIDYwIFE1MCA4MCAzMCA4NSBRNzAgODUgNTAgNjAiIGZpbGw9IiNmZmZmZmYiLz48L3N2Zz4="
                }
        
        return {
            "success": True,
            "profile_picture": picture_data
        }
    except Exception as e:
        logger.error(f"Error getting profile picture: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve profile picture"
        )

@router.delete("/api/user/profile/picture")
async def delete_profile_picture(current_user: UserInDB = Depends(get_current_user)):
    """Delete current user's profile picture"""
    try:
        # In a real implementation, you would delete this from the database
        # await db.delete_profile_picture(current_user.id)
        return {"success": True, "message": "Profile picture deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting profile picture: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete profile picture"
        )
