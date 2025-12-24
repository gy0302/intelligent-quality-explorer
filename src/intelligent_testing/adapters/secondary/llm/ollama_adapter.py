import httpx
from typing import List, Dict, Any
from application.ports.llm_gateway import LLMGateway, GenerationRequest, GenerationResponse
from  ..configs.settings import get_settings
from ...shared.utils.logging_setup import get_logger

logger = get_logger(__name__)


class OllamaAdapter(LLMGateway):
    """Ollama LLM 适配器实现"""

    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.ollama_base_url
        self.default_model = self.settings.ollama_model
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=60.0)
        logger.info(f"Ollama适配器初始化，目标: {self.base_url}, 默认模型: {self.default_model}")

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        """调用Ollama生成接口"""
        endpoint = "/api/generate"
        payload = {
            "model": request.model or self.default_model,
            "prompt": request.prompt,
            "stream": False,
            "options": {
                "temperature": request.temperature,
                "num_predict": request.max_tokens
            }
        }

        try:
            logger.debug(f"调用Ollama生成，模型: {payload['model']}, 提示词长度: {len(request.prompt)}")
            response = await self.client.post(endpoint, json=payload)
            response.raise_for_status()
            result = response.json()

            return GenerationResponse(
                content=result.get("response", ""),
                model_used=result.get("model"),
                tokens_used=result.get("eval_count", 0),
                finish_reason="stop"
            )
        except httpx.RequestError as e:
            logger.error(f"Ollama请求失败: {e}")
            raise ConnectionError(f"无法连接到Ollama服务: {e}")
        finally:
            await self.client.aclose()