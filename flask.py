# app.py
from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
import json
from datetime import datetime
import os

app = Flask(__name__)

# Database initialization
def init_db():
    conn = sqlite3.connect('icu_education.db')
    c = conn.cursor()
    
    # Create tables if they don't exist
    c.execute('''CREATE TABLE IF NOT EXISTS research_articles
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, author TEXT, 
                 publish_date TEXT, abstract TEXT, content TEXT, pdf_path TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS guidelines
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, organization TEXT, 
                 category TEXT, publish_date TEXT, content TEXT, file_path TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS quiz_questions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT, option1 TEXT, 
                 option2 TEXT, option3 TEXT, option4 TEXT, correct_option INTEGER)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS user_interactions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, page TEXT, action TEXT, 
                 timestamp TEXT, additional_data TEXT)''')
    
    # Insert sample data if tables are empty
    c.execute("SELECT COUNT(*) FROM research_articles")
    if c.fetchone()[0] == 0:
        sample_research = [
            ("Sedation Protocols in Mechanically Ventilated Patients", "Dr. James Wilson", 
             "2023-08-15", "Comparative study of sedation protocols...", "Full content here", "/pdfs/sedation.pdf"),
            ("Early Mobilization in ICU: Effects on Patient Outcomes", "Dr. Sarah Johnson", 
             "2023-07-28", "Randomized controlled trial demonstrating...", "Full content here", "/pdfs/mobilization.pdf")
        ]
        c.executemany("INSERT INTO research_articles (title, author, publish_date, abstract, content, pdf_path) VALUES (?, ?, ?, ?, ?, ?)", 
                     sample_research)
    
    c.execute("SELECT COUNT(*) FROM quiz_questions")
    if c.fetchone()[0] == 0:
        sample_questions = [
            ("Which of the following is the first-line vasopressor for septic shock?", 
             "Norepinephrine", "Dopamine", "Epinephrine", "Vasopressin", 1),
            ("What is the recommended head-of-bed elevation for mechanically ventilated patients to prevent VAP?", 
             "15-20 degrees", "30-45 degrees", "0-10 degrees", "45-60 degrees", 2)
        ]
        c.executemany("INSERT INTO quiz_questions (question, option1, option2, option3, option4, correct_option) VALUES (?, ?, ?, ?, ?, ?)", 
                     sample_questions)
    
    conn.commit()
    conn.close()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/research')
def get_research_articles():
    conn = sqlite3.connect('icu_education.db')
    c = conn.cursor()
    c.execute("SELECT * FROM research_articles ORDER BY publish_date DESC")
    articles = []
    for row in c.fetchall():
        articles.append({
            'id': row[0],
            'title': row[1],
            'author': row[2],
            'publish_date': row[3],
            'abstract': row[4],
            'content': row[5],
            'pdf_path': row[6]
        })
    conn.close()
    return jsonify(articles)

@app.route('/api/guidelines')
def get_guidelines():
    category = request.args.get('category', '')
    conn = sqlite3.connect('icu_education.db')
    c = conn.cursor()
    
    if category:
        c.execute("SELECT * FROM guidelines WHERE category = ? ORDER BY publish_date DESC", (category,))
    else:
        c.execute("SELECT * FROM guidelines ORDER BY publish_date DESC")
    
    guidelines = []
    for row in c.fetchall():
        guidelines.append({
            'id': row[0],
            'title': row[1],
            'organization': row[2],
            'category': row[3],
            'publish_date': row[4],
            'content': row[5],
            'file_path': row[6]
        })
    conn.close()
    return jsonify(guidelines)

@app.route('/api/quiz')
def get_quiz_questions():
    conn = sqlite3.connect('icu_education.db')
    c = conn.cursor()
    c.execute("SELECT * FROM quiz_questions")
    questions = []
    for row in c.fetchall():
        questions.append({
            'id': row[0],
            'question': row[1],
            'options': [row[2], row[3], row[4], row[5]],
            'correct_option': row[6]
        })
    conn.close()
    return jsonify(questions)

@app.route('/api/track-interaction', methods=['POST'])
def track_interaction():
    data = request.json
    page = data.get('page', '')
    action = data.get('action', '')
    additional_data = json.dumps(data.get('additional_data', {}))
    
    conn = sqlite3.connect('icu_education.db')
    c = conn.cursor()
    c.execute("INSERT INTO user_interactions (page, action, timestamp, additional_data) VALUES (?, ?, ?, ?)",
              (page, action, datetime.now().isoformat(), additional_data))
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success'})

@app.route('/pdfs/<path:filename>')
def serve_pdf(filename):
    return send_file(f'static/pdfs/{filename}', as_attachment=False)

# Additional API endpoints for other sections can be added here

if __name__ == '__main__':
    init_db()
    app.run(debug=True)