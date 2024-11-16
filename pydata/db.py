# {
#   "A": {
#     "bottomnote": "herbaceous",
#     "region": "rioja",
#     "topnote": "intense",
#     "variety": "cabernet"
#   },
#   "B": {
#     "bottomnote": "aromatic",
#     "region": "mosel",
#     "topnote": "rich",
#     "variety": "chardonnay"
#   }
# }
import psycopg2
from db_config import db_config
import numpy as np
from scipy.spatial.distance import cosine

def find_closest_wines(vector, top_n=5):
    """
    Find the closest wines to the given vector using cosine similarity.

    Args:
        vector (list): The input vector to compare.
        top_n (int): Number of closest wines to return.

    Returns:
        list: A list of dictionaries containing the wine ID and similarity score.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Fetch all wine IDs and their combined vectors
        cursor.execute("SELECT wine_id, combined_vector FROM combined_embeddings;")
        wines = cursor.fetchall()

        # Calculate similarity for each wine
        similarities = []
        for wine_id, wine_vector in wines:
            similarity = 1 - cosine(vector, wine_vector)  # Cosine similarity (higher is closer)
            similarities.append({"wine_id": wine_id, "similarity": similarity})

        # Sort by similarity in descending order and get the top N
        closest_wines = sorted(similarities, key=lambda x: x["similarity"], reverse=True)[:top_n]
        return closest_wines
    except Exception as e:
        print(f"Error finding closest wines: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def get_db_connection():
    """Establish and return a new database connection."""
    return psycopg2.connect(**db_config)

def get_all_wines():
    """Retrieve all rows from the wines2 table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM wines2")
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        wines = [dict(zip(column_names, row)) for row in rows]
    finally:
        cursor.close()
        conn.close()
    return wines

def get_unique_wines_data():
    """Retrieve unique values for variety, region, topnote, and bottomnote."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
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
            bottomnote_set.add(row[3])
        result = {
            "variety": list(variety_set),
            "region": list(region_set),
            "topnote": list(topnote_set),
            "bottomnote": list(bottomnote_set),
        }
    finally:
        cursor.close()
        conn.close()
    return result

def calculate_vector_from_json(data):
    """
    Calculate a combined vector based on values from the provided JSON.
    
    Args:
        data (dict): A JSON object with terms as values (keys are irrelevant).
        
    Returns:
        list: A combined vector (sum of vectors for the given values) or None if no vectors are found.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        combined_vector = None
        
        for value in data.values():
            if value:
                # Query the vector for the current value
                cursor.execute("SELECT vector FROM token_embeddings WHERE token = %s", (value.lower(),))
                result = cursor.fetchone()
                if result:
                    vector = result[0]
                    if combined_vector is None:
                        combined_vector = vector
                    else:
                        combined_vector = [x + y for x, y in zip(combined_vector, vector)]
        
        return combined_vector
    finally:
        cursor.close()
        conn.close()
