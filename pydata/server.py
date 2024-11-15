from flask import Flask, jsonify
import psycopg2
from db_config import db_config

app = Flask(__name__)

def get_db_connection():
    """Create a connection to the PostgreSQL database."""
    conn = psycopg2.connect(**db_config)
    return conn

@app.route('/wines', methods=['GET'])
def get_wines():
    """Endpoint to get all terms (rows) from the wines table."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute query
        cursor.execute("SELECT * FROM wines2")

        # Fetch all rows
        rows = cursor.fetchall()

        # Get column names from cursor description
        column_names = [desc[0] for desc in cursor.description]

        # Convert rows to a list of dictionaries
        wines = [dict(zip(column_names, row)) for row in rows]

        # Close the connection
        cursor.close()
        conn.close()

        return jsonify(wines), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
