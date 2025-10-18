import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class RAGChatbot:
    def __init__(self, openai_api_key: str, model: str = "gpt-3.5-turbo"):
        """
        Initialize the chatbot with OpenAI API key.
        
        Args:
            openai_api_key: Your OpenAI API key
            model: OpenAI model to use (default: gpt-3.5-turbo)
        """
        os.environ["OPENAI_API_KEY"] = openai_api_key
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model,
            temperature=0.7,
            streaming=True
        )
        
        # Initialize embeddings for RAG
        self.embeddings = OpenAIEmbeddings()
        
        # Initialize memory for conversation history
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
        # Vector store (will be None until documents are added)
        self.vectorstore = None
        self.chain = None
        
    def add_documents(self, texts: list[str], chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Add documents to the RAG system.
        
        Args:
            texts: List of text strings to add to the knowledge base
            chunk_size: Size of text chunks for splitting
            chunk_overlap: Overlap between chunks
        """
        # Split texts into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )
        
        # Create documents
        documents = [Document(page_content=text) for text in texts]
        splits = text_splitter.split_documents(documents)
        
        # Create or update vector store
        if self.vectorstore is None:
            self.vectorstore = FAISS.from_documents(splits, self.embeddings)
        else:
            self.vectorstore.add_documents(splits)
        
        # Create conversational retrieval chain
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
            memory=self.memory,
            return_source_documents=True,
            verbose=False
        )
        
        print(f"✓ Added {len(splits)} document chunks to knowledge base")
    
    def chat(self, question: str) -> dict:
        """
        Chat with the bot. Uses RAG if documents are loaded, otherwise direct chat.
        
        Args:
            question: User's question
            
        Returns:
            Dictionary with 'answer' and optional 'sources'
        """
        if self.chain is not None:
            # RAG-enabled chat
            response = self.chain.invoke({"question": question})
            return {
                "answer": response["answer"],
                "sources": response.get("source_documents", [])
            }
        else:
            # Direct chat without RAG
            from langchain.chains import LLMChain
            from langchain.prompts import ChatPromptTemplate
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful AI assistant specialized in heulosophy."),
                ("human", "{question}")
            ])
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            response = chain.invoke({"question": question})
            
            return {
                "answer": response["text"],
                "sources": []
            }
    
    def clear_memory(self):
        """Clear conversation history."""
        self.memory.clear()
        print("✓ Conversation history cleared")


# Example usage
if __name__ == "__main__":
    # Initialize chatbot
    bot = RAGChatbot(OPENAI_API_KEY)
    
    print("=== Basic Chat (No RAG) ===")
    response = bot.chat("Hello! What can you help me with?")
    print(f"Bot: {response['answer']}\n")
    
    # Add documents for RAG
    print("\n=== Adding Documents ===")
    sample_texts = [
        """
        LangChain is a framework for developing applications powered by language models.
        It enables applications that are context-aware and can reason about their responses.
        """,
        """
        RAG (Retrieval-Augmented Generation) combines the benefits of retrieval-based 
        and generative AI models. It retrieves relevant documents and uses them to 
        generate more accurate and contextual responses.
        """,
        """
        Vector databases store embeddings of text chunks, allowing for semantic search.
        This enables finding relevant information based on meaning rather than keywords.
        """
    ]
    bot.add_documents(sample_texts)
    
    # Chat with RAG
    print("\n=== Chat with RAG ===")
    response = bot.chat("What is RAG?")
    print(f"Bot: {response['answer']}")
    print(f"Sources used: {len(response['sources'])} documents\n")
    
    response = bot.chat("How does it work with vector databases?")
    print(f"Bot: {response['answer']}\n")
    
    # Clear conversation history
    bot.clear_memory()