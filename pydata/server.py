"""
Wine API
========
This API provides access to the wines2 database. It offers the following endpoints:

1. GET /: A simple HTML page listing available endpoints.
2. GET /wines: Retrieve all rows from the wines table.
3. GET /unique-wines: Retrieve unique values from the variety, region, and topnote columns.
"""

from flask import Flask, jsonify, render_template_string
import psycopg2
from db_config import db_config

app = Flask(__name__)

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
            <li><strong>GET /wines</strong>: Retrieve all rows from the wines table.</li>
            <li><strong>GET /unique-wines</strong>: Retrieve unique values from the variety, region, and topnote columns.</li>
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
        SELECT DISTINCT variety, region, topnote
        FROM wines2
        """
        cursor.execute(query)
        variety_set = set()
        region_set = set()
        topnote_set = set()
        for row in cursor.fetchall():
            variety_set.add(row[0])
            region_set.add(row[1])
            topnote_set.add(row[2])
        result = {
            "unique-variety": list(variety_set),
            "unique-region": list(region_set),
            "unique-topnote": list(topnote_set),
        }
        cursor.close()
        conn.close()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
