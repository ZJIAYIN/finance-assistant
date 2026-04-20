"""
Agent服务
处理对话流程：检索 -> 组装Prompt -> 调用LLM
"""
import json
from typing import List, Dict, Any, Generator, Tuple
from sqlalchemy.orm import Session

from app.repositories import ConversationRepository
from app.services.rag_service import RAGService
from app.services.llm_service import LLMService
from app.models import Conversation


class AgentService:
    """对话Agent服务"""

    def __init__(self, db: Session, conversation_repo: ConversationRepository):
        self.db = db
        self.conversation_repo = conversation_repo
        self.rag_service = RAGService()
        self.llm_service = LLMService()

    def get_session_history(self, session_id: int, user_id: int) -> List[Dict[str, str]]:
        """获取会话历史记录"""
        conversations = self.conversation_repo.get_by_session(session_id, user_id)

        history = []
        for conv in conversations:
            history.extend(conv.to_message_format())

        return history

    def build_system_prompt(self, retrieved_docs: List[str], data_date: str, has_relevant_data: bool) -> str:
        """构建系统Prompt"""
        # 如果没有相关数据，给出严格提示
        if not has_relevant_data:
            return """你是一位专业的金融投资助手。

【重要提示】
当前向量数据库中没有检索到与用户问题相关的金融数据。

你的回答必须遵循以下规则：
1. 直接回复："根据现有数据，我无法回答这个问题。我的知识仅限于数据库中的金融行情数据。"
2. 不要基于你的预训练知识回答
3. 不要编造任何数据
4. 可以建议用户尝试询问其他金融相关问题"""

        # 有数据时的正常prompt
        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            context_parts.append(f"【信息{i}】{doc}")

        retrieved_context = "\n\n".join(context_parts)

        system_prompt = f"""你是一位专业的金融投资助手。请严格基于以下检索到的数据回答用户问题：

【检索数据】日期：{data_date}
{retrieved_context}

【严格规则】
1. 只能使用【检索数据】中的信息回答，禁止编造任何数据
2. 如果检索数据无法回答问题，直接说明"根据当前数据无法回答"
3. 结合对话历史理解用户意图（如"那...呢"指代前文主题）
4. 投资有风险，建议仅供参考，不构成投资建议
5. 保持专业、客观、简洁的语气

【禁止事项】
- 禁止使用你自己的预训练知识回答金融数据相关问题
- 禁止提供检索数据中没有的具体数字、涨跌幅、价格等信息"""

        return system_prompt

    def prepare_chat(
        self,
        user_id: int,
        session_id: int,
        question: str
    ) -> Tuple[List[Dict[str, str]], str, int, bool]:
        """
        准备对话所需的参数
        返回：(messages, data_date, retrieved_count, has_relevant_data)
        """
        # Step 1: RAG检索（t-1天数据）
        retrieved_docs, data_date = self.rag_service.search(question)

        # 判断是否有相关数据
        has_relevant_data = len(retrieved_docs) > 0 and data_date != ""

        # Step 2: 获取历史对话
        history = self.get_session_history(session_id, user_id)

        # Step 3: 构建System Prompt
        system_prompt = self.build_system_prompt(retrieved_docs, data_date, has_relevant_data)

        # Step 4: 组装messages
        messages = self.llm_service.format_history_to_messages(
            system_prompt=system_prompt,
            history=history,
            current_question=question
        )

        # 打印最终Prompt到控制台（调试用）
        print("\n" + "="*60)
        print("【SYSTEM PROMPT】")
        print("="*60)
        print(system_prompt)
        print("\n" + "="*60)
        print("【MESSAGES 完整结构】")
        print("="*60)
        for msg in messages:
            print(f"[{msg['role'].upper()}]: {msg['content'][:200]}...")
        print("="*60 + "\n")

        return messages, data_date, len(retrieved_docs), has_relevant_data

    def chat(
        self,
        user_id: int,
        session_id: int,
        question: str
    ) -> Dict[str, Any]:
        """
        处理用户提问（非流式）
        完整流程：检索 -> 组装Prompt -> 调用LLM -> 保存记录
        """
        messages, data_date, retrieved_count, has_relevant_data = self.prepare_chat(
            user_id, session_id, question
        )

        # Step 5: 调用LLM
        answer = self.llm_service.chat(messages)

        # Step 6: 保存对话记录
        conversation = Conversation(
            user_id=user_id,
            session_id=session_id,
            user_msg=question,
            assistant_msg=answer,
            data_date=data_date
        )
        self.db.add(conversation)
        self.db.commit()

        return {
            "answer": answer,
            "data_date": data_date,
            "retrieved_count": retrieved_count
        }

    def chat_stream(
        self,
        user_id: int,
        session_id: int,
        question: str
    ) -> Generator[Tuple[str, bool], None, None]:
        """
        流式处理用户提问
        每次yield: (content_chunk, is_done)
        is_done=True时表示生成完成，content_chunk是完整回答
        """
        messages, data_date, retrieved_count, has_relevant_data = self.prepare_chat(
            user_id, session_id, question
        )

        full_answer = ""

        # Step 5: 流式调用LLM
        for chunk in self.llm_service.chat_stream(messages):
            full_answer += chunk
            yield chunk, False  # 返回片段，未结束

        # Step 6: 保存对话记录
        conversation = Conversation(
            user_id=user_id,
            session_id=session_id,
            user_msg=question,
            assistant_msg=full_answer,
            data_date=data_date
        )
        self.db.add(conversation)
        self.db.commit()

        # 发送完成信号，附带完整信息
        done_data = json.dumps({
            "data_date": data_date,
            "retrieved_count": retrieved_count,
            "done": True
        }, ensure_ascii=False)
        yield done_data, True
