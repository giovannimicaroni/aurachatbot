import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter
from typing import List

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set. Add it to your .env or export it in the shell.")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

class RAGChatbot:
    def __init__(self, openai_api_key: str, model: str = "gpt-3.5-turbo"):
        """
        Initialize the chatbot with OpenAI API key.
        """
        self.openai_api_key = openai_api_key
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model,
            temperature=0.7,
            streaming=True
        )
        
        # Initialize embeddings for RAG
        self.embeddings = OpenAIEmbeddings()
        
        # Vector store (will be None until documents are added)
        self.vectorstore = None
        # self.chain will now hold the simple LCEL RAG chain (no history wrapper)
        self.chain = None 
    
    def _format_docs(self, docs: List[Document]) -> str:
        """Formats retrieved documents into a single string for the prompt."""
        # Note: Added metadata fetching for better context clarity
        return "\n\n".join(f"Source: {doc.metadata.get('source', 'N/A')}\nContent: {doc.page_content}" for doc in docs)

    def _setup_stateless_rag_chain(self):
        """Builds the core RAG chain using LCEL without history components."""
        
        # 1. Answer Generator Prompt
        # The prompt is simplified since it doesn't need to reference chat history.
        answer_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "Você é um assistente de IA especializado em heulosofia. Responda as perguntas em português. Use SOMENTE o contexto fornecido para responder à pergunta. Se a resposta não estiver no contexto, diga que não sabe, mantendo um tom conversacional.\n\nContexto:\n{context}"),
                ("human", "Question: {question}"),
            ]
        )
        
        # 2. Stateless LCEL RAG Chain
        # The input is the question, which is passed directly to the retriever.
        return (
            {
                # The question is used directly for retrieval (no history-aware rephrasing)
                "context": itemgetter("question") | self.vectorstore.as_retriever(search_kwargs={"k": 3}) | self._format_docs,
                "question": itemgetter("question"), # Original question passed to the next step
            }
            | answer_prompt 
            | self.llm 
            | StrOutputParser()
        )

# --------------------------------------------------------------------------------------
    def add_documents(self, texts: list[str], chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Add documents to the RAG system and initializes the stateless LCEL chain.
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )
        
        # Added a simple metadata source for display
        documents = [Document(page_content=text, metadata={"source": f"doc_{i}"}) for i, text in enumerate(texts)]
        splits = text_splitter.split_documents(documents)
        
        if self.vectorstore is None:
            self.vectorstore = InMemoryVectorStore(self.embeddings)
            self.vectorstore.add_documents(splits)
        else:
            self.vectorstore.add_documents(splits)
        
        self.chain = self._setup_stateless_rag_chain()
        
        print(f"✓ Added {len(splits)} document chunks to knowledge base.")

    # --- UPDATED METHOD: Simplified chat interface ---
    def chat(self, question: str) -> dict:
        """
        Chat with the bot. Each message is independent.
        """
        if self.chain is not None:
            # RAG-enabled chat using the stateless LCEL chain
            # The input is simple: {"question": question}
            response = self.chain.invoke({"question": question})
            
            return {
                "answer": response,
                "sources": [] # Source retrieval is simplified out
            }
        else:
            # Direct chat without RAG
            prompt = ChatPromptTemplate.from_messages([
                ("system", "Você é um assistente de IA especializado em heulosofia. Responda as perguntas em português."),
                ("human", "{question}")
            ])
            chain = prompt | self.llm | StrOutputParser()
            result = chain.invoke({"question": question})

            return {
                "answer": result,
                "sources": []
            }



# Example usage
if __name__ == "__main__":
    bot = RAGChatbot(OPENAI_API_KEY)
    
    # Direct chat
    response = bot.chat("Olá! Como posso te ajudar?")
    print(f"Bot: {response['answer']}\n")
    
    # Add documents for RAG
    print("\n=== Adding Documents ===")
    sample_texts = [
        """
        LangChain é um framework para desenvolver aplicações alimentadas por modelos de linguagem.
        Ele permite criar aplicações que são conscientes do contexto e podem raciocinar sobre suas respostas.
        """,
        """
        RAG (Retrieval-Augmented Generation) combina os benefícios de modelos de IA baseados em recuperação
        e de modelos generativos. Ele recupera documentos relevantes e os utiliza para gerar respostas
        mais precisas e contextualizadas.
        """,
        """
        Bancos de dados vetoriais armazenam embeddings de trechos de texto, permitindo buscas semânticas.
        Isso possibilita encontrar informações relevantes com base no significado, em vez de palavras-chave.
        """
    ]
    bot.add_documents(sample_texts)
    
    # Chat with Stateless RAG
    print("\n=== Chat with Stateless RAG ===")
    
    # 1. First question
    q1 = "O que é RAG no contexto de modelos de linguagem?"
    response = bot.chat(q1)
    print(f"Q1: {q1}")
    print(f"Bot: {response['answer']}")
    print("-" * 20)
    
    # 2. Follow-up question (The system CANNOT use the answer from Q1 to understand this)
    q2 = "Como ele funciona em bases de dados vetoriais?"
    response = bot.chat(q2)
    print(f"Q2: {q2}")
    print(f"Bot: {response['answer']}")
    print("-" * 20)
    
    # 3. New question, explicitly stating the topic (to confirm independence)
    q3 = "O que a LangChain permite criar?"
    response = bot.chat(q3)
    print(f"Q3: {q3}")
    print(f"Bot: {response['answer']}")
    print("-" * 20)