from typing import List, Dict, Any, Optional
from openai import OpenAI
from pathlib import Path
from utils.config import API_KEY, API_URL, AI_CHAT_PROMPT_PATH


class AIChatService:
    def __init__(self):
        self.client = OpenAI(api_key=API_KEY, base_url=API_URL)
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        try:
            if AI_CHAT_PROMPT_PATH.exists():
                with open(AI_CHAT_PROMPT_PATH, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception:
            pass
        return "你是一位专业、友好的AI教学助手。"

    def chat(self, messages: List[Dict[str, str]], model: str = "deepseek-chat") -> Dict[str, Any]:
        if not API_KEY:
            raise ValueError("API_KEY未配置，请在.env文件中设置")

        formatted_messages = [{"role": "system", "content": self.system_prompt}]
        formatted_messages.extend(messages)

        response = self.client.chat.completions.create(
            model=model,
            messages=formatted_messages,
            stream=False
        )

        usage = None
        if response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }

        return {
            "answer": response.choices[0].message.content,
            "usage": usage
        }


ai_chat_service = AIChatService()
