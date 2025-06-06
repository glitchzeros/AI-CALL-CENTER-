"""
Telegram integration router
The Scribe's Telegram Gateway
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional

from database.connection import get_database
from models.user import User
from models.telegram import TelegramChat
from routers.auth import get_current_user

router = APIRouter()

class TelegramChatResponse(BaseModel):
    id: int
    chat_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    created_at: str

class TelegramLinkRequest(BaseModel):
    chat_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

@router.get("/chats", response_model=List[TelegramChatResponse])
async def get_telegram_chats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Get user's linked Telegram chats
    The Scribe's Telegram Connections
    """
    try:
        result = await db.execute(
            select(TelegramChat).where(
                TelegramChat.user_id == current_user.id,
                TelegramChat.is_active == True
            ).order_by(TelegramChat.created_at.desc())
        )
        
        chats = result.scalars().all()
        
        return [
            TelegramChatResponse(
                id=chat.id,
                chat_id=chat.chat_id,
                username=chat.username,
                first_name=chat.first_name,
                last_name=chat.last_name,
                is_active=chat.is_active,
                created_at=chat.created_at.isoformat()
            )
            for chat in chats
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get Telegram chats")

@router.post("/link-chat", response_model=TelegramChatResponse)
async def link_telegram_chat(
    chat_data: TelegramLinkRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Link a Telegram chat to user account
    The Scribe's Telegram Binding
    """
    try:
        # Check if chat is already linked
        existing_result = await db.execute(
            select(TelegramChat).where(TelegramChat.chat_id == chat_data.chat_id)
        )
        existing_chat = existing_result.scalar_one_or_none()
        
        if existing_chat:
            if existing_chat.user_id == current_user.id:
                # Already linked to this user
                return TelegramChatResponse(
                    id=existing_chat.id,
                    chat_id=existing_chat.chat_id,
                    username=existing_chat.username,
                    first_name=existing_chat.first_name,
                    last_name=existing_chat.last_name,
                    is_active=existing_chat.is_active,
                    created_at=existing_chat.created_at.isoformat()
                )
            else:
                raise HTTPException(status_code=400, detail="Chat is already linked to another user")
        
        # Create new chat link
        new_chat = TelegramChat(
            chat_id=chat_data.chat_id,
            user_id=current_user.id,
            username=chat_data.username,
            first_name=chat_data.first_name,
            last_name=chat_data.last_name,
            is_active=True
        )
        
        db.add(new_chat)
        await db.commit()
        await db.refresh(new_chat)
        
        return TelegramChatResponse(
            id=new_chat.id,
            chat_id=new_chat.chat_id,
            username=new_chat.username,
            first_name=new_chat.first_name,
            last_name=new_chat.last_name,
            is_active=new_chat.is_active,
            created_at=new_chat.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to link Telegram chat")

@router.delete("/chats/{chat_id}")
async def unlink_telegram_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Unlink a Telegram chat from user account
    The Scribe's Telegram Unbinding
    """
    try:
        result = await db.execute(
            select(TelegramChat).where(
                TelegramChat.chat_id == chat_id,
                TelegramChat.user_id == current_user.id
            )
        )
        
        chat = result.scalar_one_or_none()
        
        if not chat:
            raise HTTPException(status_code=404, detail="Telegram chat not found")
        
        # Deactivate instead of deleting to preserve history
        chat.is_active = False
        await db.commit()
        
        return {"message": "Telegram chat unlinked successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to unlink Telegram chat")

@router.get("/bot-info")
async def get_bot_info():
    """
    Get Telegram bot information for linking
    The Scribe's Telegram Identity
    """
    return {
        "bot_username": "AetheriumScribeBot",  # This would be configured
        "instructions": [
            "1. Start a chat with @AetheriumScribeBot on Telegram",
            "2. Send the command /link",
            "3. Follow the instructions to complete the linking process",
            "4. Your Telegram chat will be connected to your Aetherium account"
        ],
        "features": [
            "Send messages via Telegram",
            "Receive notifications",
            "Trigger workflows via Telegram commands",
            "Integration with voice and SMS workflows"
        ]
    }