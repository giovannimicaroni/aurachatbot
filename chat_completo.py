from chatbot import RAGChatbot

import os

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

def init_chat():
    bot = RAGChatbot(OPENAI_API_KEY)
    bot.add_documents("M_a/")
    flag_chat = True

    history = []
    interacao = 0
    input_inicial = input("Olá! Estou aqui para te auxiliar com reflexões, insights e orientações relacionadas à heulosofia, que é a filosofia da felicidade e do bem-estar. Se tiver alguma dúvida, questionamento ou busca por inspiração, estou à disposição para ajudar. Como posso contribuir para o seu bem-estar hoje?\n")

    while flag_chat:

        response = bot.chat(input_inicial, history)

        hist_unity = {"interaction": interacao, "human":input_inicial,
                      "assistant": response['answer']}
        
        print(response["answer"])
        
        history.append(hist_unity)
        while len(history) > 10:
            history.pop(0)

        interacao += 1

        input_inicial = input()

        if input_inicial == "q":
            break


if __name__ == "__main__":
    
    init_chat()
    