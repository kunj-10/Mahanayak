import os
import httpx
from typing import Optional, Dict


class GoogleAuth:
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
    ):
        self.client_id = client_id or os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = redirect_uri or os.getenv("GOOGLE_REDIRECT_URI")

        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            raise ValueError("Google OAuth credentials are missing")

        self.token_url = "https://oauth2.googleapis.com/token"
        self.user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"

    async def exchange_code_for_token(self, code: str) -> Dict:
        """
        Exchange authorization code for access and ID tokens.
        """
        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_url, data=data)
            response.raise_for_status()
            return response.json()
    
    async def refresh_access_token(self, refresh_token: str):
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_url, data=payload)
            response.raise_for_status()
            return response.json()
        
    async def get_user_info(self, access_token: str) -> Dict:
        """
        Retrieve user's profile information using access token.
        """
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(self.user_info_url, headers=headers)
            response.raise_for_status()
            return response.json()

    def get_authorization_url(self, scope: Optional[list] = None, state: Optional[str] = None) -> str:
        """
        Returns a URL to redirect the user to Google for OAuth.
        """
        scope = scope or [
            'openid',
            'email',
            'profile',
            'https://www.googleapis.com/auth/forms.body',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/calendar'
        ]
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(scope),
            "access_type": "offline",
            "include_granted_scopes": "true",
        }
        if state:
            params["state"] = state

        import urllib.parse
        return f"{base_url}?{urllib.parse.urlencode(params)}"


if __name__ == "__main__":
    auth = GoogleAuth()
    print(auth.get_authorization_url())