"""AI评审核心服务"""
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_classic.chains import LLMChain
from langchain_classic.prompts import PromptTemplate
from langchain_community.llms import Ollama
from langchain_openai import OpenAI
from src.config.settings import settings
from src.models.ai_review import AIReview, ReviewType, ReviewResult


class AIReviewService:
    """AI评审核心服务"""
    
    def __init__(self):
        # 根据配置选择AI模型
        if settings.openai.api_key and settings.openai.api_key != "your-openai-api-key":
            self.llm = OpenAI(
                api_key=settings.openai.api_key,
                model=settings.openai.model,
                temperature=settings.openai.temperature,
                max_tokens=settings.openai.max_tokens
            )
        else:
            self.llm = Ollama(
                base_url=settings.ollama.base_url,
                model=settings.ollama.model,
                temperature=settings.ollama.temperature
            )
    
    async def perform_review(self, db: AsyncSession, review_type: ReviewType, target_id: int, content: str) -> Dict[str, Any]:
        """
        执行AI评审
        
        Args:
            db: 数据库会话
            review_type: 评审类型
            target_id: 评审对象ID
            content: 评审内容
            
        Returns:
            Dict: 评审结果信息
        """
        try:
            # 获取评审专家配置
            reviewers = settings.ai_reviewers
            review_results = []
            
            # 对每个专家角色执行评审
            for reviewer in reviewers:
                review_result = await self._review_by_expert(
                    reviewer_role=reviewer["role"],
                    focus_areas=reviewer["focus_areas"],
                    review_type=review_type,
                    content=content
                )
                
                # 保存评审结果到数据库
                ai_review = AIReview(
                    review_type=review_type,
                    target_id=target_id,
                    reviewer_role=reviewer["role"],
                    reviewer_focus=reviewer["focus_areas"],
                    review_content=content,
                    review_result=ReviewResult(review_result["result"]),
                    review_comments=review_result["comments"],
                    improvement_suggestions=review_result["suggestions"]
                )
                db.add(ai_review)
                review_results.append(review_result)
            
            # 合并评审结果
            final_result = self._merge_review_results(review_results)
            
            # 提交事务
            await db.commit()
            
            return {
                "success": True,
                "message": "AI review completed successfully",
                "review_results": review_results,
                "final_result": final_result
            }
        except Exception as e:
            await db.rollback()
            return {
                "success": False,
                "message": f"AI review failed: {str(e)}"
            }
    
    async def _review_by_expert(self, reviewer_role: str, focus_areas: List[str], review_type: ReviewType, content: str) -> Dict[str, Any]:
        """
        单个专家角色执行评审
        
        Args:
            reviewer_role: 评审专家角色
            focus_areas: 关注领域
            review_type: 评审类型
            content: 评审内容
            
        Returns:
            Dict: 单个专家的评审结果
        """
        # 获取评审提示词
        prompt_template = self._get_review_prompt(reviewer_role, focus_areas, review_type)
        
        # 创建LLM Chain
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        
        # 执行评审
        result = chain.run(content=content)
        
        # 解析评审结果
        return self._parse_review_result(result)
    
    def _get_review_prompt(self, reviewer_role: str, focus_areas: List[str], review_type: ReviewType) -> PromptTemplate:
        """
        获取评审提示词
        
        Args:
            reviewer_role: 评审专家角色
            focus_areas: 关注领域
            review_type: 评审类型
            
        Returns:
            PromptTemplate: 评审提示词模板
        """
        # 构建关注领域字符串
        focus_areas_str = ", ".join(focus_areas)
        
        # 根据评审类型调整提示词
        if review_type == ReviewType.API_REVIEW:
            review_subject = "API设计和规范"
        elif review_type == ReviewType.TEST_POINT_REVIEW:
            review_subject = "测试点"
        elif review_type == ReviewType.TEST_CASE_REVIEW:
            review_subject = "测试用例"
        elif review_type == ReviewType.TEST_SCRIPT_REVIEW:
            review_subject = "测试脚本"
        else:
            review_subject = "内容"
        
        prompt_template = PromptTemplate(
            input_variables=["content"],
            template="""
            你是一位经验丰富的{reviewer_role}，专注于{focus_areas_str}等领域。
            
            请你对以下{review_subject}进行专业评审：
            
            {content}
            
            评审要求：
            1. 从{reviewer_role}的角度出发，评估{review_subject}的质量和完整性
            2. 重点关注{focus_areas_str}等方面
            3. 指出存在的问题和不足之处
            4. 提供具体的改进建议
            5. 给出明确的评审结果：通过(PASSED)、部分通过(PARTIALLY_PASSED)或不通过(FAILED)
            
            请按照以下JSON格式返回评审结果：
            {{
                "result": "PASSED|PARTIALLY_PASSED|FAILED",
                "comments": [
                    {{
                        "area": "关注领域",
                        "comment": "具体意见",
                        "severity": "高|中|低"
                    }}
                ],
                "suggestions": [
                    {{
                        "area": "改进领域",
                        "suggestion": "具体建议"
                    }}
                ]
            }}
            """
        )
        
        return prompt_template
    
    def _parse_review_result(self, result: str) -> Dict[str, Any]:
        """
        解析评审结果
        
        Args:
            result: LLM返回的评审结果
            
        Returns:
            Dict: 解析后的评审结果
        """
        import json
        
        try:
            # 提取JSON部分
            if "{" in result:
                json_start = result.index("{")
                json_end = result.rindex("}") + 1
                result_json = result[json_start:json_end]
                return json.loads(result_json)
            else:
                # 如果没有JSON格式，返回默认结果
                return {
                    "result": "PARTIALLY_PASSED",
                    "comments": [
                        {
                            "area": "格式问题",
                            "comment": "评审结果格式不符合要求",
                            "severity": "中"
                        }
                    ],
                    "suggestions": [
                        {
                            "area": "格式改进",
                            "suggestion": "请返回符合要求的JSON格式评审结果"
                        }
                    ]
                }
        except Exception as e:
            # 解析失败时返回默认结果
            return {
                "result": "PARTIALLY_PASSED",
                "comments": [
                    {
                        "area": "解析错误",
                        "comment": f"Failed to parse review result: {str(e)}",
                        "severity": "高"
                    }
                ],
                "suggestions": [
                    {
                        "area": "结果格式",
                        "suggestion": "请确保返回有效的JSON格式"
                    }
                ]
            }
    
    def _merge_review_results(self, review_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        合并多个评审结果
        
        Args:
            review_results: 多个评审结果列表
            
        Returns:
            Dict: 合并后的评审结果
        """
        # 统计各评审结果的数量
        result_counts = {
            "PASSED": 0,
            "PARTIALLY_PASSED": 0,
            "FAILED": 0
        }
        
        for result in review_results:
            result_counts[result["result"]] += 1
        
        # 确定最终结果
        if result_counts["FAILED"] > 0:
            final_result = "FAILED"
        elif result_counts["PARTIALLY_PASSED"] > 0:
            final_result = "PARTIALLY_PASSED"
        else:
            final_result = "PASSED"
        
        # 合并所有意见和建议
        all_comments = []
        all_suggestions = []
        
        for i, result in enumerate(review_results):
            reviewer_role = settings.ai_reviewers[i]["role"]
            
            for comment in result["comments"]:
                comment["reviewer_role"] = reviewer_role
                all_comments.append(comment)
            
            for suggestion in result["suggestions"]:
                suggestion["reviewer_role"] = reviewer_role
                all_suggestions.append(suggestion)
        
        return {
            "result": final_result,
            "comments": all_comments,
            "suggestions": all_suggestions,
            "detailed_results": review_results
        }
    
    async def get_review_history(self, db: AsyncSession, review_type: ReviewType, target_id: int) -> List[Dict[str, Any]]:
        """
        获取评审历史记录
        
        Args:
            db: 数据库会话
            review_type: 评审类型
            target_id: 评审对象ID
            
        Returns:
            List[Dict]: 评审历史记录列表
        """
        from sqlalchemy import select
        
        try:
            result = await db.execute(
                select(AIReview)
                .where(AIReview.review_type == review_type)
                .where(AIReview.target_id == target_id)
                .order_by(AIReview.created_at.desc())
            )
            
            reviews = result.scalars().all()
            
            return [{
                "id": review.id,
                "reviewer_role": review.reviewer_role,
                "review_type": review.review_type.value,
                "target_id": review.target_id,
                "review_result": review.review_result.value,
                "review_comments": review.review_comments,
                "improvement_suggestions": review.improvement_suggestions,
                "created_at": review.created_at
            } for review in reviews]
        except Exception as e:
            print(f"Failed to get review history: {str(e)}")
            return []
