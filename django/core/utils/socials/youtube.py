

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from core.utils.auth import OAuth2Handler

class YouTubeAPI:
    def __init__(self, email: str, provider: str = "google"):
        self.oauth_handler = OAuth2Handler(email=email, provider=provider)
        self.token_data = self.oauth_handler.get_or_refresh_token()
        if not self.token_data:
            raise ValueError(f"Failed to retrieve valid OAuth token for {email}.")
        self.access_token = self.token_data.get("access_token")
        self.refresh_token = self.token_data.get("refresh_token")
        self.service = self.get_authenticated_service()

    def get_authenticated_service(self):
        token_url = self.oauth_handler.user_data["token_url"]
        client_id = self.oauth_handler.user_data["client_id"]
        client_secret = self.oauth_handler.user_data["client_secret"]
        credentials = Credentials(
            token=self.access_token,
            refresh_token=self.refresh_token,
            token_uri=token_url,
            client_id=client_id,
            client_secret=client_secret,
            # scopes=["https://www.googleapis.com/auth/youtube.upload"]
        )
        return build("youtube", "v3", credentials=credentials)

    def upload_video(self,video_file: str,title: str,description: str,category_id: str,tags: list) -> str:
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": category_id,
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
            },
        }

        try:
            insert_request = self.service.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=MediaFileUpload(video_file, chunksize=-1, resumable=True),
            )
            response = insert_request.execute()
            return response.get("id")
        except Exception as e:
            print(f"Error uploading video: {e}")
            return None
    
    def comment_on_video(self, video_id: str, comment_text: str) -> dict:
        try:
            insert_request = self.service.commentThreads().insert(
                part="snippet",
                body={
                    "snippet": {
                        "videoId": video_id,
                        "topLevelComment": {
                            "snippet": {
                                "textOriginal": comment_text
                            }
                        }
                    }
                }
            )
            response = insert_request.execute()
            return response
        except Exception as e:
            print(f"Error commenting on video: {e}")
            return {}
        
    def get_video_comments(self, video_id: str, max_results: int = 50) -> list:
        try:
            request = self.service.commentThreads().list(
                part="snippet,replies",
                videoId=video_id,
                order="time",
                textFormat="plainText",
                maxResults=max_results
            )
            response = request.execute()
            items = response.get("items", [])
            return items
        except Exception as e:
            print(f"Error retrieving comments: {e}")
            return []
        
    def reply_to_comment(self, parentId: str, reply_text: str) -> dict:
        try:
            insert_request = self.service.comments().insert(
                part="snippet",
                body={
                    "snippet": {
                        "parentId": parentId,
                        "textOriginal": reply_text
                    }
                }
            )
            response = insert_request.execute()
            return response
        except Exception as e:
            print(f"Error replying to comment: {e}")
            return {}

