from flask import Flask, render_template, request, jsonify, session
from chatbot import RAGChatbot
import os
from dotenv import load_dotenv
import secrets

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # For session management

# Initialize chatbot globally
chatbot = RAGChatbot(OPENAI_API_KEY)

# Store conversation histories in memory (use Redis/DB for production)
conversations = {}

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

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

@app.route('/api/search', methods=['POST'])
def search():
    """Handle search queries"""
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
    """Handle contact form submissions"""
    try:
        data = request.get_json()
        name = data.get('name', '')
        email = data.get('email', '')
        message = data.get('message', '')
        
        # Here you would typically send an email or save to database
        # For now, just log it
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
    """Clear conversation history for current session"""
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