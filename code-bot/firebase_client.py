import os
import sys
import time
import requests

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from config import FIREBASE_DATABASE_URL

# Check if Firebase Admin SDK can be initialized
_admin_db = None
try:
    import firebase_admin
    from firebase_admin import credentials, db

    # Look for service account in local dir or parent dir
    possible_paths = [
        os.path.join(os.path.dirname(__file__), "serviceAccountKey.json"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "quipu-c6fdb-firebase-adminsdk-fbsvc-a904bcabc6.json"),
        os.path.join(os.path.dirname(__file__), "quipu-c6fdb-firebase-adminsdk-fbsvc-a904bcabc6.json"),
    ]
    
    cred_file = next((p for p in possible_paths if os.path.exists(p)), None)
    if cred_file and not firebase_admin._apps:
        cred = credentials.Certificate(cred_file)
        firebase_admin.initialize_app(cred, {"databaseURL": FIREBASE_DATABASE_URL})
        _admin_db = db
        print(f"[Firebase Admin] Initialized successfully using: {os.path.basename(cred_file)}")
    elif firebase_admin._apps:
        _admin_db = db
except Exception as e:
    print(f"[Firebase Admin Notice] Falling back to REST API ({e})")
    _admin_db = None

def get_bot_status() -> bool:
    """Reads whether the bot is set to active from Firebase RTDB. Defaults to False (OFF)."""
    if _admin_db:
        try:
            val = _admin_db.reference("bot_status").get()
            if isinstance(val, dict):
                return bool(val.get("is_active", False))
            elif isinstance(val, bool):
                return val
            return False
        except Exception as e:
            print(f"[Firebase Admin Warning] {e}, trying REST...")

    try:
        url = f"{FIREBASE_DATABASE_URL}/bot_status.json"
        res = requests.get(url, timeout=5)
        if res.status_code == 200 and res.json() is not None:
            data = res.json()
            if isinstance(data, dict):
                return bool(data.get("is_active", False))
            return bool(data)
        return False
    except Exception as e:
        print(f"[Firebase Warning] Could not fetch bot status: {e}")
        return False

def set_bot_status(is_active: bool) -> bool:
    """Sets the bot status flag in Firebase RTDB."""
    if _admin_db:
        try:
            _admin_db.reference("bot_status").set({
                "is_active": is_active,
                "updated_at": int(time.time() * 1000)
            })
            return True
        except Exception as e:
            print(f"[Firebase Admin Warning] {e}, trying REST...")

    try:
        url = f"{FIREBASE_DATABASE_URL}/bot_status.json"
        res = requests.put(url, json={"is_active": is_active, "updated_at": int(time.time() * 1000)}, timeout=5)
        return res.status_code == 200
    except Exception as e:
        print(f"[Firebase Error] Could not update bot status: {e}")
        return False

def push_question(question_data: dict) -> str:
    """Uploads a solved question to Firebase RTDB under /questions."""
    if "timestamp" not in question_data:
        question_data["timestamp"] = int(time.time() * 1000)

    if _admin_db:
        try:
            ref = _admin_db.reference("questions").push(question_data)
            return ref.key
        except Exception as e:
            print(f"[Firebase Admin Warning] {e}, trying REST...")

    try:
        url = f"{FIREBASE_DATABASE_URL}/questions.json"
        res = requests.post(url, json=question_data, timeout=10)
        if res.status_code == 200:
            return res.json().get("name", "unknown")
        else:
            print(f"[Firebase Error] Upload failed: {res.status_code} {res.text}")
            return None
    except Exception as e:
        print(f"[Firebase Error] Could not upload question: {e}")
        return None

def get_questions() -> dict:
    """Retrieves all questions from Firebase RTDB."""
    if _admin_db:
        try:
            return _admin_db.reference("questions").get() or {}
        except Exception as e:
            print(f"[Firebase Admin Warning] {e}, trying REST...")

    try:
        url = f"{FIREBASE_DATABASE_URL}/questions.json"
        res = requests.get(url, timeout=8)
        if res.status_code == 200:
            return res.json() or {}
        return {}
    except Exception as e:
        print(f"[Firebase Error] Could not get questions: {e}")
        return {}

def delete_question(qid: str) -> bool:
    """Deletes a specific question by id from Firebase RTDB."""
    if _admin_db:
        try:
            _admin_db.reference(f"questions/{qid}").delete()
            return True
        except Exception as e:
            print(f"[Firebase Admin Warning] {e}, trying REST...")

    try:
        url = f"{FIREBASE_DATABASE_URL}/questions/{qid}.json"
        res = requests.delete(url, timeout=5)
        return res.status_code == 200
    except Exception as e:
        print(f"[Firebase Error] Could not delete question: {e}")
        return False

def clear_all_questions() -> bool:
    """Clears all questions from Firebase RTDB."""
    if _admin_db:
        try:
            _admin_db.reference("questions").delete()
            return True
        except Exception as e:
            print(f"[Firebase Admin Warning] {e}, trying REST...")

    try:
        url = f"{FIREBASE_DATABASE_URL}/questions.json"
        res = requests.delete(url, timeout=5)
        return res.status_code == 200
    except Exception as e:
        print(f"[Firebase Error] Could not clear questions: {e}")
        return False
