import logging
import json
import re
import subprocess
import os
import shutil as sh
import concurrent.futures
import yt_dlp
import sys
import random
import time
import requests
from datetime import timedelta
import pyperclip

logger = logging.getLogger(__name__)  

def log(message):
    print(message)
    logger.info(message)

def run_concurrent_tasks(task_function, items):
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(task_function, item) for item in items]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
    return results

class YoutubeDLHelper:
    ydl = None
    path = ''
    type = ''
    platform = ''
    save_directory = ''
    
    def __init__(self, url: str = '') -> None:
        self.url = url
        self.downloaded = []
        if url:
            self.extract_info(url)
    
    def extract_info(self, url: str) -> list[dict]:
        info = []
        platform, type = self.identify_url_components(url)
        if platform in ['youtube', 'soundcloud']:
            command = [
                'yt-dlp',
                '--skip-download',
                '--print-json',
                url
            ]
            
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for line in process.stdout:
                strip = line.strip()
                if strip:
                    info.append(json.loads(strip))
            errors = process.stderr.read()
            if errors:
                raise RuntimeError(f"Error extracting metadata: {errors} for URL: {url}")

            output, errors = process.communicate()
            process.stdout.close()
            process.stderr.close()
            process.wait()
        else:
            exit(f"Unsupported URL: {url}")
        if platform in ['youtube', 'soundcloud']:
            name = info[0]['playlist_title'] if type == 'playlist' else info[0]['title']
            uploader = info[0]['uploader'] if platform == 'youtube' else url.split("/")[3]

        self.path = os.path.join("/media", platform, uploader, name)
        self.platform = platform
        self.url = url
        self.type = type
        self.info = info
        return info

    def identify_url_components(self, url: str) -> tuple[str, str]:
        url_patterns = [
            ('soundcloud', 'artist', r'soundcloud\.com/[^/]+/?$'),
            ('soundcloud', 'track', r'soundcloud\.com/[^/]+/[^/]+$'),
            ('soundcloud', 'playlist', r'soundcloud\.com/[^/]+/sets/'),
            ('youtube', 'track', r'youtube\.com/watch\?v='),
            ('youtube', 'playlist', r'youtube\.com/playlist\?list='),
        ]
        for platform, url_type, pattern in url_patterns:
            if re.search(pattern, url):
                return platform, url_type
        exit(f"Unsupported URL: {url}")

    def create_snippet(self, input, timestamp, output):
        subprocess.call([
            "ffmpeg", "-i", f"{input}.wav", "-ss", timestamp['start'], "-to", timestamp['end'], "-c:a", "pcm_s16le", "-ar", "44100", f"{output}.wav"
        ])
        print(f"Snippet created: {output}")

    def process_snippet(self, path, timestamp):
        snippet_output = os.path.join(path.rsplit("/", 1)[0], f"{timestamp['start'].replace(':', '')}_{timestamp['end'].replace(':', '')}")
        self.create_snippet(path, timestamp, snippet_output)
        return f"{snippet_output}.wav"

    def download(self, timestamps: list = None) -> any:
        if os.path.isdir(self.path) and self.type == "playlist":
            sh.rmtree(self.path)

        def process_track(track) -> any:
            save = self.path
            name = track.get('webpage_url_basename') or track.get('title') or "unknown"
            url = track.get('webpage_url') or track.get('url')

            if self.type == "playlist":
                save = os.path.join(save, name)
            elif timestamps:
                os.makedirs(save, exist_ok=True)
                save = os.path.join(save, track.get('title', name))

            download_cmd = [
                'yt-dlp',
                '--format', 'bestaudio/best',
                '--extract-audio',
                '--audio-format', 'wav',
                '--audio-quality', '0',
                '-o', save, url
            ]
            download = subprocess.Popen(download_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, errors = download.communicate()
            if download.returncode == 0:
                if timestamps:
                    self.downloaded.extend(run_concurrent_tasks(lambda t: self.process_snippet(save, t), timestamps))
                return f"{save}.wav"
            else:
                print(f"Error downloading {name}: {errors.decode() if errors else errors}")
                return None

        tracks = self.info
        self.downloaded.extend(run_concurrent_tasks(process_track, tracks))
        return self.downloaded
        
    def scrape_artist(self, url: str) -> dict:
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8,de;q=0.7,fa;q=0.6',
            'Authorization': 'OAuth 2-299981-66593390-Ay501VJFG3ly13T',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Origin': 'https://soundcloud.com',
            'Referer': 'https://soundcloud.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'x-datadome-clientid': 'RoGdTydBuUNBdENCtEGX2aV2HS8302OMO14gkG~Bvj1b2MXqQ4GXP1v5~Rwyix8wef356kcKGmVhdvanWzNSqPDdoOHDikrjim~TmpwLW4kR4zQv35weEPI7goGTCTps',
        }
        params = {
            'client_id': 'pBOtnFXSovQGu3Xby3dIdgbSXj1EgVS0',
            'limit': '10',
            'offset': '0',
            'linked_partitioning': '1',
            'app_version': '1756910035',
            'app_locale': 'en',
        }
        urls = []
        with yt_dlp.YoutubeDL({}) as ydl:
            try:
                info = ydl.extract_info(url, download=False, process=False)
                urls = [entry['url'] for entry in info.get('entries')]
                user_id = str(info.get('id'))
            except Exception as e:
                print(f"Failed to get info for {url}: {e}")
                return {}
        # 'tracks', 'toptracks', 'albums', 'reposts', 'playlists_without_albums'
        endpoints = ['playlists_without_albums']
        for i, endpoint in enumerate(endpoints):
            try:
                response = requests.get(f'https://api-v2.soundcloud.com/users/{user_id}/{endpoint}', params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
                for entry in data.get('collection', []):
                    urls.append(entry['permalink_url'])
                urls = list(set(urls))
                if i > 0 and i < len(endpoints) - 1:
                    time.sleep(random.uniform(5, 10))
            except Exception as e:
                print(f"Failed to get {endpoint} for user {user_id}: {e}")
        return urls
                
