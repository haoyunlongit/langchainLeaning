import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# 1. Load Environment Variables
load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    print("⚠️ Please set OPENAI_API_KEY in .env file")
    exit(1)

def run_rag_pipeline():
    print("--- 1. Loading Documents ---")
    file_path = "rag_data/company_policy.txt"
    loader = TextLoader(file_path)
    docs = loader.load()
    print(f"Loaded {len(docs)} document(s).")

    print("\n--- 2. Splitting Documents ---")
    # Split long text into smaller chunks for embedding
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,  # Characters per chunk
        chunk_overlap=50, # Overlap to maintain context
        add_start_index=True
    )
    splits = text_splitter.split_documents(docs)
    print(f"Split into {len(splits)} chunks.")
    print(f"Example chunk content: {splits[0].page_content[:100]}...")

    print("\n--- 3. Indexing (Embedding + VectorStore) ---")
    # Use OpenAI Embeddings to convert text to vectors
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # Create VectorStore (FAISS) - This stores vectors in memory (or disk)
    # We use FAISS (Facebook AI Similarity Search) for efficient similarity search
    vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
    print("VectorStore created successfully.")

    print("\n--- 4. Retrieval ---")
    # Create a retriever interface from the vectorstore
    # k=2 means we retrieve the top 2 most similar chunks
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 2})
    
    # Test retrieval alone
    query = "What is the policy for remote work equipment?"
    retrieved_docs = retriever.invoke(query)
    print(f"Query: {query}")
    print(f"Retrieved {len(retrieved_docs)} relevant chunks.")
    for i, doc in enumerate(retrieved_docs):
        print(f"  [Chunk {i}] Source: {doc.metadata['source']} | Content: {doc.page_content.strip()[:100]}...")

    print("\n--- 5. Generation (RAG Chain) ---")
    # Define the LLM
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    # Define the Prompt Template
    # The 'context' variable will be filled by the retriever
    system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer the question. "
        "If you don't know the answer, say that you don't know. "
        "Use three sentences maximum and keep the answer concise."
        "\n\n"
        "{context}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    # Create the Chain
    # 1. document_chain: Takes documents + query -> generates answer
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    # 2. retrieval_chain: Takes query -> fetches docs -> passes to document_chain
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    # Run the Chain
    questions = [
        "How much is the home office budget?",
        "Can I fly business class to New York (5 hour flight)?",
        "What tech stack do we use?"
    ]

    for q in questions:
        print(f"\nUser: {q}")
        response = rag_chain.invoke({"input": q})
        print(f"Agent: {response['answer']}")
        # We can also inspect the source documents used
        # print(f"Source Docs: {[d.page_content[:20] for d in response['context']]}")

if __name__ == "__main__":
    run_rag_pipeline()
