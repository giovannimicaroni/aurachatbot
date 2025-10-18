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
from PyPDF2 import PdfReader

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set. Add it to your .env or export it in the shell.")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


class RAGChatbot:
    def __init__(self, openai_api_key: str, model: str = "gpt-5-nano"):
        """
        Initialize the chatbot with OpenAI API key and other attributes.
        """
        self.openai_api_key = openai_api_key
        
        self.llm = ChatOpenAI(
            model=model,
            temperature=0.7,
            streaming=True
        )
        
        self.embeddings = OpenAIEmbeddings()
        
        self.vectorstore = None
        self.chain = None 
        
        self.add_documents(texts_path="arquivos_ong/")
    
    def _format_docs(self, docs: List[Document]) -> str:
        """Formats retrieved documents into a single string for the prompt. Adds simple metadata."""
  
        return "\n\n".join(f"Source: {doc.metadata.get('source', 'N/A')}\nContent: {doc.page_content}" for doc in docs)

    def _setup_rag_chain(self):
        """Builds the core RAG chain using LCEL without history components.
        The input is the question, which is passed directly to the retriever.
        """
        
        answer_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "Você é um assistente de IA amigável especializado em Eulosofia. Sua tarefa é conversar com o usuário e resonder suas perguntas. As perguntas podem ser sobre o contexto fornecido ou sobre o histórico da conversa. Responda as perguntas em português. Use somente o contexto fornecido ou o histórico de conversa para responder à pergunta. Se a resposta não estiver no contexto ou no histórico da conversa, diga que não sabe, mantendo um tom conversacional. \n\n Histórico da conversa:{history} \n\nContexto:\n{context}"),
                ("human", "Question: {question}"),
            ])

        return (
            {
                "context": itemgetter("question") | self.vectorstore.as_retriever(search_kwargs={"k": 3}) | self._format_docs,
                "question": itemgetter("question"),
                "history": itemgetter("history")
            }
            | answer_prompt 
            | self.llm 
            | StrOutputParser()
        )
    
    
    def add_documents(self, texts_path, chunk_size: int = 1000, chunk_overlap: int = 50, batch_size: int = 500):
            """
            Add documents to the RAG system and initializes the stateless LCEL chain.
            Documents are split into chunks and uploaded to the vectorstore in batches.
            """
            def _get_texts(texts_path=texts_path):
                data = []
                ind = 0
                for dirpath, dirnames, filenames in os.walk(texts_path):
                    for filename in filenames:
                        source = os.path.join(dirpath, filename)

                        if filename.lower().endswith(".txt"):
                            ind += 1

                            try:
                                with open(source, "r", encoding="utf-8", errors="ignore") as f:
                                    text = f.read()
                                data.append({"indice": ind ,"source": source, "text": text, "is_pdf": False})
                            except Exception as e:
                                print("Erro na leitura do arquivo")

                        elif filename.lower().endswith(".pdf"):
                            ind += 1
                            text = ""

                            try:
                                reader = PdfReader(source)
                                for page in reader.pages:
                                    text += (page.extract_text() or "")
                            except Exception:
                                print("Erro de acesso ao PyPDF2")

                            data.append({"indice": ind, "source": source, "text": text, "is_pdf": True})
                        else:
                            print(f"Formato não aceito: {source}")

                return data
            
            texts = _get_texts(texts_path)

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len
            )
            
            documents = [
            Document(page_content=text_dicts["text"], 
                        metadata={
                    "indice": text_dicts.get("indice"),
                        "source": text_dicts.get("source"),
                        "is_pdf": text_dicts.get("is_pdf", False),
                    }) for text_dicts in texts]
            
            splits = text_splitter.split_documents(documents)

            print(f"Número de chunks {len(splits)}")

            if self.vectorstore is None:
                self.vectorstore = InMemoryVectorStore(self.embeddings)

            # Add in batches
            total = len(splits)
            num_batches = (total + batch_size - 1) // batch_size
            for i in range(0, total, batch_size):
                batch = splits[i:i + batch_size]
                self.vectorstore.add_documents(batch)
                print(f"Added batch {i // batch_size + 1}/{num_batches} ({len(batch)} chunks)")

            self.chain = self._setup_rag_chain()
            
            print(f"✓ Added {len(splits)} document chunks to knowledge base.")

    def chat(self, question: str, history: str) -> dict:
        """
        Chat with the bot. Each message is independent. input: {"question": question}
        """
        if self.chain is not None:

            print(f"\n\n {history}")
            
            response = self.chain.invoke({"question": question, "history": history})

            return {
                "answer": response,
                "sources": []
            }
        else:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "Você é um assistente de IA especializado em heulosofia. Esse é o histórico da conversa {history}"),
                ("human", "{question}")
            ])

            print(prompt)

            chain = prompt | self.llm | StrOutputParser()
            result = chain.invoke({"question": question, "history": history})

            return {
                "answer": result,
                "sources": []
            }


def generate_audio(text):
    from pathlib import Path
    from openai import OpenAI

    client = OpenAI()
    speech_file_path = Path(__file__).parent / "speech.mp3"

    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="ash",
        input=text,
        instructions="Speak in a assertive and positive tone.",
    ) as response:
        response.stream_to_file(speech_file_path)

if __name__ == "__main__":
    bot = RAGChatbot(OPENAI_API_KEY)
    
    # Direct chat
    response = bot.chat("Olá! Como posso te ajudar?", "")
    print(f"Bot: {response['answer']}\n")
    
    # Add documents for RAG
    print("\n=== Adding Documents ===")

    
    # Chat with Stateless RAG
    print("\n=== Chat with Stateless RAG ===")
    
    q1 = "O que o palestrante define como 'Saneamento Mental'?"
    response = bot.chat(q1, "")
    print(f"Q1: {q1}")
    print(f"Bot: {response['answer']}")
    print("-" * 20)
    
    q2 = "Cite os quatro procedimentos ou ferramentas essenciais para praticar o 'Zendrômeda' e promover a auto-equalização."
    response = bot.chat(q2, "")
    print(f"Q2: {q2}")
    print(f"Bot: {response['answer']}")
    print("-" * 20)
    
    q3 = "Como a análise dos sonhos, mesmo os pesadelos, pode resultar em uma sensação de bem-estar e clareza ao acordar? Utilize os exemplos dos participantes para explicar o processo."
    response = bot.chat(q3, "")
    print(f"Q3: {q3}")
    print(f"Bot: {response['answer']}")
    print("-" * 20)
