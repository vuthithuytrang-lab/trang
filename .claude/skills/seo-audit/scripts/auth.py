"""Nạp credential Google cho bước Search Console (gsc.py, index_status.py).

Bản rút gọn từ auth.py của skill seo-analyst: chỉ phần nạp credential, không chạy luồng OAuth.
Hỗ trợ hai loại file: authorized_user (refresh_token, client_id, client_secret) và service_account.

Vị trí credential lấy từ biến môi trường:
  GSC_CREDENTIALS_FILE  một file credential cố định
  GSC_CREDENTIALS_DIR   thư mục chứa nhiều file *.json, script tự dò file có quyền với property
Không đặt biến nào thì dò trong <thư mục skill>/credentials/.
"""
import glob
import json
import os

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]


def credential_candidates():
    f = os.environ.get("GSC_CREDENTIALS_FILE")
    if f:
        return [os.path.expanduser(f)]
    d = os.path.expanduser(os.environ.get("GSC_CREDENTIALS_DIR") or os.path.join(SKILL_DIR, "credentials"))
    return [p for p in sorted(glob.glob(os.path.join(d, "*.json"))) if not os.path.basename(p).startswith(".")]


def load_credentials(cred_path, scopes=None):
    scopes = scopes or SCOPES
    with open(cred_path) as f:
        data = json.load(f)

    cred_type = data.get("type", "")

    if cred_type == "service_account":
        from google.oauth2 import service_account
        return service_account.Credentials.from_service_account_file(cred_path, scopes=scopes)

    if cred_type in ("authorized_user", "") and "refresh_token" in data:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request

        effective_scopes = data.get("scopes") or scopes
        creds = Credentials.from_authorized_user_file(cred_path, effective_scopes)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            _save_token(cred_path, creds)
        return creds

    raise ValueError(f"Unknown credential type '{cred_type}' in {cred_path}")


def _save_token(path, creds):
    data = json.loads(creds.to_json())
    data["type"] = "authorized_user"
    with open(path, "w") as f:
        json.dump(data, f)
