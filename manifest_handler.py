import os
import requests, zipfile

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
