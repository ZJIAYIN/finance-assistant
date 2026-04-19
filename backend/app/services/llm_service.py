"""
大模型服务
调用通义千问API
"""
import os
from typing import List, Dict, Any, Optional, Generator
import dashscope
from dashscope import Generation, TextEmbedding

from app.core.config import settings


class LLMService:
    def __init__(self):
        # 设置API Key
        api_key = settings.DASHSCOPE_API_KEY or os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            raise ValueError("DASHSCOPE_API_KEY not set")
        dashscope.api_key = api_key

    def get_embedding(self, text: str) -> Optional[List[float]]:
        """获取文本embedding"""
        try:
            resp = TextEmbedding.call(
                model=settings.EMBEDDING_MODEL,
                input=text
            )
            if resp.status_code == 200:
                return resp.output["embeddings"][0]["embedding"]
            else:
                print(f"Embedding error: {resp.message}")
                return None
        except Exception as e:
            print(f"Embedding exception: {e}")
            return None

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """对话生成"""
        try:
            response = Generation.call(
                model=settings.LLM_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                result_format="message"
            )

            if response.status_code == 200:
                return response.output.choices[0].message.content
            else:
                error_msg = f"LLM调用失败: {response.message}"
                print(error_msg)
                return f"抱歉，我暂时无法回答这个问题。{error_msg}"
        except Exception as e:
            error_msg = f"LLM调用异常: {str(e)}"
            print(error_msg)
            return f"抱歉，系统暂时不可用。{error_msg}"

    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Generator[str, None, None]:
        """
        流式对话生成
        返回生成器，每次yield一个token
        """
        try:
            responses = Generation.call(
                model=settings.LLM_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                result_format="message",
                stream=True
            )

            for response in responses:
                if response.status_code == 200:
                    chunk = response.output.choices[0].message.content
                    yield chunk
                else:
                    yield f"[错误: {response.message}]"
                    break

        except Exception as e:
            yield f"[异常: {str(e)}]"

    @staticmethod
    def format_history_to_messages(
        system_prompt: str,
        history: List[Dict[str, str]],
        current_question: str
    ) -> List[Dict[str, str]]:
        """将历史记录格式化为messages数组"""
        messages = [{"role": "system", "content": system_prompt}]

        # 添加历史对话
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})

        # 添加当前问题
        messages.append({"role": "user", "content": current_question})

        return messages
