"""
对话接口
"""
import json
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.schemas import ChatRequest, ChatResponse
from app.api.deps import get_db, get_current_user_id, get_agent_service
from app.services.agent_service import AgentService

router = APIRouter()


def sse_format(data: str) -> str:
    """格式化SSE消息"""
    return f"data: {data}\n\n"


@router.post("", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    发送消息进行对话（非流式）
    完整流程：RAG检索 -> 组装Prompt -> 调用LLM -> 保存记录
    """
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="消息不能为空"
        )

    try:
        result = agent_service.chat(
            user_id=user_id,
            session_id=request.session_id,
            question=request.message.strip()
        )

        return ChatResponse(
            answer=result["answer"],
            data_date=result["data_date"],
            retrieved_count=result["retrieved_count"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"对话处理失败: {str(e)}"
        )


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    流式对话（SSE）
    返回 EventStream，前端通过 EventSource 接收
    """
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="消息不能为空"
        )

    async def generate() -> AsyncGenerator[str, None]:
        """生成SSE流"""
        try:
            for chunk, is_done in agent_service.chat_stream(
                user_id=user_id,
                session_id=request.session_id,
                question=request.message.strip()
            ):
                if is_done:
                    # 发送完成信号，包含元数据
                    done_data = json.dumps({
                        "type": "done",
                        "data": json.loads(chunk)
                    }, ensure_ascii=False)
                    yield sse_format(done_data)
                else:
                    # 发送内容片段
                    content_data = json.dumps({
                        "type": "content",
                        "data": chunk
                    }, ensure_ascii=False)
                    yield sse_format(content_data)

        except Exception as e:
            error_data = json.dumps({
                "type": "error",
                "data": str(e)
            }, ensure_ascii=False)
            yield sse_format(error_data)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 禁用Nginx缓冲
        }
    )
