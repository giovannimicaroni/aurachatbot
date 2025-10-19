from flask import Flask, render_template, request, jsonify, session
from chatbot import RAGChatbot
import os
from dotenv import load_dotenv
import secrets
from getpass import getpass
import sys
import tty
import termios

def custom_getpass(prompt="Password: "):
    """Custom getpass that shows asterisks while typing"""
    print(prompt, end='', flush=True)
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    
    try:
        tty.setraw(sys.stdin.fileno())
        password = ""
        while True:
            ch = sys.stdin.read(1)
            if ch == '\r' or ch == '\n':  # Enter pressed
                sys.stdout.write('\n')
                break
            elif ch == '\x7f' or ch == '\x08':  # Backspace
                if password:
                    password = password[:-1]
                    sys.stdout.write('\b \b')  # Erase character
            elif ord(ch) < 32:  # Skip control characters
                continue
            else:
                password += ch
                sys.stdout.write('*')
            sys.stdout.flush()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return password


load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("Please enter your OpenAI API Key (input will be hidden):")
    openai_api_key = custom_getpass("OpenAI API Key: ").strip()
    print("\n")

app = Flask(__name__)
#Recomendação de segurança
app.secret_key = secrets.token_hex(16)  

# Inicializar chatbot globalmente
if openai_api_key:
    os.environ["OPENAI_API_KEY"] = openai_api_key
    chatbot = RAGChatbot(openai_api_key=openai_api_key)
#Histórico de conversas em uma mesma sessão
conversations = {}

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/chat')
def chat_page():
    """Render the dedicated chat page"""
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get or create session ID
        if 'session_id' not in session:
            session['session_id'] = secrets.token_hex(8)
        
        session_id = session['session_id']
        
        # Get conversation history for this session
        if session_id not in conversations:
            conversations[session_id] = []
        
        history = conversations[session_id]
        
        # Get bot response
        response = chatbot.chat(message, history)
        
        # Update history
        hist_unity = {
            "interaction": len(history),
            "human": message,
            "assistant": response['answer']
        }
        history.append(hist_unity)
        
        # Keep only last 10 interactions
        while len(history) > 10:
            history.pop(0)
        
        conversations[session_id] = history
        
        return jsonify({
            'response': response['answer'],
            'sources': response.get('sources', [])
        })
    
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Recebe multipart/form-data com campos:
      - file: arquivo enviado
      - save_to_default: '1' ou '0'
    Se save_to_default == '1', salva o arquivo em arquivos_ong/ e adiciona à vectorstore.
    Caso contrário, adiciona apenas temporariamente à vectorstore.
    """
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'Nenhum arquivo enviado'}), 400

        file_storage = request.files['file']
        if file_storage.filename == '':
            return jsonify({'success': False, 'message': 'Arquivo sem nome'}), 400

        save_to_default = request.form.get('save_to_default', '0')

        # Decide se vai salvar em disco
        if save_to_default == '1' or save_to_default.lower() == 'true':
            chatbot.add_single_document(file_storage, save_to_dir='arquivos_ong')
            msg = f"Arquivo '{file_storage.filename}' salvo e adicionado à base principal."
        else:
            chatbot.add_single_document(file_storage)
            msg = f"Arquivo '{file_storage.filename}' adicionado temporariamente à base (não salvo em disco)."

        return jsonify({'success': True, 'message': msg}), 200

    except Exception as e:
        print(f"Erro ao processar upload: {e}")
        return jsonify({'success': False, 'message': f'Erro interno: {e}'}), 500

@app.route('/api/search', methods=['POST'])
def search():
    """Seach queries na pagina principal"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Get or create session ID
        if 'session_id' not in session:
            session['session_id'] = secrets.token_hex(8)
        
        session_id = session['session_id']
        
        # Get conversation history for this session
        if session_id not in conversations:
            conversations[session_id] = []
        
        history = conversations[session_id]
        
        # Get bot response
        response = chatbot.chat(query, history)
        
        # Update history
        hist_unity = {
            "interaction": len(history),
            "human": query,
            "assistant": response['answer']
        }
        history.append(hist_unity)
        
        # Keep only last 10 interactions
        while len(history) > 10:
            history.pop(0)
        
        conversations[session_id] = history
        
        return jsonify({
            'response': response['answer'],
            'sources': response.get('sources', [])
        })
    
    except Exception as e:
        print(f"Error in search endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/contact', methods=['POST'])
def contact():
    """Submissão de contatos"""
    try:
        data = request.get_json()
        name = data.get('name', '')
        email = data.get('email', '')
        message = data.get('message', '')
        

        print(f"Contact form submission:")
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Message: {message}")
        
        return jsonify({'success': True, 'message': 'Mensagem enviada com sucesso!'})
    
    except Exception as e:
        print(f"Error in contact endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    """Limpa o histórico da sessão atual"""
    try:
        if 'session_id' in session:
            session_id = session['session_id']
            if session_id in conversations:
                conversations[session_id] = []
        
        return jsonify({'success': True, 'message': 'History cleared'})
    
    except Exception as e:
        print(f"Error in clear-history endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500
  


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)