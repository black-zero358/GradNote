import os
import json
from typing import Dict, List, Optional, Literal, TypedDict, Any, Tuple
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage
from langfuse.callback import CallbackHandler
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 从环境变量获取配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
OPENAI_LLM_MODEL = os.getenv("OPENAI_LLM_MODEL", "deepseek-v3-250324")

# 从环境变量获取特定任务的模型配置，如果未设置，则使用OPENAI_LLM_MODEL
LLM_SOLVING_MODEL = os.getenv("LLM_SOLVING_MODEL", OPENAI_LLM_MODEL)
LLM_REVIEW_MODEL = os.getenv("LLM_REVIEW_MODEL", OPENAI_LLM_MODEL)

# 从环境变量获取特定任务的提示词配置
LLM_SOLVING_PROMPT = os.getenv("LLM_SOLVING_PROMPT", "你是一个专业的解题助手，能够使用已知的知识点来解答学生的题目。")
LLM_REVIEW_PROMPT = os.getenv("LLM_REVIEW_PROMPT", "你是一个专业的解题审查员，需要检查解题过程是否正确，并与正确答案对比。")

class SolveState(TypedDict):
    """解题工作流状态类型"""
    question: str  # 题目内容
    knowledge_points: List[Dict[str, str]]  # 相关知识点列表
    correct_answer: Optional[str]  # 正确答案
    solution: Optional[str]  # 解题过程
    review_passed: Optional[bool]  # 审查是否通过
    review_reason: Optional[str]  # 审查意见
    attempts: int  # 尝试次数
    trace_id: Optional[str]  # Langfuse追踪ID
    error: Optional[str]  # 错误信息

