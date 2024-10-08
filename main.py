import requests, zipfile, os, pickle, json, sqlite3, re
import pyttsx3  # Import the pyttsx3 library for text-to-speech

API_KEY = '2d25521978b3434bb1ed46c9d4a84592'
HEADERS = {'X-API-Key': API_KEY}
MANIFEST_URL = 'https://www.bungie.net/Platform/Destiny2/Manifest/'
VERSION_FILE = 'manifest_version.txt'


# Fetch the manifest from Bungie API
def get_manifest():
    r = requests.get(MANIFEST_URL, headers=HEADERS)
    manifest = r.json()
    return manifest


# Extract the SQLite database file from the downloaded zip
def download_manifest_zip(url, save_path):
    r = requests.get(f"https://www.bungie.net{url}", stream=True)
    with open(save_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=128):
            f.write(chunk)
    with zipfile.ZipFile(save_path, 'r') as zip_ref:
        zip_ref.extractall(os.path.dirname(save_path))


# Check if we already have the latest manifest version
def check_manifest_version(current_version):
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, 'r') as f:
            stored_version = f.read().strip()
        if stored_version == current_version:
            print("Manifest is up to date.")
            return True
    return False


# Save the latest manifest version locally
def save_manifest_version(version):
    with open(VERSION_FILE, 'w') as f:
        f.write(version)


# Query the SQLite database to extract all lore entries
def get_lore_entries(database_path):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Querying the "DestinyLoreDefinition" table for lore
    query = "SELECT json from DestinyLoreDefinition"
    cursor.execute(query)

    lore_entries = [json.loads(row[0]) for row in cursor.fetchall()]
    conn.close()

    return lore_entries


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


# Save the lore entries to a JSON file
def save_lore_to_json(lore_entries, filename='lore_entries.json'):
    with open(filename, 'w') as f:
        json.dump(lore_entries, f, indent=4)


# Search the lore entries for the given keyword and rank by frequency
def search_lore_entries(lore_entries, keyword):
    keyword = keyword.lower()  # Convert keyword to lowercase for case-insensitive search
    results = []

    for entry in lore_entries:
        title = entry.get('displayProperties', {}).get('name', 'No Title')
        description = entry.get('displayProperties', {}).get('description', '').lower()

        # Count occurrences of the keyword in the description
        occurrences = len(re.findall(keyword, description))

        # Count words in the description
        word_count = len(description.split())

        if occurrences > 0:
            results.append((title, description, occurrences, word_count))

    # Sort results by occurrences in descending order
    results.sort(key=lambda x: x[2], reverse=True)

    return results


# Convert the selected lore entry to audio using pyttsx3
def convert_to_audio(text, title, output_file):
    engine = pyttsx3.init()

    # Set properties to make the voice more natural
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  # Change the voice, index 1 is typically female
    engine.setProperty('rate', 150)  # Speed of speech
    engine.setProperty('volume', 1)  # Volume level (0.0 to 1.0)

    audio_file = f"{output_file}.mp3"

    # Save the audio to an output file
    engine.save_to_file(text, audio_file)
    engine.runAndWait()

    print(f"Audio saved as {audio_file}")


def main():
    # Step 1: Get manifest data from Bungie API
    manifest_data = get_manifest()

    if 'Response' in manifest_data:
        current_version = manifest_data['Response']['version']

        # Step 2: Check if we already have the latest manifest
        if not check_manifest_version(current_version):
            # Step 3: Get the manifest download URL
            manifest_url = manifest_data['Response']['mobileWorldContentPaths']['en']

            # Step 4: Download and extract the manifest database
            db_zip_path = 'manifest.zip'
            download_manifest_zip(manifest_url, db_zip_path)



        # Step 5: List all tables to find the correct one (already found DestinyLoreDefinition)
        # list_tables('world_sql_content_ac48f64bc0716275b9e258b508fb30f8.content')

        # Step 6: Query the DestinyLoreDefinition table for lore
        lore_entries = get_lore_entries('world_sql_content_ac48f64bc0716275b9e258b508fb30f8.content')

        # Step 7: Save lore entries to a JSON file
        save_lore_to_json(lore_entries)

        # Step 8: Save the current manifest version locally
        save_manifest_version(current_version)

        # Step 9: Ask the user for a keyword to search
        keyword = input("Enter a keyword to search for in the lore entries: ")

        # Step 10: Search for the keyword in the lore entries
        search_results = search_lore_entries(lore_entries, keyword)

        # Step 11: Print the search results ranked by frequency, word count, and number them
        print(f"Lore entries containing '{keyword}':")
        for i, (title, description, count, word_count) in enumerate(search_results, 1):
            print(f"{i}. {title}: {count} occurrence(s), {word_count} words")

        # Step 12: Ask the user for the ID of the article to convert
        article_id = int(input("Enter the ID of the article to convert to audio: ")) - 1
        if 0 <= article_id < len(search_results):
            selected_title, selected_description, _, _ = search_results[article_id]

            # Step 13: Convert the selected lore entry to audio using pyttsx3
            output_file = selected_title.replace(" ", "_").lower()
            convert_to_audio(selected_description, selected_title, output_file)
        else:
            print("Invalid ID.")


if __name__ == '__main__':
    main()
