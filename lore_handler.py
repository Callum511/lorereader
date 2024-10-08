import sqlite3
import json
import re


# Query the SQLite database for lore entries
def get_lore_entries(database_path):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    query = "SELECT json FROM DestinyLoreDefinition"
    cursor.execute(query)
    lore_entries = [json.loads(row[0]) for row in cursor.fetchall()]
    conn.close()
    return lore_entries


# Search lore entries for the given keyword and return results
def search_lore_entries(lore_entries, keyword):
    keyword = keyword.lower()
    results = []

    for entry in lore_entries:
        title = entry.get('displayProperties', {}).get('name', 'No Title')
        description = entry.get('displayProperties', {}).get('description', '').lower()
        occurrences = len(re.findall(keyword, description))
        word_count = len(description.split())

        if occurrences > 0:
            results.append((title, description, occurrences, word_count))

    results.sort(key=lambda x: x[2], reverse=True)
    return results
