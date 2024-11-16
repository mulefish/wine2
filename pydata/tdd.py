import psycopg2
from db_config import db_config
from db import calculate_vector_from_json, find_closest_wines

def wines2_getAllUniqueTerms_and_check_embeddings():
    # The unique number of dimensions in the wines2 table ought to match the number of embedded words in token_embeddings. 
    # This matters because spaces and capitalization matters - so this is a check to make sure that my lazyness is not 
    # being punished. 
    try:
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()

        query = """SELECT type, variety, region, topnote, bottomnote FROM wines2;"""
        cursor.execute(query)

        type_set = set()
        variety_set = set()
        region_set = set()
        top_note_set = set()
        bottom_note_set = set()

        for row in cursor.fetchall():
            type_, variety, region, top_note, bottom_note = row
            type_set.add(type_)
            variety_set.add(variety)
            region_set.add(region)
            top_note_set.add(top_note)
            bottom_note_set.add(bottom_note)

        uniques = type_set | variety_set | region_set | top_note_set | bottom_note_set
        unique_count = len(uniques)
        print(f"Unique terms count in wines2: {unique_count}")

        query = """SELECT COUNT(*) FROM token_embeddings;"""
        cursor.execute(query)
        embedded_count = cursor.fetchone()[0]
        print(f"Embedded tokens count in token_embeddings: {embedded_count}")

        if unique_count == embedded_count:
            print("PASS The unique count matches the embedded count.")
        else:
            print("FAIL The unique count does NOT match the embedded count.")




    except psycopg2.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def calculate_vector_from_json_test():
    json1 = {
        "key_does_not_matter": "herbaceous"
    }
    json2 = {
        "key_does_not_matter": "cabernet"
    }

    a = calculate_vector_from_json(json1)
    b = calculate_vector_from_json(json2)
    c = calculate_vector_from_json(json1)

    # Check if both vectors are not None
    assert a is not None, "Vector a is None"
    assert b is not None, "Vector b is None"

    # Check if both vectors have the same length
    assert len(a) == len(b), "Vectors a and b have different lengths"

    # Check if the vectors have different values
    assert a != b, "Vectors a and b have the same values"

    # Check if a and c vectors are the same
    assert a == c, "Vectors a and c are different"

    print("PASS: Vectors are valid, same length, and different.")


def find_closest_wines_test():
    json = {
        "key_does_not_matter": "herbaceous"
    }

    vector = calculate_vector_from_json(json)
    found_wines = find_closest_wines(vector)
    print(found_wines)


wines2_getAllUniqueTerms_and_check_embeddings()
calculate_vector_from_json_test()
find_closest_wines_test() 