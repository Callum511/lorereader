import subprocess
import sys
import os
import requests, zipfile, json, sqlite3, re
import torchaudio
from bark import generate_audio, preload_models

API_KEY = '2d25521978b3434bb1ed46c9d4a84592'
HEADERS = {'X-API-Key': API_KEY}
MANIFEST_URL = 'https://www.bungie.net/Platform/Destiny2/Manifest/'
VERSION_FILE = 'manifest_version.txt'


# Fetch the manifest from Bungie API
def get_manifest():
    r = requests.get(MANIFEST_URL, headers=HEADERS)
    return r.json()


# Download and extract the manifest database
def download_manifest_zip(url, save_path):
    r = requests.get(f"https://www.bungie.net{url}", stream=True)
    with open(save_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=128):
            f.write(chunk)
    with zipfile.ZipFile(save_path, 'r') as zip_ref:
        zip_ref.extractall(os.path.dirname(save_path))


# Check if the current manifest is already saved
def check_manifest_version(current_version):
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, 'r') as f:
            stored_version = f.read().strip()
        return stored_version == current_version
    return False


# Save the latest manifest version
def save_manifest_version(version):
    with open(VERSION_FILE, 'w') as f:
        f.write(version)


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


# Convert selected lore entry to audio using Bark
def convert_to_audio_bark(text, output_file):
    # Load Bark models
    preload_models()

    # Generate audio using Bark
    audio_array = generate_audio(text)

    # Save the audio file
    audio_file = f"{output_file}.wav"
    torchaudio.save(audio_file, audio_array, 24000)  # Assuming 24kHz sampling rate
    print(f"Audio saved as {audio_file}")


def main():
    # Step 1: Ensure Bark dependencies are installed
    check_and_install_bark()

    # Step 2: Fetch manifest data from Bungie API
    manifest_data = get_manifest()

    if 'Response' in manifest_data:
        current_version = manifest_data['Response']['version']

        # Step 3: Check if the manifest is already up-to-date
        if not check_manifest_version(current_version):
            manifest_url = manifest_data['Response']['mobileWorldContentPaths']['en']

            # Step 4: Download and extract the manifest database
            db_zip_path = 'manifest.zip'
            download_manifest_zip(manifest_url, db_zip_path)

        # Step 5: Query the DestinyLoreDefinition table for lore
        lore_entries = get_lore_entries('world_sql_content_ac48f64bc0716275b9e258b508fb30f8.content')

        # Step 6: Save the current manifest version
        save_manifest_version(current_version)

        # Step 7: Ask for a keyword to search the lore entries
        keyword = input("Enter a keyword to search for in the lore entries: ")

        # Step 8: Search for the keyword in the lore entries
        search_results = search_lore_entries(lore_entries, keyword)

        # Step 9: Display search results
        print(f"Lore entries containing '{keyword}':")
        for i, (title, description, count, word_count) in enumerate(search_results, 1):
            print(f"{i}. {title}: {count} occurrence(s), {word_count} words")

        # Step 10: Ask for the ID of the article to convert to audio
        article_id = int(input("Enter the ID of the article to convert to audio: ")) - 1
        if 0 <= article_id < len(search_results):
            selected_title, selected_description, _, _ = search_results[article_id]

            # Step 11: Convert the selected lore entry to audio using Bark
            output_file = selected_title.replace(" ", "_").lower()
            convert_to_audio_bark(selected_description, output_file)
        else:
            print("Invalid ID.")


if __name__ == '__main__':
    main()
