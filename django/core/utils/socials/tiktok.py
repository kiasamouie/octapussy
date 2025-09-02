import os
import requests
from typing import Optional
from utils.auth import OAuth2Handler

class TikTokAPI:
    def __init__(self, client_id: str, client_secret: str, account_id: str, auth_url: str, token_url: str, redirect_uri: str, token_file: str = os.path.join('tokens', 'tiktok.json')):
        self.account_id = account_id
        self.oauth_handler = OAuth2Handler(client_id, client_secret, auth_url, token_url, redirect_uri, token_file)
        self.token_data = self.oauth_handler.get_or_refresh_token(scope=["video.upload", "user.info.basic"])
        self.access_token = self.token_data.get('access_token')
        self.base_url = "https://open-api.tiktok.com"

    def upload_video(self, video_file_path: str, description: str) -> Optional[str]:
        upload_url = f"{self.base_url}/video/upload/"
        headers = {
            'Authorization': f"Bearer {self.access_token}",
            'Content-Type': 'multipart/form-data'
        }

        with open(video_file_path, 'rb') as video_file:
            files = {
                'video': video_file,
                'description': (None, description)
            }
            response = requests.post(upload_url, headers=headers, files=files)

        if response.status_code == 200:
            video_id = response.json().get('data', {}).get('video_id')
            print(f"Video uploaded successfully. Video ID: {video_id}")
            return video_id
        else:
            print(f"Failed to upload video: {response.json()}")
            return None

    def publish_video(self, video_id: str) -> bool:
        publish_url = f"{self.base_url}/video/publish/"
        payload = {
            'video_id': video_id,
            'access_token': self.access_token,
        }
        response = requests.post(publish_url, data=payload)

        if response.status_code == 200:
            print("Video published successfully:", response.json())
            return True
        else:
            print("Failed to publish video:", response.json())
            return False

    def upload_and_publish(self, video_file_path: str, description: str) -> bool:
        video_id = self.upload_video(video_file_path, description)
        if video_id:
            return self.publish_video(video_id)
        return False
