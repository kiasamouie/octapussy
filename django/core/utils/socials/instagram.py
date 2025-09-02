import os
import time
import requests
from utils.auth import OAuth2Handler

class InstagramAPI:
    def __init__(self, client_id, client_secret, account_id, auth_url, token_url, redirect_uri, token_file=os.path.join('tokens', 'instagram.json')):
        self.account_id = account_id
        self.oauth_handler = OAuth2Handler(client_id, client_secret, auth_url, token_url, redirect_uri, token_file)
        self.token_data = self.oauth_handler.get_or_refresh_token(scope=["instagram_basic", "instagram_content_publish"])
        self.access_token = self.token_data.get('access_token')
        self.base_url = "https://graph.facebook.com/v18.0"

    def exchange_for_long_lived_token(self, short_lived_token):
        url = f"https://graph.facebook.com/v18.0/oauth/access_token"
        params = {
            'grant_type': 'fb_exchange_token',
            'client_id': self.oauth_handler.client_id,
            'client_secret': self.oauth_handler.client_secret,
            'redirect_uri': self.oauth_handler.redirect_uri,
            'fb_exchange_token': short_lived_token
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            token_data = response.json()
            token_data['expires_at'] = int(time.time()) + token_data.get('expires_in', 3600 * 60)
            self.oauth_handler.save_token(token_data)
            self.access_token = token_data.get('access_token')
            return token_data['access_token']
        else:
            return None

    def upload_media(self, media_url, caption, media_type="image"):
        upload_url = f"{self.base_url}/{self.account_id}/media"
        payload = {
            'access_token': self.access_token,
            'caption': caption
        }
        if media_type == "image":
            payload['image_url'] = media_url
        elif media_type == "video":
            payload['media_type'] = 'REELS'
            payload['video_url'] = media_url
        response = requests.post(upload_url, data=payload)
        print("Upload Media Response Status Code:", response.status_code)
        print("Upload Media Response Content:", response.json())
        if response.status_code == 200:
            return response.json().get('id')
        else:
            return None

    def check_media_status(self, media_id):
        status_url = f"{self.base_url}/{media_id}"
        params = {
            'access_token': self.access_token,
            'fields': 'status'
        }
        while True:
            response = requests.get(status_url, params=params)
            if response.status_code == 200:
                media_status = response.json().get('status')
                print(f"Media processing status: {media_status}")
                if 'finished' in media_status.lower():
                    return True
                elif 'error' in media_status.lower():
                    return False
                else:
                    time.sleep(5)
            else:
                return False

    def publish_media(self, media_id):
        publish_url = f"{self.base_url}/{self.account_id}/media_publish"
        payload = {
            'creation_id': media_id,
            'access_token': self.access_token
        }
        response = requests.post(publish_url, data=payload)
        print("Publish Media Response Status Code:", response.status_code)
        print("Publish Media Response Content:", response.json())
        if response.status_code == 200:
            return True
        else:
            return False

    def upload_and_publish(self, media_url, caption, media_type="image"):
        media_id = self.upload_media(media_url, caption, media_type)
        if media_id:
            if self.check_media_status(media_id):
                return self.publish_media(media_id)
        return False
