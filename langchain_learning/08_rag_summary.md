# Phase 08: 检索增强生成 (RAG)

## 1. 核心概念
RAG (Retrieval-Augmented Generation) 是一种将**外部知识**注入到 LLM 上下文的技术架构。

核心流程（RAG Triad）：
1.  **Retrieve (检索)**：根据用户问题，从知识库中找到最相关的片段。
2.  **Augment (增强)**：将检索到的片段作为“上下文”放入 Prompt 中。
3.  **Generate (生成)**：LLM 基于增强后的 Prompt 生成答案。

## 2. 关键组件 (LangChain 抽象)

| 组件 | 作用 | 常见实现 |
| :--- | :--- | :--- |
| **Loader** | 加载各种格式的数据源 | `TextLoader`, `PyPDFLoader`, `WebBaseLoader` |
| **Splitter** | 将长文档切分为适合 LLM 窗口的小块 | `RecursiveCharacterTextSplitter` (推荐) |
| **Embedding** | 将文本转化为向量 (语义表示) | `OpenAIEmbeddings`, `HuggingFaceEmbeddings` |
| **VectorStore** | 存储与索引向量，支持相似度搜索 | `FAISS` (本地/轻量), `Chroma`, `Pinecone` |
| **Retriever** | 检索接口，定义如何查找文档 | `VectorStoreRetriever`, `MultiQueryRetriever` |

## 3. 代码实现要点 (`08_rag_basic.py`)

### A. 数据准备 (Indexing)
```python
# 1. 加载
loader = TextLoader("rag_data/company_policy.txt")
docs = loader.load()

# 2. 切分 (Chunking)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
splits = text_splitter.split_documents(docs)

# 3. 向量化与存储
vectorstore = FAISS.from_documents(splits, OpenAIEmbeddings())
```

### B. 检索与生成 (Retrieval & Generation)
使用 `create_retrieval_chain` 快速构建标准流水线：

```python
# 1. 定义检索器
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

# 2. 定义生成链 (Stuff Documents Chain)
# 负责将检索到的 docs 填充进 prompt 的 {context} 占位符
question_answer_chain = create_stuff_documents_chain(llm, prompt)

# 3. 组合 RAG 链
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

# 4. 调用
response = rag_chain.invoke({"input": "What is the budget?"})
print(response["answer"])
```

## 4. 常见问题与工程取舍
1.  **Chunk Size**: 切太小会丢失上下文，切太大会引入噪声。通常 500-1000 chars 是起点。
2.  **Overlap**: 必须保留重叠 (e.g., 10-20%) 以防止句子被切断导致语义丢失。
3.  **VectorStore 选择**:
    *   **FAISS/Chroma (Local)**: 适合开发测试、小规模数据、无运维成本。
    *   **Pinecone/Weaviate (Cloud)**: 适合大规模生产环境，支持持久化和元数据过滤。
4.  **"Stuff" Chain**: 最简单的合并策略，直接把所有相关文档塞进 Prompt。如果文档太长，需考虑 `MapReduce` 或 `Refine` 策略。
