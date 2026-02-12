import firebase_admin  # type: ignore
from firebase_admin import credentials, auth
from .config import settings


def initialize_firebase_app():
    try:
        firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate(str(settings.FIREBASE_CREDENTIALS_PATH))
        firebase_admin.initialize_app(cred)
        print("Firebase app initialized.")


def verify_token(token: str) -> dict:
    return auth.verify_id_token(token)
