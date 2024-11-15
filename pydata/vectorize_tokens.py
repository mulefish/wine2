"""
This script defines a class `XYZ` that processes wine-related data and extracts GloVe embeddings 
for terms found in specific columns of the `wines2` table in a PostgreSQL database. 
It drops the 'token_embeddings' table if it exists, recreates it, and saves the embeddings into the database.
The script also prints out terms that are not found in the GloVe embeddings.
"""

import psycopg2
import numpy as np
from db_config import db_config
import time


class XYZ:
    def __init__(self):
        self.PATH = r"C:\\Users\\squar\\jars\\glove.6B\\glove.6B.50d.txt"
        self.wines = []
        self.type_set = set()
        self.variety_set = set()
        self.region_set = set()
        self.top_note_set = set()
        self.bottom_note_set = set()
        self.word_embeddings = {}
        self.selected_embeddings = {}
        self.missing_terms = []
        self.load_glove_model(self.PATH)

    def get_wines(self):
        try:
            connection = psycopg2.connect(**db_config)
            cursor = connection.cursor()
            query = """SELECT type, variety, region, topnote, bottomnote FROM wines2;"""
            cursor.execute(query)

            for row in cursor.fetchall():
                type_, variety, region, top_note, bottom_note = row
                self.type_set.add(type_)
                self.variety_set.add(variety)
                self.region_set.add(region)
                self.top_note_set.add(top_note)
                self.bottom_note_set.add(bottom_note)

            self.extract_selected_embeddings()

        except psycopg2.Error as e:
            print(f"Database error: {e}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()

    def load_glove_model(self, glove_file_path):
        try:
            with open(glove_file_path, "r", encoding="utf-8") as f:
                for line in f:
                    values = line.split()
                    word = values[0]
                    vector = np.array(values[1:], dtype=float)
                    self.word_embeddings[word] = vector
        except IOError as e:
            print(f"Error reading GloVe file: {e}")

    def extract_selected_embeddings(self):
        unique_terms = (
            self.type_set
            | self.variety_set
            | self.region_set
            | self.top_note_set
            | self.bottom_note_set
        )
        for term in unique_terms:
            vector = self.word_embeddings.get(term.lower())
            if vector is not None:
                self.selected_embeddings[term] = vector
            else:
                self.missing_terms.append(term)
        if self.missing_terms:
            print("Sad. Not found in GloVe embeddings:")
            for term in self.missing_terms:
                print(f" - {term}")

    def save_embeddings_to_db(self):
        try:
            connection = psycopg2.connect(**db_config)
            cursor = connection.cursor()

            # Drop the table if it exists
            cursor.execute("DROP TABLE IF EXISTS token_embeddings;")
            
            # Create the table
            cursor.execute("""
                CREATE TABLE token_embeddings (
                    token TEXT PRIMARY KEY,
                    vector FLOAT8[]
                );
            """)

            # Insert embeddings
            for token, vector in self.selected_embeddings.items():
                cursor.execute("""
                    INSERT INTO token_embeddings (token, vector)
                    VALUES (%s, %s)
                    ON CONFLICT (token) DO NOTHING;
                """, (token, vector.tolist()))

            connection.commit()
            print("Table dropped, recreated, and embeddings saved to the database successfully.")
        except psycopg2.Error as e:
            print(f"Database error: {e}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()


if __name__ == "__main__":
    start_time = time.time()
    xyz = XYZ()
    xyz.get_wines()
    xyz.save_embeddings_to_db()
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Execution time: {elapsed_time:.2f} seconds")
