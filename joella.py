import requests
import os
import hashlib
from urllib.parse import urlparse
from pathlib import Path

ALLOWED_CONTENT_TYPES = ['image/jpeg', 'image/png', 'image/gif']
MAX_FILE_SIZE_MB = 5
HASHES_FILE = "Fetched_Images/hashes.txt"

def sanitize_filename(filename):
    return "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_')).rstrip()

def get_file_hash(content):
    return hashlib.sha256(content).hexdigest()

def is_duplicate(file_hash):
    if not os.path.exists(HASHES_FILE):
        return False
    with open(HASHES_FILE, 'r') as f:
        return file_hash in f.read().splitlines()

def save_hash(file_hash):
    with open(HASHES_FILE, 'a') as f:
        f.write(file_hash + '\n')

def fetch_image(url):
    try:
        headers = {
            'User-Agent': 'Ubuntu Image Fetcher 1.0'
        }

        response = requests.get(url, headers=headers, stream=True, timeout=10)
        response.raise_for_status()

        # Check content type
        content_type = response.headers.get('Content-Type', '')
        if not any(ct in content_type for ct in ALLOWED_CONTENT_TYPES):
            print(f"✗ Skipping {url} (Invalid content type: {content_type})")
            return

        # Check file size
        content_length = response.headers.get('Content-Length')
        if content_length and int(content_length) > MAX_FILE_SIZE_MB * 1024 * 1024:
            print(f"✗ Skipping {url} (File too large)")
            return

        content = response.content
        file_hash = get_file_hash(content)

        if is_duplicate(file_hash):
            print(f"⚠ Duplicate detected for {url}, skipping.")
            return
        else:
            save_hash(file_hash)

        parsed_url = urlparse(url)
        filename = sanitize_filename(os.path.basename(parsed_url.path)) or "downloaded_image.jpg"
        save_path = os.path.join("Fetched_Images", filename)

        with open(save_path, 'wb') as f:
            f.write(content)

        print(f"✓ Successfully fetched: {filename}")
        print(f"✓ Image saved to {save_path}")

    except requests.exceptions.RequestException as e:
        print(f"✗ Request error: {e}")
    except Exception as e:
        print(f"✗ General error: {e}")

def main():
    print("Welcome to the Ubuntu Image Fetcher")
    print("A tool for mindfully collecting images from the web\n")

    urls = input("Enter image URLs (comma-separated): ").split(',')

    os.makedirs("Fetched_Images", exist_ok=True)

    for url in map(str.strip, urls):
        if url:
            fetch_image(url)

    print("\nConnection strengthened. Community enriched.")

if __name__ == "__main__":
    main()