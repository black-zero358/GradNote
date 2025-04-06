import os
import json
from typing import List, Dict, Optional, Any
from langchain_openai import ChatOpenAI
from langfuse.callback import CallbackHandler

# 从环境变量获取配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
OPENAI_LLM_MODEL = os.getenv("OPENAI_LLM_MODEL", "deepseek-r1-250120")

# 从环境变量获取特定任务的模型配置
LLM_RETRIEVER_MODEL = os.getenv("LLM_Retriever", OPENAI_LLM_MODEL)

# 从环境变量获取特定任务的提示词配置
LLM_RETRIEVER_SYSTEM_PROMPT = os.getenv("LLM_Retriever_SYSTEM_PROMPT", "")
LLM_RETRIEVER_PROMPT = os.getenv("LLM_Retriever_PROMPT", "")

class LLMKnowledgeRetriever:
    """
    基于LLM的知识点检索器
    使用大型语言模型分析题目中可能涉及到的知识点类别
    """
    
    def __init__(self, 
                 api_key: Optional[str] = None, 
                 api_base: Optional[str] = None, 
                 model_name: Optional[str] = None):
        """
        初始化知识点检索器
        
        Args:
            api_key: API密钥，默认从环境变量获取
            api_base: API基础URL，默认从环境变量获取
            model_name: LLM模型名称，默认从环境变量获取
        """
        # 设置Langfuse回调
        callbacks = []
        self.langfuse_handler = CallbackHandler()
        callbacks.append(self.langfuse_handler)
        
        
        # 初始化LLM
        self.llm = ChatOpenAI(
            api_key=api_key or OPENAI_API_KEY,
            base_url=api_base or OPENAI_API_BASE,
            model_name=model_name or LLM_RETRIEVER_MODEL,
            callbacks=callbacks
        )

    
    def _get_task_prompt(self, content: str) -> List:
        """
        根据任务生成带有系统提示词和用户提示词的消息列表
        
        Args:
            content: 用户消息内容
            
        Returns:
            List: 包含系统提示和用户提示的消息列表
        """
        from langchain_core.messages import SystemMessage, HumanMessage
        
        messages = []
        
        # 如果有系统提示词，则添加
        if LLM_RETRIEVER_SYSTEM_PROMPT:
            messages.append(SystemMessage(content=LLM_RETRIEVER_SYSTEM_PROMPT))
        
        # 如果有提示词模板，则使用模板格式化用户消息，否则直接使用内容
        user_content = LLM_RETRIEVER_PROMPT.format(content=content) if LLM_RETRIEVER_PROMPT else content
        messages.append(HumanMessage(content=user_content))
        
        return messages
    
    
    
    def analyze_knowledge_category(self, question_text: str, categories_csv: str) -> List[Dict[str, str]]:
        """
        分析题目所属的知识点类别
        
        Args:
            question_text: 题目文本
            categories_csv: CSV格式的知识点类别数据，包含科目、章节、小节
            
        Returns:
            List[Dict[str, str]]: 可能相关的知识点类别列表
        """
        # 构建提示词内容
        prompt_content = f"""分析以下题目，确定其所属的科目、章节和小节。
        
        题目：{question_text}
        
        参考以下知识点类别 (CSV格式):
        {categories_csv}
        
        请以JSON格式返回可能相关的知识点类别列表：
        [
            {{"subject": "科目名称", "chapter": "章节名称", "section": "小节名称"}}
        ]
        
        确保返回的JSON格式正确，只输出JSON数据，不要有其他内容。
        """
        
        # 获取任务特定提示词
        messages = self._get_task_prompt(prompt_content)
        
        # 调用LLM分析题目
        response = self.llm.invoke(messages)
        
        
        # 解析JSON响应
        try:
            result_text = response.content
            # 清理可能的非JSON内容
            result_text = result_text.strip()
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            result = json.loads(result_text)
            return result if isinstance(result, list) else []
        except json.JSONDecodeError:
            return [] 