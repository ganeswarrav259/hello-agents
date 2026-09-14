"""Hello-Agents 4.2 ReAct 离线演示（Python 3.10+，仅标准库）。
源码：ganeswarrav259/hello-agents，ReAct.py blob 04ae533df7d71f14a685eb0349e024291fda7c90。
保留教材提示词及 ReActAgent 实现；替换模型、搜索和入口，保留教材解析器的已知局限。
所有回答和搜索资料均为预设的虚构示例；不会联网或读取 API 密钥。
运行：python react42_offline_demo.py
"""
import re
from typing import Callable


class HelloAgentsLLM:
    """离线替身，不是教材的真实模型客户端。"""
    def __init__(self):
        self.calls = 0
        self.prompts: list[str] = []

    def think(self, messages: list[dict[str, str]]) -> str:
        self.calls += 1
        prompt = messages[0]["content"]
        self.prompts.append(prompt)
        print(f"\n[模拟 LLM 调用 {self.calls}：本轮完整提示词]\n{prompt}")
        if self.calls == 1:
            return "Thought: 需要查询示例资料。\nAction: Search[示例品牌最新手机]"
        if self.calls == 2:
            assert "Observation: 【离线模拟】" in prompt
            return "Thought: 示例资料已经返回。\nAction: Finish[示例品牌 A1，主要卖点是续航与影像。]"
        raise RuntimeError("演示只预设两轮响应；这不是一个真实语言模型。")


class ToolExecutor:
    """与教材相同的工具映射机制；类型标注作了整理。"""
    def __init__(self):
        self.tools = {}

    def registerTool(self, name: str, description: str, func: Callable[[str], str]):
        self.tools[name] = {"description": description, "func": func}

    def getTool(self, name: str):
        return self.tools.get(name, {}).get("func")

    def getAvailableTools(self) -> str:
        return "\n".join(
            f"- {name}: {info['description']}" for name, info in self.tools.items()
        )


SEARCH_CALLS: list[str] = []


def search(query: str) -> str:
    """搜索替身：不联网，不检索真实手机。"""
    SEARCH_CALLS.append(query)
    return "【离线模拟】示例品牌 A1，主要卖点是续航与影像。"


REACT_PROMPT_TEMPLATE = """
请注意，你是一个有能力调用外部工具的智能助手。

可用工具如下：
{tools}

请严格按照以下格式进行回应：

Thought: 你的思考过程，用于分析问题、拆解任务和规划下一步行动。
Action: 你决定采取的行动，必须是以下格式之一：
- `{{tool_name}}[{{tool_input}}]`：调用一个可用工具。
- `Finish[最终答案]`：当你认为已经获得最终答案时。
- 当你收集到足够的信息，能够回答用户的最终问题时，你必须在`Action:`字段后使用 `Finish[最终答案]` 来输出最终答案。


现在，请开始解决以下问题：
Question: {question}
History: {history}
"""

class ReActAgent:
    def __init__(self, llm_client: HelloAgentsLLM, tool_executor: ToolExecutor, max_steps: int = 5):
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history = []

    def run(self, question: str):
        self.history = []
        current_step = 0

        while current_step < self.max_steps:
            current_step += 1
            print(f"\n--- 第 {current_step} 步 ---")

            tools_desc = self.tool_executor.getAvailableTools()
            history_str = "\n".join(self.history)
            prompt = REACT_PROMPT_TEMPLATE.format(tools=tools_desc, question=question, history=history_str)

            messages = [{"role": "user", "content": prompt}]
            response_text = self.llm_client.think(messages=messages)
            if not response_text:
                print("错误：LLM未能返回有效响应。"); break

            thought, action = self._parse_output(response_text)
            if thought: print(f"🤔 思考: {thought}")
            if not action: print("警告：未能解析出有效的Action，流程终止。"); break
            
            if action.startswith("Finish"):
                # 如果是Finish指令，提取最终答案并结束
                final_answer = self._parse_action_input(action)
                print(f"🎉 最终答案: {final_answer}")
                return final_answer
            
            tool_name, tool_input = self._parse_action(action)
            if not tool_name or not tool_input:
                self.history.append("Observation: 无效的Action格式，请检查。"); continue

            print(f"🎬 行动: {tool_name}[{tool_input}]")
            tool_function = self.tool_executor.getTool(tool_name)
            observation = tool_function(tool_input) if tool_function else f"错误：未找到名为 '{tool_name}' 的工具。"
            
            print(f"👀 观察: {observation}")
            self.history.append(f"Action: {action}")
            self.history.append(f"Observation: {observation}")

        print("已达到最大步数，流程终止。")
        return None

    def _parse_output(self, text: str):
        # Thought: 匹配到 Action: 或文本末尾
        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", text, re.DOTALL)
        # Action: 匹配到文本末尾
        action_match = re.search(r"Action:\s*(.*?)$", text, re.DOTALL)
        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None
        return thought, action

    def _parse_action(self, action_text: str):
        match = re.match(r"(\w+)\[(.*)\]", action_text, re.DOTALL)
        return (match.group(1), match.group(2)) if match else (None, None)

    def _parse_action_input(self, action_text: str):
        match = re.match(r"\w+\[(.*)\]", action_text, re.DOTALL)
        return match.group(1) if match else ""

if __name__ == "__main__":
    llm = HelloAgentsLLM()
    executor = ToolExecutor()
    executor.registerTool("Search", "查询预设的虚构示例资料。", search)
    agent = ReActAgent(llm_client=llm, tool_executor=executor)
    answer = agent.run("示例品牌最新手机是什么？主要卖点是什么？")
    assert answer == "示例品牌 A1，主要卖点是续航与影像。"
    assert llm.calls == 2
    assert SEARCH_CALLS == ["示例品牌最新手机"]
    assert len(agent.history) == 2
    assert all(not item.startswith("Thought:") for item in agent.history)
    print("\n[验证通过] 模拟模型调用 2 次、搜索函数调用 1 次。")
    print("[最终 history]", agent.history)
    print("[run 的返回值]", repr(answer))
