from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from db import get_all_wines, get_unique_wines_data, calculate_vector_from_json, find_closest_wines

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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
        wines = get_all_wines()
        return jsonify(wines), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/unique-wines', methods=['GET'])
def unique_wines():
    try:
        unique_data = get_unique_wines_data()
        return jsonify(unique_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_closest_wines', methods=['POST'])
def get_closest_wines():
    try:
        opinions = request.get_json()
        if not opinions:    
            return jsonify({"error": "Invalid JSON payload"}), 400

        vector = calculate_vector_from_json(opinions)
        found_wines = find_closest_wines(vector, 20)

        # Return the results as JSON
        return jsonify({"status": "success", "data": found_wines}), 200

    except Exception as e:
        # Handle unexpected errors
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
