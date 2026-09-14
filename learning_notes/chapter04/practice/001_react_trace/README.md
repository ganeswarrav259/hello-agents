# 4.2 ReAct：从入口到工具执行的完整链路

[本章知识笔记](../../notes.md) · [问题 CH04-Q002](../../questions.md#ch04-q002--42-react-代码项目完整讲解)

记录日期：2026-09-14。状态：已讲解，待学习者独立复述和修改；不是掌握证明。

本次核对仓库 main 的读取基线为 `cd40b48b2acbcf41f1f2e40b006a859444d478cd`。关键源码为 [ReAct.py](../../../../code/chapter4/ReAct.py)、[tools.py](../../../../code/chapter4/tools.py)、[llm_client.py](../../../../code/chapter4/llm_client.py)，对应 Git blob 分别为 `04ae533df7d71f14a685eb0349e024291fda7c90`、`a4665c2a6c8d352f9fe6e7647a638bcfa98e262d`、`0793e234b8456e986fe23e426136033c1d44519a`。同时对照 [第四章教材](../../../../docs/chapter4/第四章%20智能体经典范式构建.md) 的 4.2。正文和独立脚本的 Finish 解析略有不同，以下按独立 `.py` 文件解释，不混成同一份实现。

## 一、这一节到底做了什么

ReAct 是 Reasoning + Acting，不是前端 React。在这个教学项目中，模型根据问题、工具描述及历史输出一个文本动作；Python 解析动作、调用已注册的函数，把返回值加入历史，再询问模型，直到得到 Finish 或退出。

```text
agent.run(question)
    ↓
构造提示词：工具说明 + 原问题 + Action/Observation 历史
    ↓
llm.think(messages) → OpenAI Client → 模型服务
    ↓
返回完整字符串，例如 Action: Search[查询词]
    ↓
_parse_output → _parse_action
    ↓
通过 ToolExecutor 找到本地 search 函数
    ↓
search(query) → SerpApi Client → 搜索服务 → 结果字符串
    ↓
追加 Action 和 Observation → 下一轮
    ↓
模型输出 Action: Finish[答案] → run 返回字符串
```

模型负责提出动作；应用代码负责执行动作。SDK 不会因为模型输出了 Search[...] 就自行运行 Python 函数。

## 二、文件、类、对象分别是什么

| 名称 | 性质 | 本节责任 |
| --- | --- | --- |
| openai | 第三方 SDK 的 Python 包 | API 请求与响应处理 |
| OpenAI | SDK 中的客户端类 | 创建请求客户端 |
| HelloAgentsLLM | 教材自定义类 | 保存模型配置，封装一次模型调用 |
| ToolExecutor | 教材自定义类 | 保存工具描述和函数对象，按名称查找 |
| search | 普通 Python 函数 | 请求搜索服务，整理返回结果 |
| ReActAgent | 教材自定义类 | 管理循环、解析、历史与终止 |

注意对象嵌套：

```text
agent：ReActAgent
├── llm_client → llm：HelloAgentsLLM
│   └── client → OpenAI 客户端对象
├── tool_executor → ToolExecutor
│   └── tools['Search']['func'] → search 函数对象
├── history → list[str]
└── max_steps → 5
```

所以 `agent.llm_client` 不是 OpenAI 对象；`agent.llm_client.client` 才是。构造时保存对象引用，不是复制模型，不是下载权重。

## 三、先从文件末尾入口读起

```python
llm = HelloAgentsLLM()
tool_executor = ToolExecutor()
tool_executor.registerTool('Search', search_desc, search)
agent = ReActAgent(llm_client=llm, tool_executor=tool_executor)
agent.run(question)
```

前几步准备模型客户端、注册工具、组装 Agent；进入 `run()` 后才执行循环。`if __name__ == '__main__'` 下的示例只有直接运行该文件时执行；导入模块时仍会执行其他顶层语句，例如 `load_dotenv()`。

ReActAgent 初始化中的 `self.llm_client = llm_client`，右边是传入参数，左边是保存在当前 Agent 实例上的属性。进入 HelloAgentsLLM.think 时，其中的 self 又是 LLM 包装实例，而不是 Agent。

## 四、工具注册的核心：字符串到函数对象的映射

```python
tool_executor.registerTool('Search', search_desc, search)
```

注册后相当于：

```python
tool_executor.tools = {
    'Search': {
        'description': search_desc,
        'func': search,
    }
}
```

`'Search'` 是给模型使用的动作名称；`search` 是函数对象；`search('查询词')` 才是在调用函数。注册时传 `search`，不是 `search()`，否则会立即尝试执行它并把返回值当作工具。

`getAvailableTools()` 只把名称和描述转成文本给模型看，不会上传 Python 函数实现，也不会执行搜索。`getTool(name)` 返回已保存的函数对象；真正执行在 ReActAgent 的 `tool_function(tool_input)`。

```python
tool_function = tool_executor.getTool('Search')
# 此处拿到函数，还没有搜索。
observation = tool_function('查询词')
# 这里才进入 search(query)。
```

这份实现虽然叫 ToolExecutor，实际调用函数的那一行写在 ReActAgent.run 内部。未注册名称查找得到 None，再被转成错误 Observation。

## 五、提示词是文本协议，不是可执行程序

模板用 `.format(tools=..., question=..., history=...)` 填入三个动态部分。`{tools}` 是真正的格式化占位符；`{{tool_name}}` 使用双花括号，是为了让格式化后仍显示字面量 `{tool_name}`。

实际请求中的消息是：

```python
messages = [{'role': 'user', 'content': prompt}]
```

因此这里不是把工具通过 OpenAI API 的 `tools=` 参数注册，也不是以原生 tool-call 消息维护历史，而是把规则、问题和历史全部放进一个 user 消息字符串。教材称它为系统提示词设计，但源码并没有使用 `role='system'`。

`Thought:` 是提示词要求模型生成的可见文本字段，不等于读取模型内部推理。在这个脚本里，它主要用于打印；真正驱动控制流的是 Action。历史只追加 Action 和 Observation，没有保存 Thought。

## 六、一轮循环逐步发生什么

1. 递增 current_step，读取工具描述，把 history 用换行拼接。
2. 填充模板，构造 messages，调用 llm.think。
3. think 内调用 OpenAI Client 的 chat.completions.create，开启流式；逐片段打印并收集，最后 join 成完整字符串再返回。因此 Agent 不会在一个 chunk 到来时就立即执行工具。
4. `_parse_output` 从完整文本提取 Thought 和 Action；如果没有 Action，就提前退出。
5. 如果 Action 以 Finish 开头，调用 `_parse_action_input` 提取答案并 return。
6. 否则 `_parse_action` 从 `Search[查询词]` 提取名称 Search 和输入查询词。
7. 按名称查函数并实际调用；获取工具返回值作为 Observation。
8. 把 Action 和 Observation 追加到 history，进入下一轮。

三个解析器只做文本处理，不会联网，也不会执行函数。例如：

```text
'Action: Search[示例品牌最新手机]'
        ↓ _parse_output
'Search[示例品牌最新手机]'
        ↓ _parse_action
('Search', '示例品牌最新手机')
```

原正则 `(\w+)\[(.*)\]` 中两个捕获组分别对应名称和中括号内的文本，`re.DOTALL` 让点号也匹配换行。它是教学用解析规则，不是健壮的通用协议。

## 七、搜索函数里的第二条 API 链路

`search(query)` 读取 SERPAPI_API_KEY，把查询词放入参数 q，使用 `SerpApiClient(params).get_dict()` 获取搜索结果字典。返回值的优先级是 answer_box_list、answer_box.answer、knowledge_graph.description，最后才是前三条 organic_results 的标题和摘要。

这说明项目有两种 Client：OpenAI Client 请求模型服务；SerpApi Client 请求搜索服务。它们有不同密钥和返回结构。

搜索返回的不是 SDK 自动附加给模型的上下文，而是普通 Python 字符串。只有 `self.history.append(...)` 加上下一轮模板填充，模型才获得这些资料。当前函数没有继续抓取网页正文，而且常规结果只保留标题和摘要，未保留来源链接，不能把它等同于严格的事实核验或引用系统。

## 八、两轮演示：所有资料均为虚构

问题：示例品牌最新手机是什么，主要卖点是什么？

第一轮模型替身返回：

```text
Thought: 需要查询示例资料。
Action: Search[示例品牌最新手机]
```

Python 搜索替身返回：

```text
【离线模拟】示例品牌 A1，主要卖点是续航与影像。
```

此时 history 为：

```python
[
    'Action: Search[示例品牌最新手机]',
    'Observation: 【离线模拟】示例品牌 A1，主要卖点是续航与影像。',
]
```

第二轮发送的提示词仍包含原问题，额外带上以上历史。模型替身返回 `Action: Finish[示例品牌 A1，主要卖点是续航与影像。]`，run 提取答案并返回，不再搜索。

本例是 2 次模型方法调用、1 次搜索函数调用、1 次 Agent.run。不是一次模型请求自己运行所有步骤；第二轮也不是模型在原请求里自动记住工具结果。

## 九、控制流边界和修订建议

| 原版行为 | 学习时必须区分 |
| --- | --- |
| max_steps 默认 5 | 限制的是 Agent 迭代轮数；Finish 那轮也占一次，并非最多搜索 5 次再免费总结 |
| 每次 run 开头清空 history | 是单个任务内部的历史，不是跨对话长期记忆 |
| 缺响应或缺 Action 就 break | 随后仍打印“已达到最大步数”，会误报真实终止原因 |
| action.startswith('Finish') | FinishLater[...] 也会误入结束分支；应先严格解析名称，再判断是否等于 Finish |
| re.match 解析动作 | 接受部分尾随垃圾文本，多条 Action、格式漂移等可能被错误解析 |
| think 标注返回 str，异常却返回 None | 应明确 str/None 或抛出具体异常，不能把失败当作正常回答 |
| 搜索错误作为字符串 | 模型可能重试，也可能误当资料；工程版需要结构化错误和限制 |

这些建议没有直接改动教材。升级原生 function calling 可以减少手写文本协议的歧义，但自定义客户端函数仍需要由应用执行、返回工具结果，并处理权限、参数、超时和外部内容的可信边界。框架命名不是自动的安全保证。

## 十、怎么运行原教材

建议在独立虚拟环境安装与旧教程匹配的依赖：

```bash
python -m pip install openai python-dotenv google-search-results
cd code/chapter4
python ReAct.py
```

在适当位置准备不提交到 Git 的 `.env`：

```dotenv
LLM_API_KEY=替换为模型服务密钥
LLM_MODEL_ID=替换为兼容的模型ID
LLM_BASE_URL=替换为兼容的服务地址
LLM_TIMEOUT=60
SERPAPI_API_KEY=替换为搜索服务密钥
```

这些是教材使用的 LLM_* 变量名，不能直接照搬其他示例的 OPENAI_* 后假定会被读取。模型/服务需要支持源码使用的 Chat Completions、流式输出及 temperature 参数。

版本注意：教材的 `from serpapi import SerpApiClient` 对应旧 `google-search-results` 包。SerpApi 官方仓库已经提示迁移到新实现，不能只把安装命令改成 `pip install serpapi` 而保留旧 API 用法。这里为了对照教材，保留旧依赖方式；生产迁移应作为独立任务。

## 十一、离线演示与实际验证范围

同目录的 [react42_offline_demo.py](react42_offline_demo.py) 只使用 Python 标准库，不读密钥、不联网。保留原版 ReActAgent 和提示词，替换模型、搜索、工具注册包装与启动入口；因此也刻意保留原解析器的已知局限，不是生产修订版。

```bash
python learning_notes/chapter04/practice/001_react_trace/react42_offline_demo.py
```

本轮实际运行了离线演示，断言通过：模型替身调用 2 次，搜索函数调用 1 次，第二轮收到 Observation，历史不包含 Thought，run 返回预期字符串。

此外，对复制后校验 Git blob SHA 完全一致的原 ReAct.py，提取其原提示词和原 ReActAgent 类，注入离线模型/注册器替身，实际运行 10 项控制流测试，全部通过。覆盖两轮历史、首轮直接 Finish、预算包含总结轮、错误退出误报、缺 Action、未知工具反馈、无效动作反馈、Finish 前缀误判、尾随文本未拒绝，以及每次 run 清空历史。这里“通过”包括成功复现原版缺陷，并不代表缺陷已经修复。

未安装和联调真实 OpenAI/SerpApi SDK；没有请求真实模型或搜索服务；不保证学习者本地依赖及服务兼容性；没有将教材输出或模拟资料当作本次真实搜索结果。

## 十二、学习者练习

新增一个只计算文本长度的工具，不改 ReActAgent.run：

```python
def text_length(text: str) -> str:
    return str(len(text))

tool_executor.registerTool('Length', '返回输入字符串的长度。', text_length)
```

要求解释 `Action: Length[hello]` 怎样变成 `text_length('hello')`，并说明为什么注册时不能写 `text_length()`。独立完成后再更新掌握状态。

## 参考资料

- 本文开头列出的仓库原文件和 blob 版本，是本章行为分析的主要证据。
- [Python 控制流与函数](https://docs.python.org/3/tutorial/controlflow.html)
- [Python 正则表达式](https://docs.python.org/3/library/re.html)
- [Python 字符串格式化规则](https://docs.python.org/3/library/string.html)
- [OpenAI function calling](https://developers.openai.com/api/docs/guides/function-calling)
- [SerpApi 旧 Python 包及迁移提醒](https://github.com/serpapi/google-search-results-python)
