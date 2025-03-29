import json
import os
from typing import Dict, List, Optional, Literal, TypedDict
from langgraph.graph import StateGraph, END
from langchain.schema import Document
from langchain_openai import ChatOpenAI
from langfuse.callback import CallbackHandler

# 从环境变量获取配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
OPENAI_LLM_MODEL = os.getenv("OPENAI_LLM_MODEL", "deepseek-r1-250120")

class SolveState(TypedDict):
    """解题工作流状态类型"""
    question: str
    knowledge_points: List[Document]
    is_complete: bool
    solution: Optional[str]
    review_passed: Optional[bool]
    review_reason: Optional[str]
    attempts: int
    existing_knowledge_points: Optional[List[Document]]
    new_knowledge_points: Optional[List[Dict]]
    knowledge_complete_after_extraction: Optional[bool]

class SolveWorkflow:
    """解题工作流类"""
    
    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None, model_name: Optional[str] = None):
        """
        初始化解题工作流
        
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
        self.workflow = self._build_workflow()
    
    def _solve_question(self, state: SolveState) -> SolveState:
        """解题节点"""
        question = state["question"]
        knowledge_points = state["knowledge_points"]
        is_complete = state["is_complete"]
        attempts = state["attempts"]
        
        # 根据知识点完备性选择解题策略
        if not knowledge_points:
            prompt = f"""请解答以下问题：
            
            问题：{question}
            
            注意：这个问题没有相关的知识点参考，请基于你的知识解答。
            """
        elif not is_complete:
            knowledge_text = "\n".join([
                f"- {doc.metadata['subject']}/{doc.metadata['chapter']}/{doc.metadata['section']}: {doc.metadata['item']}\n  {doc.page_content}"
                for doc in knowledge_points
            ])
            
            prompt = f"""请依据以下知识点解答问题：
            
            问题：{question}
            
            参考知识点（不完备）：
            {knowledge_text}
            
            注意：提供的知识点可能不完整，请补充必要的知识解答问题。
            """
        else:
            knowledge_text = "\n".join([
                f"- {doc.metadata['subject']}/{doc.metadata['chapter']}/{doc.metadata['section']}: {doc.metadata['item']}\n  {doc.page_content}"
                for doc in knowledge_points
            ])
            
            prompt = f"""请严格依据以下完整知识点解答问题：
            
            问题：{question}
            
            参考知识点（完备）：
            {knowledge_text}
            
            注意：请确保你的解答完全基于提供的知识点。
            """
        
        # 调用 LLM
        solution = self.llm.invoke(prompt)
        
        # 更新状态
        return {
            **state,
            "solution": solution.content,
            "attempts": attempts + 1
        }

    def _review_solution(self, state: SolveState) -> SolveState:
        """审查解题过程"""
        question = state["question"]
        solution = state["solution"]
        knowledge_points = state["knowledge_points"]
        
        knowledge_text = "\n".join([
            f"- {doc.metadata['subject']}/{doc.metadata['chapter']}/{doc.metadata['section']}: {doc.metadata['item']}"
            for doc in knowledge_points
        ])
        
        prompt = f"""请审查以下解题过程是否正确：
        
        问题：{question}
        
        相关知识点：
        {knowledge_text}
        
        解题过程：
        {solution}
        
        请评估：
        1. 解题过程是否正确
        2. 是否使用了正确的方法
        3. 是否有计算错误
        4. 是否有概念性错误
        
        回复时遵守以下格式：
        {{
            "passed": true/false,  # 是否通过审查
            "reason": "审查理由"  # 简要说明理由
        }}
        """
        
        try:
            review_response = self.llm.invoke(prompt)
            review_result = json.loads(review_response.content)
            review_passed = review_result.get("passed", False)
            review_reason = review_result.get("reason", "未提供理由")
        except (json.JSONDecodeError, KeyError) as e:
            review_passed = False
            review_reason = f"解析错误: {str(e)}"

        # 更新状态
        return {
            **state,
            "review_passed": review_passed,
            "review_reason": review_reason
        }

    def _mark_knowledge_points(self, state: SolveState) -> SolveState:
        """知识点标记节点"""
        # 只有当解题通过审查且知识点不完备时才进行知识点提取
        if state["review_passed"] and not state["is_complete"]:
            knowledge_result = self._process_knowledge_points(state)
            
            return {
                **state,
                "existing_knowledge_points": state["knowledge_points"],
                "new_knowledge_points": knowledge_result,
                "knowledge_complete_after_extraction": True if knowledge_result else state["is_complete"]
            }
        
        # 如果知识点已完备或解题未通过审查，不进行知识点提取
        return {
            **state,
            "existing_knowledge_points": state["knowledge_points"],
            "new_knowledge_points": [],
            "knowledge_complete_after_extraction": state["is_complete"]
        }
    
    def _process_knowledge_points(self, state: SolveState) -> List[Dict]:
        """
        从解题过程中提取知识点
        
        Args:
            state: 解题状态
            
        Returns:
            提取的新知识点列表
        """
        question_text = state["question"]
        solution = state["solution"]
        existing_knowledge_points = state["knowledge_points"]
        
        # 如果解题未通过审查，直接返回空列表
        if not state.get("review_passed", False):
            return []
        
        # 将已有知识点加入上下文，避免提取重复知识点
        existing_points_text = "\n".join([
            f"- {point.metadata['subject']}/{point.metadata['chapter']}/{point.metadata['section']}: "
            f"{point.metadata['item']} - {point.page_content}"
            for point in existing_knowledge_points
        ]) if existing_knowledge_points else "无已有知识点"
        
        prompt = f"""请从以下解题过程中提取关键知识点，注意避免与已有知识点重复：
        
        题目：{question_text}
        
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
        
        # 调用LLM提取知识点
        response = self.llm.invoke(prompt)
        
        # 解析JSON响应
        try:
            extracted_points = json.loads(response.content)
            return extracted_points if isinstance(extracted_points, list) else []
        except json.JSONDecodeError:
            return []

    def _should_retry(self, state: SolveState) -> Literal["end", "retry"]:
        """条件路由：决定是否重试解题"""
        if state["review_passed"] or state["attempts"] >= 3:  # 通过审查或达到最大尝试次数
            return "end"
        else:
            return "retry"

    def _build_workflow(self) -> StateGraph:
        """构建工作流图"""
        # 创建工作流图
        workflow = StateGraph(SolveState)
        
        # 添加节点
        workflow.add_node("solve", self._solve_question)
        workflow.add_node("review", self._review_solution)
        workflow.add_node("mark", self._mark_knowledge_points)
        
        # 添加边
        workflow.add_edge("solve", "review")
        workflow.add_conditional_edges("review", self._should_retry, {
            "end": "mark",  # 解题通过或达到最大尝试次数后进入标记阶段
            "retry": "solve"  # 解题未通过则重试
        })
        workflow.add_edge("mark", END)
        
        # 设置入口节点
        workflow.set_entry_point("solve")
        
        # 编译工作流
        return workflow.compile()
    
    def solve(self, question: str, knowledge_points: List[Document], is_complete: bool) -> Dict:
        """
        执行解题工作流
        
        Args:
            question: 问题文本
            knowledge_points: 相关知识点列表
            is_complete: 知识点是否完备
            
        Returns:
            解题结果
        """
        initial_state = {
            "question": question,
            "knowledge_points": knowledge_points,
            "is_complete": is_complete,
            "solution": None,
            "review_passed": None,
            "review_reason": None,
            "attempts": 0,
            "existing_knowledge_points": None,
            "new_knowledge_points": None,
            "knowledge_complete_after_extraction": None
        }
        
        result = self.workflow.invoke(initial_state)
        return result 