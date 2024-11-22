
from flask import Flask, render_template, request

app = Flask(__name__)


import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import re
import json
from groq import Groq
import time
import csv
import psycopg2

def get_db_connection():
    # Connect to your PostgreSQL database
    conn = psycopg2.connect(
        dbname="my_text_db",
        user="postgres",
        password="1234",
        host="localhost",  # Or the IP address of your PostgreSQL server
        port="5432"        # Default port for PostgreSQL
    )
    return conn

def get_top_answer(query, model, conn, top_k=10):
    # Generate embedding for the input query
    query_embedding = model.encode(query, convert_to_tensor=False)
    query_embedding = np.array(query_embedding, dtype='float32')

    # Convert query_embedding to string format suitable for PostgreSQL
    embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'

    cursor = conn.cursor()

    # Perform similarity search using pgvector's <=> operator for cosine similarity
    cursor.execute("""
    SELECT id, question, answer, embedding
    FROM questions
    ORDER BY embedding <=> %s
    LIMIT %s
    """, (embedding_str, top_k))

    rows = cursor.fetchall()

    retrieved_docs = []
    for row in rows:
        retrieved_docs.append(row[2])  # Answer column

    cursor.close()

    return retrieved_docs

grok_api_key = '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'

def GroqChat(question):
    client = Groq(
        api_key=grok_api_key,

    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": question,
            }
        ],
            model = "llama-3.1-70b-versatile"
    )

    cleaned_json_string = chat_completion.choices[0].message.content

    json_str = re.sub(r'}\s*{', '}, {', cleaned_json_string)
    return json_str

def generate_answer_from_docs(query, retrieved_docs):
    result = []
    if not retrieved_docs:
        return "Don't have an answer for the query."

    context = "\n".join(retrieved_docs)
    result.append(context)

    # prompt = f"Answer the following query, based only on the given context. Do not add anything from your previous learnings. Do not state in answer that a context is provided to you. If the context seems irrelevant just say 'I don't have an appropriate answer'. query: {query} context: {context}"
    prompt = f"Answer the following query based solely on the provided context. Do not include information from outside the context, and do not mention that a context is provided. If the context does not address the query, respond with 'We're currently in the process of collecting data to provide a comprehensive answer. Thank you for your patience as we work on this. ' If the query includes greetings like 'Good morning' or 'Good evening', respond accordingly. Query: {query} Context: {context}"

    groq_answer = GroqChat(prompt)
    result.append(groq_answer)
    result.append('')
    return result

app = Flask(__name__)

# Load model once during the server startup
model = SentenceTransformer('all-MiniLM-L6-v2')
messages = []  # Initialize global message list

@app.route('/', methods=['GET', 'POST'])
def index():
    global messages

    if request.method == 'POST':
        # Check if the reset button was clicked
        if request.form.get('reset'):
            messages = []  # Clear the messages
        else:
            user_input = request.form.get('user_input')
            messages.append({'type': 'question', 'text': user_input})


            messages = messages[-20:]  # Limit message history to the last 20

            # Database query processing
            conn = get_db_connection()
            try:
                # Use user_input to retrieve relevant documents
                retrieved_docs = list(set(get_top_answer(user_input, model, conn)))
                # Generate a response based on retrieved documents
                generated_answer = generate_answer_from_docs(user_input, retrieved_docs)
                
                # Save the response to messages
                messages.append({'type': 'answer', 'text': generated_answer[1]})
            finally:
                conn.close()  # Ensure the database connection is always closed

    return render_template('index.html', messages=messages)

if __name__ == '__main__':
    app.run(debug=True)
