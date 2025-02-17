import os
import requests
import sys
import shutil
import time
import argparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote, quote
from concurrent.futures import ThreadPoolExecutor

# -- Download with Retries
def download_with_retries(url, save_folder, headers, filename, retries=3):
    for attempt in range(retries):
        try:
            with requests.get(url, headers=headers, stream=True, timeout=20) as r:
                if r.status_code == 403:
                    print(f"Access forbidden for {url}. Skipping...")
                    return False
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                downloaded = 0
                with open(filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            sys.stdout.write(f"\rDownloading {os.path.basename(filename)}: {percent:.2f}% "
                                             f"({shutil.disk_usage(save_folder).free / (1024 * 1024):.2f} MB free)   ")
                            sys.stdout.flush()
            print(f"\nSaved to {filename}\n")
            return True  # Success!
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2)  # Backoff a little before retrying
    print(f"Giving up on {url} after {retries} attempts.")
    return False

# -- Fetch the Video Links, current mp4
def fetch_video_links(base_url, headers):
    try:
        response = requests.get(base_url, headers=headers, allow_redirects=True, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error accessing {base_url}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    links = [
        urljoin(base_url + "/", quote(unquote(a['href'])))
        for a in soup.find_all('a', href=True) if a['href'].endswith('.mp4')
    ]

    if not links:
        print("No MP4 files found.")

    return links

# -- Main function to download videos, default threads is 1
def download_archive_videos(base_url, save_folder, num_threads=1):
    os.makedirs(save_folder, exist_ok=True)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": base_url
    }

    print(f"Fetching video links from {base_url}...\n")
    links = fetch_video_links(base_url, headers)

    if not links:
        return

    print(f"Found {len(links)} video(s). Downloading...\n")

    def download_video(link):
        """Wrapper function for parallel downloads."""
        filename = os.path.join(save_folder, os.path.basename(unquote(link)))
        if os.path.exists(filename):
            print(f"Skipping {filename}, already downloaded.")
            return
        print(f"Downloading {link}...")
        download_with_retries(link, save_folder, headers, filename)

    if num_threads > 1:
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            executor.map(download_video, links)
    else:
        for link in links:
            download_video(link)

    print("All downloads complete!")

# -- Main for Load In
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download all MP4 videos from an archive source.")
    parser.add_argument("-u", "--url", required=True, help="Base URL of the archive page")
    parser.add_argument("-f", "--folder", required=True, help="Folder to save downloaded files")
    parser.add_argument("-t", "--threads", type=int, default=1, help="Number of concurrent downloads (default: 1)")

    args = parser.parse_args()
    download_archive_videos(args.url, args.folder, args.threads)
