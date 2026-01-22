from typing import Dict, Any, Optional
import time
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from src.config.settings import settings


class AIAssistantService:
    """AI助手服务类"""
    
    @staticmethod
    async def chat(question: str, model: str = "qwen3:8b") -> Dict[str, Any]:
        """
        AI助手聊天功能
        
        Args:
            question: 用户问题
            model: AI模型名称
            
        Returns:
            Dict[str, Any]: 包含回答、模型信息等的响应
        """
        start_time = time.time()
        
        try:
            # 创建Ollama LLM实例
            llm = OllamaLLM(
                model=model,
                temperature=0.7,
                base_url=settings.ai.ollama_base_url
            )
            
            # 定义系统提示词
            system_prompt = """
            你是一个专业的API接口测试智能助手，负责回答用户关于API接口测试的问题。
            请根据用户的问题，提供准确、详细的回答，包括但不限于：
            - API接口测试的相关问题
            - 测试步骤
            - 常见问题
            - 测试规范
            - 缺陷管理规范
            - 系统操作帮助
            
            回答要简洁明了，重点突出，适合技术人员阅读。
            如果用户的问题超出了API接口测试的范围，请礼貌地说明你无法回答。
            """
            
            # 创建提示模板
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{question}")
            ])
            
            # 构建链式调用
            chain = prompt | llm
            
            # 执行生成
            response = chain.invoke({"question": question})
            
            end_time = time.time()
            
            # 返回结果
            return {
                "answer": response,
                "model": model,
                "tokens_used": None,  # Ollama目前不直接返回token数量
                "execution_time": round(end_time - start_time, 2)
            }
            
        except Exception as e:
            end_time = time.time()
            print(f"AI助手调用失败: {str(e)}")
            # 出现错误时返回友好提示
            return {
                "answer": "抱歉，AI助手暂时无法响应您的请求。请检查模型服务是否正常运行，或稍后再试。",
                "model": model,
                "tokens_used": None,
                "execution_time": round(end_time - start_time, 2)
            }
