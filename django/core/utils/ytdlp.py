import logging
import json
import re
import subprocess
import os
import shutil as sh
import concurrent.futures
from core.utils.utils import SpotifyClient

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
    
    def __init__(self, url) -> None:
        self.url = url
        self.downloaded = []
        self.extract_info(url)
    
    def extract_info(self, url: str) -> list[dict]:
        info = []
        platform, type = self.identify_url_components()
        if platform == 'spotify':
            spotify = SpotifyClient()
            info.append(spotify.get_track_info(url) if type == 'track' else spotify.get_playlist_info(url))
        elif platform in ['youtube', 'soundcloud']:
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
                print(f"Error extracting metadata: {errors}")

            output, errors = process.communicate()
            process.stdout.close()
            process.stderr.close()
            process.wait()
        else:
            exit(f"Unsupported URL: {url}")
            
        if platform in ['youtube', 'soundcloud']:
            name = info[0]['playlist_title'] if type == 'playlist' else info[0]['title']
            uploader = info[0]['uploader'] if platform == 'youtube' else self.url.split("/")[3]
        elif platform == 'spotify':
            if type == 'playlist':
                name = info[0]['name']
                uploader = info[0]['owner']['display_name']
            else:
                name = info[0]['name']
                uploader = info[0]['artists'][0]['name']

        self.path = os.path.join("/media", platform, uploader, name)
        self.platform = platform
        self.type = type
        self.info = info

    def identify_url_components(self) -> tuple[str, str]:
        url_patterns = [
            ('spotify', 'track', r'spotify\.com/track/'),
            ('spotify', 'playlist', r'spotify\.com/(album|playlist)/'),
            ('soundcloud', 'track', r'soundcloud\.com/[^/]+/[^/]+$'),
            ('soundcloud', 'playlist', r'soundcloud\.com/[^/]+/sets/'),
            ('youtube', 'track', r'youtube\.com/watch\?v='),
            ('youtube', 'playlist', r'youtube\.com/playlist\?list=')
        ]
        for platform, url_type, pattern in url_patterns:
            if re.search(pattern, self.url):
                return platform, url_type
        exit(f"Unsupported URL: {self.url}")

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
            if self.platform == "spotify":
                if 'track' in track:
                    track = track['track']
                name = track['name']
                url = track['external_urls']['spotify']
            else:
                name = track['webpage_url_basename']
                url = track['webpage_url']

            if self.type == "playlist":
                save = os.path.join(save, name)
            elif timestamps:
                os.makedirs(save, exist_ok=True)
                save = os.path.join(save, track['title'])

            if self.platform == "spotify":
                download_cmd = [
                    "spotify_dl",
                    "--url", url,
                    "-o", save.rsplit("/", 1)[0],
                ]
            else:
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
                print(f"Error downloading {name}: {errors.decode()}")
                return None

        tracks = self.info[0]['tracks']['items'] if self.platform == 'spotify' and self.type == 'playlist' else self.info
        self.downloaded.extend(run_concurrent_tasks(process_track, tracks))
        return self.downloaded
 