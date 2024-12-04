"""
This script defines a class `VectorizeTheWines` that processes wine-related data from a PostgreSQL database
and utilizes GloVe embeddings for terms found in specific columns of the `wines2` table.
The script performs the following tasks:
1. Loads GloVe embeddings from a file.
2. Extracts unique terms from the `type`, `variety`, `region`, `topnote`, and `bottomnote` columns.
3. Matches these terms with GloVe embeddings and stores them in the database.
4. Creates a new table (`combined_embeddings`) that references the `wines2` table and stores
   a combined vector for each wine entry, computed as the average of its embedded terms.
5. Prints terms not found in the GloVe embeddings and logs execution time.
"""

import psycopg2
import numpy as np
from db_config import db_config
import time


class VectorizeTheWines:
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
            query = """SELECT id, type, variety, region, topnote, bottomnote FROM wines2;"""
            cursor.execute(query)
            self.wines = cursor.fetchall()
            for row in self.wines:
                _, type_, variety, region, top_note, bottom_note = row
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
            cursor.execute("DROP TABLE IF EXISTS token_embeddings;")
            cursor.execute("""
                CREATE TABLE token_embeddings (
                    token TEXT PRIMARY KEY,
                    vector DOUBLE PRECISION[]
                );
            """)
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

    def save_combined_vectors_to_db(self):
        try:
            connection = psycopg2.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute("DROP TABLE IF EXISTS combined_embeddings;")
            cursor.execute("""
                CREATE TABLE combined_embeddings (
                    wine_id INT PRIMARY KEY REFERENCES wines2(id) ON DELETE CASCADE,
                    combined_vector DOUBLE PRECISION[]
                );
            """)
            for row in self.wines:
                wine_id, type_, variety, region, top_note, bottom_note = row
                combined_vector = np.zeros(50)
                term_count = 0
                for term in [type_, variety, region, top_note, bottom_note]:
                    vector = self.word_embeddings.get(term.lower())
                    if vector is not None:
                        combined_vector += vector
                        term_count += 1
                if term_count > 0:
                    combined_vector /= term_count
                    cursor.execute("""
                        INSERT INTO combined_embeddings (wine_id, combined_vector)
                        VALUES (%s, %s);
                    """, (wine_id, combined_vector.tolist()))
            connection.commit()
            print("Combined vectors saved to the database successfully.")
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
    vtw = VectorizeTheWines()
    vtw.get_wines()
    vtw.save_embeddings_to_db()     
    vtw.save_combined_vectors_to_db()
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Execution time: {elapsed_time:.2f} seconds")