class LLMSolvingWorkflow:
    """
    基于LangGraph的解题工作流

    实现完整的解题流程，包括：
    1. 使用LLM解题
    2. 审查解题过程与结果
    3. 如果审查不通过，重试解题
    """

    def __init__(self,
                 api_key: Optional[str] = None,
                 api_base: Optional[str] = None,
                 solving_model: Optional[str] = None,
                 review_model: Optional[str] = None):
        """
        初始化解题工作流

        Args:
            api_key: API密钥，默认从环境变量获取
            api_base: API基础URL，默认从环境变量获取
            solving_model: 解题模型名称，默认从环境变量获取
            review_model: 审查模型名称，默认从环境变量获取
        """
        # 初始化异步LLM客户端
        self.solving_llm = ChatOpenAI(
            api_key=api_key or OPENAI_API_KEY,
            base_url=api_base or OPENAI_API_BASE,
            model_name=solving_model or LLM_SOLVING_MODEL
        )

        self.review_llm = ChatOpenAI(
            api_key=api_key or OPENAI_API_KEY,
            base_url=api_base or OPENAI_API_BASE,
            model_name=review_model or LLM_REVIEW_MODEL
        )

        self.graph = self._build_graph()

    async def _solve_node(self, state: SolveState) -> SolveState:
        """
        解题节点，使用LLM和知识点解答题目

        Args:
            state: 当前工作流状态

        Returns:
            更新后的工作流状态
        """
        try:
            # 提取当前状态信息
            question = state["question"]
            knowledge_points = state["knowledge_points"]
            attempts = state["attempts"]



            #构建csv格式的知识点文本
            knowledge_text_csv = "科目,章节,小节,知识点,详情\n"
            for idx, kp in enumerate(knowledge_points, 1):
                knowledge_text_csv += f"{kp.get('subject', '')},{kp.get('chapter', '')},{kp.get('section', '')},{kp.get('item', '')},{kp.get('details', '')}\n"

            # 构建解题提示词
            solving_prompt = f"""请根据以下知识点解答题目。

            题目：
            {question}

            可能相关的知识点：
            {knowledge_text_csv}

            {'这是第 ' + str(attempts) + ' 次尝试解答。请特别注意审查意见并改进：' + state.get('review_reason', '') if attempts > 1 else ''}

            请提供详细的解题过程，并明确指出使用了哪些知识点。
            """

            # 创建消息
            messages = [
                SystemMessage(content=LLM_SOLVING_PROMPT),
                HumanMessage(content=solving_prompt)
            ]

            # 异步调用LLM
            response = await self.solving_llm.ainvoke(messages)

            # 更新状态
            state["solution"] = response.content
            state["attempts"] = state["attempts"] + 1

            return state
        except Exception as e:
            # 记录错误信息
            logger.error(f"解题过程出错: {str(e)}")
            state["error"] = f"解题失败: {str(e)}"
            return state

    async def _review_node(self, state: SolveState) -> SolveState:
        """
        审查节点，检查解题过程是否正确

        Args:
            state: 当前工作流状态

        Returns:
            更新后的工作流状态
        """
        try:
            # 提取当前状态信息
            question = state["question"]
            solution = state["solution"]
            correct_answer = state.get("correct_answer", "")

            # 构建审查提示词
            review_prompt = f"""请审查以下解题过程，判断是否正确。

            题目：
            {question}

            解题过程：
            {solution}

            {'正确答案：\n' + correct_answer if correct_answer else ''}

            请判断解题过程是否正确，并给出具体的审查意见。如果解题过程中有错误，请明确指出错误之处和改进建议。

            请以JSON格式输出结果：
            {{
                "passed": true/false,  // 解题过程是否正确
                "reason": "审查意见和建议"  // 详细的审查意见
            }}
            """

            # 创建消息
            messages = [
                SystemMessage(content=LLM_REVIEW_PROMPT),
                HumanMessage(content=review_prompt)
            ]

            # 异步调用LLM审查
            response = await self.review_llm.ainvoke(messages)

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

                result_text=result_text.replace("\\","\\\\")

                result = json.loads(result_text)

                # 更新状态
                state["review_passed"] = result.get("passed", False)
                state["review_reason"] = result.get("reason", "未提供审查意见")

                return state
            except json.JSONDecodeError:
                # JSON解析失败，设置为审查不通过
                state["review_passed"] = False
                state["review_reason"] = "JSON解析失败"
                return state
        except Exception as e:
            # 记录错误信息
            logger.error(f"审查过程出错: {str(e)}")
            state["error"] = f"审查失败: {str(e)}"
            state["review_passed"] = False
            state["review_reason"] = f"审查过程出错: {str(e)}"
            return state

    def _should_retry(self, state: SolveState) -> Literal["retry", "end"]:
        """
        条件路由函数，决定是重试解题还是结束工作流

        Args:
            state: 当前工作流状态

        Returns:
            下一步操作："retry" 或 "end"
        """
        # 如果出现错误，直接结束
        if state.get("error"):
            return "end"

        # 如果审查通过或已达到最大尝试次数，结束工作流
        if state.get("review_passed", False) or state.get("attempts", 0) >= 3:
            return "end"

        # 否则重试解题
        return "retry"

    def _build_graph(self) -> StateGraph:
        """
        构建工作流图

        Returns:
            StateGraph: 编译后的工作流图
        """
        # 创建工作流图
        workflow = StateGraph(SolveState)

        # 添加节点
        workflow.add_node("solve", self._solve_node)
        workflow.add_node("review", self._review_node)

        # 添加边
        workflow.add_edge("solve", "review")
        workflow.add_conditional_edges(
            "review",
            self._should_retry,
            {
                "end": END,
                "retry": "solve"
            }
        )

        # 设置入口节点
        workflow.set_entry_point("solve")

        # 编译工作流图
        return workflow.compile()

    async def invoke(self, initial_state: Dict[str, Any]) -> SolveState:
        """
        运行解题工作流

        Args:
            initial_state: 初始状态，必须包含题目内容和知识点列表

        Returns:
            SolveState: 最终工作流状态
        """
        # 检查必要的初始状态字段
        if "question" not in initial_state:
            raise ValueError("初始状态必须包含'question'字段")
        if "knowledge_points" not in initial_state:
            raise ValueError("初始状态必须包含'knowledge_points'字段")

        # 确保状态包含尝试次数字段
        if "attempts" not in initial_state:
            initial_state["attempts"] = 1

        try:
            # 创建Langfuse回调处理器
            langfuse_handler = CallbackHandler(
                session_id=str(initial_state.get("trace_id", "")),
                user_id=str(initial_state.get("user_id", "")),
                tags=["解题工作流"]
            )

            # 运行工作流，使用langfuse回调
            result = await self.graph.ainvoke(
                initial_state,
                config={"callbacks": [langfuse_handler]}
            )

            return result
        except Exception as e:
            # 记录错误信息
            logger.error(f"解题工作流执行出错: {str(e)}")
            return {
                "error": f"解题工作流执行失败: {str(e)}",
                **initial_state
            }
