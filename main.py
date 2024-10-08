import os
from manifest_handler import get_manifest, check_manifest_version, save_manifest_version, download_manifest_zip
from lore_handler import get_lore_entries, search_lore_entries
from audio_generator import convert_to_audio_bark

def main():
    # Step 1: Fetch manifest data from Bungie API
    manifest_data = get_manifest()

    if 'Response' in manifest_data:
        current_version = manifest_data['Response']['version']

        # Step 2: Check if the manifest is already up-to-date
        if not check_manifest_version(current_version):
            manifest_url = manifest_data['Response']['mobileWorldContentPaths']['en']

            # Step 3: Download and extract the manifest database
            db_zip_path = 'manifest.zip'
            download_manifest_zip(manifest_url, db_zip_path)

        # Step 4: Query the DestinyLoreDefinition table for lore#
        # find the .content file
        for file in os.listdir():
            if file.endswith('.content'):
                content_file = file
                break
        lore_entries = get_lore_entries(content_file)

        # Step 5: Save the current manifest version
        save_manifest_version(current_version)

        # Step 6: Ask for a keyword to search the lore entries
        keyword = input("Enter a keyword to search for in the lore entries: ")

        # Step 7: Search for the keyword in the lore entries
        search_results = search_lore_entries(lore_entries, keyword)

        # Step 8: Display search results
        print(f"Lore entries containing '{keyword}':")
        for i, (title, description, count, word_count) in enumerate(search_results, 1):
            print(f"{i}. {title}: {count} occurrence(s), {word_count} words")

        # Step 9: Ask for the ID of the article to convert to audio
        article_id = int(input("Enter the ID of the article to convert to audio: ")) - 1
        if 0 <= article_id < len(search_results):
            selected_title, selected_description, _, _ = search_results[article_id]

            # Step 10: Ask user to choose between large or small models
            model_type = input("Enter model type ('large' for high quality or 'small' for faster inference): ").strip().lower()
            if model_type not in ["large", "small"]:
                model_type = "large"  # Default to large model if input is invalid

            # Step 11: Convert the selected lore entry to audio using Bark
            output_file = selected_title.replace(" ", "_").lower()
            convert_to_audio_bark(selected_description, output_file, model_type)
        else:
            print("Invalid ID.")


if __name__ == '__main__':
    main()
