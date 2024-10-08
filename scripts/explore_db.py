import sqlite3
import json


# function to dump all table names in the database
def list_tables(database_path):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Query to list all tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()

    # Print table names
    print("Tables in the database:")
    for table in tables:
        print(table[0])


list_tables('../world_sql_content_ac48f64bc0716275b9e258b508fb30f8.content')
