# 第 4 章知识笔记

[本章入口](README.md) · [问题记录](questions.md)

记录类型：前期学习讨论摘要。归档日期：2026-09-11。
来源：用户此前提供的 HelloAgentsLLM 代码及“记录笔记，教学我”的要求；已在当前 fork 基线 `4f7682ceafe573d07cd8a7d0b89908500e83227d` 中核对到 4.1.3。
原文：[第四章 智能体经典范式构建](../../docs/chapter4/第四章%20智能体经典范式构建.md)。

这不是整章总结，也不是本轮重新运行客户端的报告。旧 Python 学习仓库保持原样，此处只整理相关知识与待办，不迁移私人记录或测试日志。

## 4.1.3 · 先理解程序整体

根据用户提供的代码，其流程为：

```text
读取配置 → HelloAgentsLLM() 初始化对象
        → 组织消息列表 → think(messages)
        → 发送请求 → 循环接收文本片段
        → 边打印边保存 → join 拼接 → return 返回
```

这段代码调用模型，不训练模型，也不会自动执行模型输出的快速排序程序。`think` 是作者自己起的方法名，不是 Python 关键字，也不表示读取模型内部思考。

## 核心 1：类、对象与 self

`class HelloAgentsLLM` 定义类；`llmClient = HelloAgentsLLM()` 创建并引用一个实例。
`__init__` 用来初始化实例；`self` 表示当前实例。
在 `self.model = model` 中，右边是参数，左边是保存到对象上的属性，后续方法可以读取它。
`self.client = OpenAI(...)` 是持有另一个客户端对象，不是继承。

参考：[Python 类](https://docs.python.org/zh-cn/3/tutorial/classes.html)。

## 核心 2：列表里装字典

```python
messages = [
    {"role": "system", "content": "你是一位 Python 老师。"},
    {"role": "user", "content": "解释变量。"},
]
```

`messages[1]` 取第二项；`messages[1]["content"]` 取该字典中的文本。
`List[Dict[str, str]]` 是类型提示，不自动验证字段是否齐全，也不会自动转换传入的数据。
这些访问方式是对上面这份简化数据的解释，不声称覆盖全部聊天消息形式。

参考：[Python 数据结构](https://docs.python.org/zh-cn/3/tutorial/datastructures.html)、[typing](https://docs.python.org/zh-cn/3/library/typing.html)。

## 核心 3：显示、收集与返回不同

原代码中的 `print(content, end="", flush=True)` 显示片段；`append(content)` 保存片段；`"".join(collected_content)` 拼接字符串；`return` 把结果交给调用者。
外层 `responseText` 要等函数返回后才拿到结果。外层再次 print 会重复显示文字，但这不等于又发送一次模型请求。
`continue` 跳过本轮，不结束整个循环。

参考：[Python 控制流](https://docs.python.org/zh-cn/3/tutorial/controlflow.html)、[字符串 join](https://docs.python.org/zh-cn/3/library/stdtypes.html#str.join)。

## 顺手发现的问题，后续逐项学习

| 原代码 | 要理解的边界 |
| --- | --- |
| `timeout or ...` | 0 也会触发回退；未提供与传入无效值不应混为一谈 |
| `-> str` 但错误时 `return None` | 实际返回行为与类型提示不一致 |
| `except Exception` 后返回 None | 可能掩盖具体问题，应结合调用边界设计处理方式 |
| 循环前打印“成功” | 后续接收仍可能失败，不应把开始接收等同完成 |
| 顶层 `load_dotenv()` | 导入模块也会执行顶层语句，入口保护不覆盖它 |
| `apiKey` / `baseUrl` | 命名风格问题，不是语法错误 |

这些是基于已提供代码的分析；真实 SDK、模型参数兼容性和服务行为需要在实际调用时核对版本。
参考：[真值与布尔运算](https://docs.python.org/zh-cn/3/library/stdtypes.html#truth-value-testing)、[Python 模块](https://docs.python.org/zh-cn/3/tutorial/modules.html)。

## 架构先分职责

入口负责准备消息和展示结果；包装类负责封装调用；SDK 负责请求与响应处理。
当前先理解这三层职责，不为了“专业”提前拆成复杂项目。发生实际复用和测试需求后，再记录拆分方案与取舍。

## 待学习者验证

完成本章 README 中的片段收集函数，并解释为什么 return 通常应放在收集循环之后。
待確認：学习者系统、Python 版本、独立作答、真实依赖和服务配置。
本轮只做来源定位和笔记归档；没有运行此客户端，也不把上次助手环境的测试记作本轮通过。

## 4.2 · ReAct 从入口到工具执行

补充日期：2026-09-14。对应真实问题：CH04-Q002。状态：已讲解，待学习者独立验证。

完整讲解、源码版本、运行方式、边界分析与练习见 [4.2 ReAct 完整链路](practice/001_react_trace/README.md)。同目录提供 [无需密钥的离线演示](practice/001_react_trace/react42_offline_demo.py)。原教材 `docs/` 和 `code/` 未修改。

最重要的链路：

```text
ReActAgent.run
  → 拼接问题、工具描述和历史
  → HelloAgentsLLM.think
  → OpenAI Client 请求模型服务
  → 解析模型返回的 Action 文本
  → ToolExecutor 按名称查找函数
  → Python 执行 search(query)
  → 把 Action 和 Observation 追加到历史
  → 下一轮模型调用，或 Finish 返回答案
```

SDK 是工具包；Client 是客户端实例；HelloAgentsLLM 是项目封装；ReActAgent 是控制器。Agent 持有 LLM 包装和工具注册器，而不是继承它们。`agent.llm_client.client` 才是内层 OpenAI Client。

`registerTool('Search', description, search)` 保存函数对象，不执行搜索；`tool_function(tool_input)` 才执行。给模型的是工具名称和说明文本，不是函数实现。本章也未使用原生 API 的 `tools=`。

教材的 think 虽然流式打印，但返回前会把所有文本片段拼接完。因此 ReActAgent 拿到完整字符串后才解析工具动作。Thought 是提示生成的可见字段，不是 SDK 读取的内部推理；原脚本只把 Action 和 Observation 保存到 history。

history 在每次 run 开始时清空；下一轮通过重新构造 prompt 传递历史，不是 Client 自动记忆。max_steps 限制循环轮数，Finish 总结轮也计入。

本轮验证：核对原 ReAct.py 的 Git blob SHA，使用其原提示词和原 Agent 类注入离线替身，10 项控制流测试通过；独立演示也验证了两轮模型替身调用、一次搜索函数调用。测试包括复现 Finish 前缀误判和错误终止日志，因此通过不等于原版缺陷已修复。未安装并联调真实 SDK，未请求模型/搜索服务，没有验证学习者本地环境。

## 4.3—后续小节

Plan-and-Solve、Reflection 尚未开始本轮逐节学习；后续按真实提问继续记录。
