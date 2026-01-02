# LangChain 学习之旅 (Android 开发者版)

欢迎来到 LangChain 学习实战项目。本项目专为有 Android 开发经验的工程师设计，通过类比 Android 核心概念来学习 AI 开发。

## 快速开始

### 1. 环境配置

```bash
# 1. 创建并激活虚拟环境 (已自动完成)
# source .venv/bin/activate

# 2. 安装依赖 (已自动完成)
# pip install -r requirements.txt

# 3. 配置 API Key
cp .env.example .env
```

**重要**：请打开 `.env` 文件，填入你的 OpenAI API Key。
如果你使用国内中转 (如 OneAPI)，请修改 `OPENAI_API_BASE` 地址。

### 2. 运行课程代码

**阶段一：Model I/O (View & ViewModel)**

```bash
python 01_model_io.py
```

## 课程目录

- **01_model_io.py**: 基础的 Model + Prompt + Parser 流程
- **02_lcel_chain.py**: 多步链与上下文累加 (`RunnablePassthrough.assign`)
- **03_structured_output.py**: 结构化输出与 Pydantic 模型
- **phase_01_03_summary.md**: 阶段性总结（01-03）
- **04_output_fixing_parser.py**: 解析失败自动修复（OutputFixingParser）
- **05_prompt_partials.py**: 使用 `Prompt.partial()` 预绑定格式说明
- **06_function_calling_tools.py**: 模型工具调用（Function Calling）
