import os
from typing import Optional

import firebase_admin
from firebase_admin import credentials, firestore

_app: Optional[firebase_admin.App] = None


def get_firebase_app() -> firebase_admin.App:
    global _app
    if _app is not None:
        return _app

    cred = None
    if cred is None:
        sa_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if sa_path and os.path.exists(sa_path):
            cred = credentials.Certificate(sa_path)

    # Initialize app
    if cred is not None:
        _app = firebase_admin.initialize_app(cred)
    else:
        try:
            _app = firebase_admin.initialize_app()
        except ValueError as exc:
            raise RuntimeError(
                "Firebase Admin failed to initialize. Set GOOGLE_APPLICATION_CREDENTIALS."
            ) from exc

    return _app


def get_firestore_client() -> firestore.Client:
    get_firebase_app()
    return firestore.client()


