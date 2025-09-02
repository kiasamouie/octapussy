

import requests
import time
from typing import Optional, Dict
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
from datetime import datetime, timezone

class OAuth2Handler:
    def __init__(self, email: str, provider: str):
        User = get_user_model()
        user_obj = User.objects.filter(email=email).first()
        if not user_obj:
            raise ValueError(f"No user found with email '{email}'.")
        social_account = SocialAccount.objects.filter(user=user_obj, provider=provider).first()
        if not social_account:
            raise ValueError(f"No social account found for provider '{provider}' and user '{email}'.")
        try:
            social_app = SocialApp.objects.get(provider=provider)
        except SocialApp.DoesNotExist:
            raise ValueError(f"No SocialApp configured for provider '{provider}'.")
        social_token = SocialToken.objects.filter(account=social_account).first()
        if not social_token:
            raise ValueError(f"No social token found for provider '{provider}' and user '{email}'.")

        if social_token.expires_at:
            expires_ts = int(social_token.expires_at.timestamp())
        else:
            expires_ts = 0

        self.user_data = {
            "user_id": user_obj.pk,
            "account_id": social_account.pk,
            "client_id": social_app.client_id,
            "client_secret": social_app.secret,
            "access_token": social_token.token,
            "refresh_token": social_account.extra_data.get("refresh_token") or social_token.token,
            "token_url": "https://oauth2.googleapis.com/token",
            "expires_at": expires_ts,
        }
        self.provider = provider

    def load_token(self) -> Optional[Dict]:
        """
        Loads current token data from self.user_data.
        """
        if not self.user_data:
            raise ValueError(f"No user data.")
        return {
            "access_token": self.user_data.get("access_token"),
            "refresh_token": self.user_data.get("refresh_token"),
            "expires_at": self.user_data.get("expires_at"),
        }

    def save_token(self, token_data: Dict) -> None:
        social_token = SocialToken.objects.filter(account_id=self.user_data["account_id"]).first()
        if not social_token:
            return
        social_token.token = token_data["access_token"]
        expires_at_ts = token_data.get("expires_at")
        if expires_at_ts:
            dt_obj = datetime.fromtimestamp(expires_at_ts, tz=timezone.utc)
            social_token.expires_at = dt_obj
        social_token.save()

        if "refresh_token" in token_data:
            social_account = social_token.account
            social_account.extra_data["refresh_token"] = token_data["refresh_token"]
            social_account.save()

    def handle_access_token(self,authorization_code: Optional[str] = None,refresh_token: Optional[str] = None,is_refresh: bool = False) -> Optional[Dict]:
        if not self.user_data:
            return None
        payload = {
            "client_id": self.user_data["client_id"],
            "client_secret": self.user_data["client_secret"],
        }
        token_url = self.user_data["token_url"]
        if is_refresh:
            if not refresh_token:
                print("Error: Missing refresh token for refresh flow.")
                return None
            payload.update({
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            })
        else:
            # dont need this because of allauth
            payload.update({
                "code": authorization_code,
                "redirect_uri": f"http://localhost:5000/accounts/{self.provider}/login/callback/",
                "grant_type": "authorization_code",
            })

        response = requests.post(token_url, data=payload)
        if response.status_code == 200:
            token_data = response.json()
            expires_in = token_data.get("expires_in", 3600)
            token_data["expires_at"] = int(time.time()) + expires_in
            self.save_token(token_data)
            return token_data
        else:
            print(f"Failed to handle token. Status: {response.status_code}")
            print(f"Response: {response.content}")
            return None

    def get_or_refresh_token(self) -> Optional[Dict]:
        token_data = self.load_token()
        if not token_data:
            return None
        now_ts = int(time.time())
        expires_at_ts = token_data.get("expires_at", 0)
        if expires_at_ts < now_ts + 30:
            print("Token expired or expiring soon. Attempting refresh...")
            refresh_tok = token_data.get("refresh_token") or token_data["access_token"]
            return self.handle_access_token(refresh_token=refresh_tok, is_refresh=True)
        return token_data
