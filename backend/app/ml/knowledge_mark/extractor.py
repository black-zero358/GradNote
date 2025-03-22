import json
import os
from typing import Dict, List, Optional
from langchain.schema import Document
from langchain_openai import ChatOpenAI
from langfuse.callback import CallbackHandler

# 从环境变量获取配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
OPENAI_LLM_MODEL = os.getenv("OPENAI_LLM_MODEL", "deepseek-r1-250120")

class KnowledgeExtractor:
    """知识点提取器，用于从题目和解题过程中提取知识点"""
    
    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None, model_name: Optional[str] = None):
        """
        初始化知识点提取器
        
        Args:
            api_key: API密钥，默认从环境变量获取
            api_base: API基础URL，默认从环境变量获取
            model_name: 模型名称，默认从环境变量获取
        """
        self.langfuse_handler = CallbackHandler()
        self.llm = ChatOpenAI(
            api_key=api_key or OPENAI_API_KEY,
            base_url=api_base or OPENAI_API_BASE,
            model_name=model_name or OPENAI_LLM_MODEL,
            callbacks=[self.langfuse_handler]
        )
    
    def extract_subject_info(self, question_text: str) -> Dict[str, str]:
        """
        提取题目所属的科目、章节、小节
        
        Args:
            question_text: 题目文本
            
        Returns:
            包含科目、章节、小节和置信度的字典
        """
        prompt = f"""分析以下题目，确定其所属的科目、章节和小节。
        题目：{question_text}
        
        请以JSON格式返回结果：
        {{
            "subject": "科目名称",
            "chapter": "章节名称",
            "section": "小节名称",
            "confidence": 分数 # 0-10的置信度
        }}
        """
        
        response = self.llm.invoke(prompt)
        
        # 解析JSON响应
        try:
            result = json.loads(response.content)
            return result
        except json.JSONDecodeError:
            # 解析失败则返回低置信度结果
            return {
                "subject": "未知",
                "chapter": "未知",
                "section": "未知",
                "confidence": 0
            }
    
    def evaluate_knowledge_points(self, knowledge_points: List[Document], question: str) -> Dict:
        """
        评估知识点是否完备
        
        Args:
            knowledge_points: 知识点列表
            question: 问题文本
            
        Returns:
            评估结果字典
        """
        if not knowledge_points:
            return {
                "is_complete": False,
                "confidence": 0,
                "missing_concepts": ["需要提取知识点"],
                "reasoning": "没有提供任何知识点"
            }
            
        knowledge_text = "\n".join([
            f"- {doc.metadata['subject']}/{doc.metadata['chapter']}/{doc.metadata['section']}: {doc.metadata['item']}"
            for doc in knowledge_points
        ])
        
        prompt = f"""判断以下知识点是否足够解答这个问题：
        
        问题：{question}
        
        知识点：
        {knowledge_text}
        
        请以JSON格式返回结果：
        {{
            "is_complete": true/false,  # 知识点是否完备
            "missing_concepts": ["概念1", "概念2"],  # 缺少的关键概念（如有）
            "confidence": 0-10,  # 置信度分数
            "reasoning": "推理过程"  # 简要说明理由
        }}
        """
        
        response = self.llm.invoke(prompt)
        
        # 解析JSON响应
        try:
            result = json.loads(response.content)
            return result
        except json.JSONDecodeError:
            # 解析失败则保守返回False
            return {
                "is_complete": False,
                "confidence": 0,
                "missing_concepts": ["解析失败"],
                "reasoning": "JSON解析错误"
            }
    
    def extract_knowledge_points(
        self, 
        question: str, 
        solution: str, 
        existing_points: Optional[List[Document]] = None
    ) -> List[Dict]:
        """
        从解题过程中提取知识点
        
        Args:
            question: 问题文本
            solution: 解题过程
            existing_points: 已有知识点列表
            
        Returns:
            新提取的知识点列表
        """
        # 根据是否有已存在的知识点，选择不同的提示模板
        if existing_points and len(existing_points) > 0:
            # 有一些知识点，但不完备，需要补充其他知识点
            # 将已有知识点加入上下文，避免提取重复知识点
            existing_points_text = "\n".join([
                f"- {point.metadata['subject']}/{point.metadata['chapter']}/{point.metadata['section']}: "
                f"{point.metadata['item']} - {point.page_content}"
                for point in existing_points
            ])
            
            prompt = f"""请从以下解题过程中提取关键知识点，注意避免与已有知识点重复：
            
            题目：{question}
            
            解题过程：
            {solution}
            
            已有知识点：
            {existing_points_text}
            
            请以JSON格式列出额外需要的知识点（避免与已有知识点重复），包括：
            - subject: 科目
            - chapter: 章节
            - section: 小节
            - item: 具体知识点名称
            - details: 知识点详细说明
            
            如果没有需要补充的知识点，请返回空数组 []
            
            例如：
            [
                {{
                    "subject": "高等数学",
                    "chapter": "一元函数微分学的应用",
                    "section": "单调性与极值的判断",
                    "item": "单调性的判别",
                    "details": "如果在区间I上，导数f'(x)>0，则f(x)在I上单调递增；如果f'(x)<0，则f(x)在I上单调递减。"
                }}
            ]
            """
        else:
            # 没有任何知识点，需要完全提取
            prompt = f"""请从以下解题过程中提取所有关键知识点：
            
            题目：{question}
            
            解题过程：
            {solution}
            
            请以JSON格式列出所有必要的知识点，包括：
            - subject: 科目
            - chapter: 章节
            - section: 小节
            - item: 具体知识点名称
            - details: 知识点详细说明
            
            例如：
            [
                {{
                    "subject": "高等数学",
                    "chapter": "一元函数微分学的应用",
                    "section": "单调性与极值的判断",
                    "item": "单调性的判别",
                    "details": "如果在区间I上，导数f'(x)>0，则f(x)在I上单调递增；如果f'(x)<0，则f(x)在I上单调递减。"
                }}
            ]
            """
        
        # 调用LLM提取知识点
        response = self.llm.invoke(prompt)
        
        # 解析JSON响应
        try:
            extracted_points = json.loads(response.content)
            return extracted_points if isinstance(extracted_points, list) else []
        except json.JSONDecodeError:
            return [] 