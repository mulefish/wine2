import psycopg2
from db_config import db_config


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


wines2_getAllUniqueTerms_and_check_embeddings()
