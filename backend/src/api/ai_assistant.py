from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from pydantic import BaseModel

from src.shared.database import get_db_session
from src.services.ai.assistant_service import AIAssistantService

router = APIRouter(prefix="/api/v1/ai/assistant", tags=["AI助手"])


# 请求模型
class ChatRequest(BaseModel):
    """AI助手聊天请求模型"""
    model: str = "qwen3:8b"  # 模型名称
    question: str = ...      # 用户问题


# 响应模型
class ChatResponse(BaseModel):
    """AI助手聊天响应模型"""
    answer: str              # AI回答
    model: str               # 使用的模型
    tokens_used: Optional[int] = None  # 使用的token数量
    execution_time: Optional[float] = None  # 执行时间（秒）


@router.post("/chat", response_model=ChatResponse, summary="AI助手聊天")
async def ai_assistant_chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    AI助手聊天接口
    
    - **model**: 模型名称，默认使用qwen3:8b
    - **question**: 用户输入的问题
    
    返回AI助手生成的回答
    """
    try:
        # 调用AI助手服务
        result = await AIAssistantService.chat(
            question=request.question,
            model=request.model
        )
        
        return ChatResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI助手服务错误: {str(e)}")
