from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv
import sqlite3
from datetime import datetime

# Configuration
load_dotenv()
app = Flask(__name__)
CORS(app)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Database setup
def init_db():
    conn = sqlite3.connect('chats.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chats
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  prompt TEXT NOT NULL,
                  response TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

@app.route('/api/chat', methods=['POST'])
def chat():
    if not request.json or 'prompt' not in request.json:
        abort(400, description="Missing 'prompt' in request")
    
    try:
        # Get response from Gemini
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(request.json['prompt'])
        
        # Store in database
        conn = sqlite3.connect('chats.db')
        c = conn.cursor()
        c.execute("INSERT INTO chats (prompt, response) VALUES (?, ?)",
                 (request.json['prompt'], response.text))
        conn.commit()
        conn.close()
        
        return jsonify({
            "response": response.text,
            "chat_id": c.lastrowid
        })
        
    except Exception as e:
        app.logger.error(f"Error in Gemini API: {str(e)}")
        abort(500, description="Failed to process request")

@app.route('/api/history', methods=['GET'])
def get_history():
    conn = sqlite3.connect('chats.db')
    c = conn.cursor()
    c.execute("SELECT * FROM chats ORDER BY created_at DESC LIMIT 50")
    history = [{"id": row[0], "prompt": row[1], "response": row[2], "timestamp": row[3]} 
               for row in c.fetchall()]
    conn.close()
    return jsonify(history)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080)
