import firebase_admin
from firebase_admin import credentials, auth
from .config import settings

def initialize_firebase_app():
    if not firebase_admin._apps:
        cred = credentials.Certificate(settings.firebase_credentials)
        firebase_admin.initialize_app(cred)
        print("Firebase app initialized.")

def verify_token(token: str) -> dict:
    return auth.verify_id_token(token)

