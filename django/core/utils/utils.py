import logging
import json
import os
import boto3
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
logger = logging.getLogger(__name__)  

def log(message):
    print(message)
    logger.info(message)
   
class S3Client:
    client = None
    def __init__(self) -> None:
        if os.environ.get('AWS_ACCESS_KEY_ID') is None or os.environ.get('AWS_SECRET_ACCESS_KEY') is None:
            return None
        self.client = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        )
        self.bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')
        self.region = os.environ.get('AWS_S3_REGION_NAME')        
    
    def file_exists(self, key: str):
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except:
            return False
        
    def file_url(self, track, key: str):
        track['s3_file_key'] = key
        track['s3_file_url'] = f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{key}"
        return track['s3_file_url']

    def delete(self, key):
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
            return True
        except:
            return False

    def is_image_file(self, file_name) -> bool:
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
        extension = os.path.splitext(file_name)[1].lower()
        return extension in image_extensions

class SpotifyClient:
    def __init__(self, client_id=None, client_secret=None):
        load_dotenv()
        self.client_id = client_id or os.getenv('SPOTIPY_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('SPOTIPY_CLIENT_SECRET')
        if not self.client_id or not self.client_secret:
            raise ValueError("SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET must be set")
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=self.client_id, client_secret=self.client_secret))

    @property
    def client_id(self):
        return self._client_id

    @client_id.setter
    def client_id(self, value):
        self._client_id = value

    @property
    def client_secret(self):
        return self._client_secret

    @client_secret.setter
    def client_secret(self, value):
        self._client_secret = value

    def get_playlist_info(self, playlist_url):
        playlist_id = self._extract_id_from_url(playlist_url)
        playlist = self.sp.playlist(playlist_id)
        return playlist

    def get_track_info(self, track_url):
        track_id = self._extract_id_from_url(track_url)
        track = self.sp.track(track_id)
        return track

    def search(self, query, search_type='track', limit=10):
        results = self.sp.search(q=query, type=search_type, limit=limit)
        return results

    def _extract_id_from_url(self, url):
        return url.split("/")[-1].split("?")[0]

    def to_json(self, data):
        return json.dumps(data, indent=4)