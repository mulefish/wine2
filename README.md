# wine2
A wine store! Python + React + Word2Vec + Pandas + GloVe : Oh! The buzzwords! So 2024.  

# TODO
1: The DB is postgres localhost. Move to Databricks Cloud! Look at pydata/db_config.py  

# Create data and run the server: 
step0: look in 'cd pydata' and look in db_config.py to make sure connection strings are OK
step1: python create_wines.py   
step2: python vectorize_tokes.py    
step3: python server.py
NOTE: I am using python version 3.12.6 but I doubt that that matters much - nothing tricksy happening here.  

# Postgres notes: 
psql -h localhost -p 5432 -U postgres -d test_db   
\d wines2
\d token_embeddings 
\d combined_embeddings
