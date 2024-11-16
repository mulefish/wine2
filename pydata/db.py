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
