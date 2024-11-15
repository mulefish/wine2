"""
Wine API
========
This API provides access to the wines2 database. It offers the following endpoints:

1. GET /: A simple HTML page listing available endpoints.
2. GET /wines: Retrieve all rows from the wines table.
3. GET /unique-wines: Retrieve unique values from the variety, region, and topnote columns.

CORS is enabled to allow this API to be used with a React frontend.
"""

from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
import psycopg2
from db_config import db_config

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def get_db_connection():
    conn = psycopg2.connect(**db_config)
    return conn

@app.route('/')
def home():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Available Endpoints</title>
    </head>
    <body>
        <h1>Welcome to the Wine API</h1>
        <p>Below are the available endpoints:</p>
        <ul>
            <li><a href="/wines"><strong>GET /wines</strong></a>: Retrieve all rows from the wines table.</li>
            <li><a href="/unique-wines"><strong>GET /unique-wines</strong></a>: Retrieve unique values from the variety, region, and topnote columns.</li>
            <li><strong>GET /</strong>: Show this page with a list of endpoints.</li>
        </ul>
    </body>     
    </html>
    """
    return render_template_string(html_content)

@app.route('/wines', methods=['GET'])
def get_wines():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM wines2")
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        wines = [dict(zip(column_names, row)) for row in rows]
        cursor.close()
        conn.close()
        return jsonify(wines), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/unique-wines', methods=['GET'])
def get_unique_wines():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
        SELECT DISTINCT variety, region, topnote, bottomnote
        FROM wines2
        """
        cursor.execute(query)
        variety_set = set()
        region_set = set()
        topnote_set = set()
        bottomnote_set = set()

        for row in cursor.fetchall():
            variety_set.add(row[0])
            region_set.add(row[1])
            topnote_set.add(row[2])
            bottomnote_set.add(row[2])
        result = {
            "variety": list(variety_set),
            "region": list(region_set),
            "topnote": list(topnote_set),
            "bottomnote": list(bottomnote_set),
        }
        cursor.close()
        conn.close()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
