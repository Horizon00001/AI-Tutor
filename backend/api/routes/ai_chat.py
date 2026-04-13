from fastapi import APIRouter, HTTPException

from api.models.schemas import AIChatRequest, AIChatResponse
from services.ai_chat_service import ai_chat_service

router = APIRouter(prefix="/ai-chat", tags=["AI助手"])


@router.post("/multi-turn", response_model=AIChatResponse)
async def multi_turn_chat(request: AIChatRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="消息列表不能为空")

    if not request.messages[-1].role == "user":
        raise HTTPException(status_code=400, detail="最后一条消息必须是用户消息")

    try:
        messages = [msg.model_dump() for msg in request.messages]
        result = ai_chat_service.chat(messages, request.model)

        return AIChatResponse(
            answer=result["answer"],
            usage=result.get("usage")
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI服务调用失败: {str(e)}")
