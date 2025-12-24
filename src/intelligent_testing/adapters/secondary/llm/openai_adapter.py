"""
OpenAI适配器
实现LLM网关接口，连接到OpenAI API
"""

import openai
from typing import Dict, Any, List
from openai import AsyncOpenAI

from application.ports.llm_gateway import LLMGateway, LLMRequest, LLMResponse
from config.settings import settings


class OpenAIAdapter(LLMGateway):
    """OpenAI适配器实现"""

    def __init__(self):
        api_key = settings.OPENAI_API_KEY
        base_url = settings.OPENAI_BASE_URL

        if not api_key:
            raise ValueError("OpenAI API key is not configured")

        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url if base_url else "https://api.openai.com/v1"
        )
        self.default_model = settings.OPENAI_MODEL

    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """使用OpenAI生成文本"""
        try:
            model = request.model or self.default_model

            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": request.system_prompt or "You are a helpful assistant."},
                    {"role": "user", "content": request.prompt}
                ],
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )

            return LLMResponse(
                content=response.choices[0].message.content,
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "provider": "openai"
                }
            )

        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    async def generate_with_chat(self, messages: List[Dict[str, str]],
                                 temperature: float = 0.1) -> str:
        """使用聊天模式生成"""
        try:
            response = await self.client.chat.completions.create(
                model=self.default_model,
                messages=messages,
                temperature=temperature
            )
            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"OpenAI chat error: {str(e)}")

    def supports_model(self, model_name: str) -> bool:
        """检查是否支持特定模型"""
        # OpenA支持的模型通常以gpt-开头
        return model_name.startswith(("gpt-", "text-"))

    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return [
            "gpt-4-turbo-preview",
            "gpt-4",
            "gpt-3.5-turbo",
            "text-davinci-003"
        ]