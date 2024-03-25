import base64
import os
import os.path
from abc import abstractmethod
from email.message import EmailMessage
from typing import Any, Protocol

from google.auth.external_account_authorized_user import (
    Credentials as ExAuthCredentials,
)
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials as OAuthCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from .email_client import EmailClient

Credentials = OAuthCredentials | ExAuthCredentials


class GmailTokenStore(Protocol):
    @abstractmethod
    def get_token(self) -> Credentials | None:
        pass

    @abstractmethod
    def store_token(self, credentials: Credentials):
        pass


class GmailTokenFileStore(GmailTokenStore):
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def get_token(self) -> Credentials | None:
        if os.path.exists(self.file_path):
            creds = OAuthCredentials.from_authorized_user_file(self.file_path)
            return creds

    def store_token(self, credentials: Credentials):
        with open(self.file_path, "w") as token:
            token.write(credentials.to_json())


class GmailClient(EmailClient):
    scopes = ["https://www.googleapis.com/auth/gmail.modify"]
    local_server_port = 60131
    authorize_locally = True

    def __init__(self, client_secret_path: str, token_store: GmailTokenStore) -> None:
        self.token_store = token_store
        self._credentials = self._authorize(client_secret_path)
        self._service = self._build_service(self._credentials)

    def _authorize(self, client_secret_path: str) -> Credentials:
        creds = self.token_store.get_token()
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secret_path, self.scopes
                )
                creds = self._authorization_flow(flow)
        return creds

    def _authorization_flow(self, flow: InstalledAppFlow) -> Credentials:
        creds = flow.run_local_server(port=self.local_server_port, open_browser=False)
        return creds

    def _build_service(self, credentials: Credentials):
        return build("gmail", "v1", credentials=credentials)

    def _send_email(self, message: EmailMessage) -> dict[str, Any]:
        encoded_message = self._encode_message(message)
        raw_message = {"raw": encoded_message}
        res = (
            self._service.users()
            .messages()
            .send(userId="me", body=raw_message)
            .execute()
        )
        return res

    def _draft_email(self, message: EmailMessage) -> dict[str, Any]:
        encoded_message = self._encode_message(message)
        raw_message = {"message": {"raw": encoded_message}}
        draft = (
            self._service.users()
            .drafts()
            .create(userId="me", body=raw_message)
            .execute()
        )
        return draft

    @classmethod
    def _encode_message(cls, message: EmailMessage) -> str:
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return encoded_message

    @property
    def _credentials(self) -> Credentials:
        return self.__credentials

    @_credentials.setter
    def _credentials(self, value: Credentials):
        self.token_store.store_token(value)
        self.__credentials = value
