# LangChain 学习路线图（阶段 06–13）

## 概述
- 目标：以工程视角掌握 LangChain 的高频能力，形成可复用的组件化与管线化思维。
- 产出：每节 1 个可运行脚本 + 1 页总结卡片；逐步汇总到 README 与阶段性总览。

## 已完成（01–05）
- 01 Model I/O：Prompt | Model | Parser 基本管线
- 02 LCEL Chain：多步链与上下文累加（RunnablePassthrough）
- 03 Structured Output：Pydantic + Parser + format_instructions
- 04 OutputFixingParser：解析失败自动修复（兜底策略）
- 05 Prompt.partial：在 Prompt 层预绑定格式说明

## 阶段 06：工具调用（Function Calling）
- 目标：让模型“调用工具”而不是编造答案（如时间/汇率/本地计算）。
- 要点：StructuredTool、函数签名、bind_tools、错误处理与返回结构约束。
- 产出：06_function_calling_tools.py、06_function_calling_summary.md。

## 阶段 07：Agent 基础（LangGraph）
- 目标：多步决策与状态管理，选择合适工具并可循环迭代。
- 要点：状态图、停机条件、记忆与上下文策略、节点与边的组织。
- 产出：07_agent_basics.py、07_agent_summary.md。

## 阶段 08：检索增强（RAG）
- 目标：接入外部知识，实现“先检索、后生成”。
- 要点：Loader、Splitter、Embeddings、VectorStore、Retriever 的组合与取舍。
- 产出：08_rag_basic.py、08_rag_summary.md。

## 阶段 09：Prompt 设计与模式
- 目标：稳定输出与高质量指令设计（System、Few-shot、结构提示）。
- 要点：任务分解、拒绝/澄清策略、模板复用与版本化管理。
- 产出：09_prompt_patterns.py、09_prompt_summary.md。

## 阶段 10：会话记忆（Memory）
- 目标：让对话“有记忆”，并控制记忆成本与污染。
- 要点：BufferMemory、SummaryMemory、检索式记忆的取舍与组合。
- 产出：10_memory_strategies.py、10_memory_summary.md。

## 阶段 11：可靠性与性能
- 目标：稳定/高并发/低成本的工程落地。
- 要点：重试与退避、并发/批处理、Streaming、缓存与去重策略。
- 产出：11_reliability_performance.py、11_reliability_summary.md。

## 阶段 12：评估与监控
- 目标：数据化质量评估与运行时可观测性。
- 要点：LLM-as-judge、用例集评估、成本/延迟监控、日志与追踪。
- 产出：12_evaluation_monitoring.py、12_evaluation_summary.md。

## 阶段 13：部署与配置
- 目标：Provider 抽象、环境配置、模块化封装与 CLI/服务化。
- 要点：配置管理（.env）、模型切换、策略注入、插件化与 README 入口更新。
- 产出：13_deploy_config.py、13_deploy_summary.md。

## 综合实战项目：Android Library Advisor
- 能力整合：工具调用 + RAG + 结构化输出 + Fixing 兜底 + partial 提示。
- 产出：project_library_advisor.py、项目 README、示例数据。

## 验证策略
- 每节运行示例脚本；关键节（06/08/12/13）加入故障注入与兜底验证。
- 阶段汇总：phase_06_14_summary.md 汇总架构图、组合模式与工程取舍。

## 文档化
- 每节产出总结卡片并更新 README 课程目录。
- 保持“一句话总结 + 关键要点 + 关联代码链接”的统一格式。
