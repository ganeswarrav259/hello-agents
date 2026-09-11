# Hello-Agents · 学习笔记

[回到个人学习入口](../LEARNING.md) · [原教程](../README.md)

这里记录“我遇到了什么问题、理解了什么、改了什么、如何验证”，不是复制一本教材。
章节依据本 fork 初始化时的真实目录建立，版本见 [来源快照](source_snapshot.md)。

## 第一次只走这条线

[学习前准备](00_preparation/README.md) → [前言记录](preface/README.md) → [第 1 章](chapter01/README.md)。
当前已有 [第 4 章 HelloAgentsLLM 预习记录](chapter04/notes.md)，不要求跳过前面的基础。

## 正文章节导航

| 章节 | 学习笔记入口 | 本轮预留的重点 |
| --- | --- | --- |
| 01 | [初识智能体](chapter01/README.md) | 定义、组成、输入到行动的流程 |
| 02 | [智能体发展史](chapter02/README.md) | 发展脉络与不同方法的取舍 |
| 03 | [大语言模型基础](chapter03/README.md) | 模型基础、提示、能力边界 |
| 04 | [智能体经典范式构建](chapter04/README.md) | 基础客户端、ReAct、计划、反思 |
| 05 | [基于低代码平台的智能体搭建](chapter05/README.md) | 输入输出、节点和平台工作流 |
| 06 | [框架开发实践](chapter06/README.md) | 入口、框架抽象、状态与调用链 |
| 07 | [构建你的Agent框架](chapter07/README.md) | 接口、模块职责、依赖和测试 |
| 08 | [记忆与检索](chapter08/README.md) | 记忆、检索和存储的数据流 |
| 09 | [上下文工程](chapter09/README.md) | 信息选择、组织和预算 |
| 10 | [智能体通信协议](chapter10/README.md) | 调用双方、消息与协议边界 |
| 11 | [Agentic-RL](chapter11/README.md) | 训练流程、数据、资源和评估 |
| 12 | [智能体性能评估](chapter12/README.md) | 指标、测试样本与复现实验 |
| 13 | [智能旅行助手](chapter13/README.md) | 综合项目入口、服务与协作 |
| 14 | [自动化深度研究智能体](chapter14/README.md) | 研究流程、证据与报告生成 |
| 15 | [构建赛博小镇](chapter15/README.md) | 状态、角色和交互流程 |
| 16 | [毕业设计](chapter16/README.md) | 自己定义需求、实现与验收 |

这些“重点”是本学习区制定的学习目标，不表示已经完成逐节讲解。

## 每章只记住四个入口

```text
chapterXX/
├── README.md         # 原文、源码、学习目标和阅读顺序
├── notes.md          # 语法、原理、架构知识和复习
├── questions.md      # 每次提问、解释、修正和验证
└── practice/
    └── README.md     # 实际代码案例、调试和项目的放置规则
```

代码很多时，在本章 `practice/001_topic/` 中保留原件和修订版；现在不提前制造空项目。
原教程是 `docs/chapter4/`，个人笔记是 `learning_notes/chapter04/`，补零只用于让个人笔记排序整齐。

## 跨章节入口

[学习路线](01_roadmap.md) · [进度表](progress.md) · [协作规则](WORKFLOW.md) · [基础知识索引](foundations/README.md) · [扩展篇笔记](extra/README.md) · [待归档问题](pending/README.md) · [记录模板](templates/README.md) · [变更记录](CHANGELOG.md)

阅读资料不等于掌握。只有学习者能解释、修改并给出验证结果，才更新为相应的完成状态。
