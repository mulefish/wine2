"""
This script generates synthetic data for wines, including their attributes such as type, region, variety,
year, price, top notes, and bottom notes. Wine names are generated to sound more realistic and reflect a
combination of region, variety, and descriptive elements.
It drops the PostgreSQL database table 'wines2' if it exists and then creates a new one.
The script inserts the generated data into the table and ensures no duplicate entries.
"""

import random
import pandas as pd
import psycopg2
from db_config import db_config

wine_types = ['red', 'white', 'rose', 'sparkling', 'dessert', 'fortified']
regions = {
    'bordeaux': ['rich', 'bold', 'earthy'],
    'napa': ['woody', 'dark', 'robust'],
    'tuscany': ['herbaceous', 'spicy', 'smooth'],
    'rioja': ['oak', 'vanilla', 'leathery'],
    'barossa': ['spicy', 'intense', 'smoky'],
    'champagne': ['bubbly', 'citrus', 'light'],
    'mosel': ['sweet', 'floral', 'fruity'],
    'mendoza': ['ripe', 'plummy', 'bold'],
    'sonoma': ['fruity', 'complex', 'aromatic']
}
varieties = ['cabernet', 'sauvignon', 'pinot', 'chardonnay', 'merlot', 'blanc', 'syrah', 'malbec', 'zinfandel', 'riesling']

# Helper function to generate wine names
def generate_wine_name(region, variety, descriptor):
    """
    Generate a wine name using the region, variety, and a descriptor.
    Example: "Napa Bold Cabernet" or "Tuscany Smooth Syrah".
    """
    return f"{region.capitalize()} {descriptor.capitalize()} {variety.capitalize()}"

N = 100
wines = []
for i in range(N):
    wine_type = random.choice(wine_types)
    region = random.choice(list(regions.keys()))
    variety = random.choice(varieties)
    topnote, bottomnote = random.sample(regions[region], 2)
    descriptor = random.choice([topnote, bottomnote])
    wine_name = generate_wine_name(region, variety, descriptor)
    wine = {
        "ID": i + 1,
        "Name": wine_name,
        "Type": wine_type,
        "Variety": variety,
        "Year": random.randint(1980, 2023),
        "Region": region,
        "Price": random.randint(10, 300),
        "Topnote": topnote,
        "Bottomnote": bottomnote
    }
    wines.append(wine)

df_wines = pd.DataFrame(wines)

try:
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS wines2 CASCADE;")
    
    create_table_query = """
    CREATE TABLE wines2 (
        id INT PRIMARY KEY,
        name VARCHAR(100),
        type VARCHAR(50),
        variety VARCHAR(50),
        year INT,
        region VARCHAR(50),
        price INT,
        topnote VARCHAR(50),
        bottomnote VARCHAR(50)
    );
    """
    cursor.execute(create_table_query)
    
    for index, row in df_wines.iterrows():
        query = """
        INSERT INTO wines2 (id, name, type, variety, year, region, price, topnote, bottomnote)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING;
        """
        values = (
            row['ID'], row['Name'], row['Type'], row['Variety'], row['Year'],
            row['Region'], row['Price'], row['Topnote'], row['Bottomnote']
        )
        cursor.execute(query, values)
    
    conn.commit()
    print("The end! Table dropped, recreated, and data inserted successfully!")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
