"""Credential loading — cần CẢ Sheets lẫn Docs scope (chưa skill nào ở đây xin scope Docs,
nên lần đầu chạy chắc chắn phải OAuth mới). Auto-browser fallback, tái dùng OAuth client
config của các skill khác nếu có."""
from __future__ import annotations

import json
import os
import secrets
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

SCRIPTS_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPTS_DIR.parent
SKILLS_ROOT = SKILL_DIR.parent
OAUTH_CLIENTS_DIR = SKILL_DIR / "oauth_clients"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/documents",
]

_REDIRECT_PORT = 8766  # khác cổng maps-audit (8765) để tránh đụng nếu chạy song song
_REDIRECT_URI = f"http://localhost:{_REDIRECT_PORT}"

# Skill cài cạnh nhau trong cùng thư mục skills → dùng chung token nếu có.
_CREDENTIAL_SOURCES = [
    SKILLS_ROOT / "maps-audit" / "credentials",
    SKILLS_ROOT / "cro-setup" / "credentials",
    SKILLS_ROOT / "seo-analyst" / "credentials",
    SKILLS_ROOT / "cro-report" / "credentials",
    SKILLS_ROOT / "site-auditor" / "credentials",
    SKILL_DIR / "credentials",
]


def _has_required_scopes(creds) -> bool:
    scopes = set(creds.scopes or [])
    return all(req in scopes for req in SCOPES)


def load_credential_file(path: Path):
    """Load + auto-refresh a credential JSON. Returns None on failure."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials

        data = json.loads(path.read_text())
        if "refresh_token" not in data:
            return None

        effective_scopes = data.get("scopes") or SCOPES
        creds = Credentials.from_authorized_user_file(str(path), effective_scopes)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            updated = json.loads(creds.to_json())
            updated["type"] = "authorized_user"
            path.write_text(json.dumps(updated, indent=2))
        return creds
    except Exception as e:
        print(f"  Warning: skip {path.name} — {e}", flush=True)
        return None


def find_credential():
    """Scan mọi nguồn credential, trả (label, creds) đầu tiên có ĐỦ scope spreadsheets+documents.

    Vì chưa skill nào từng xin scope documents, kết quả gần như luôn None trong lần chạy
    đầu — cần auto_oauth()/generate_auth_url() để lấy token mới.
    """
    seen = set()
    for creds_dir in _CREDENTIAL_SOURCES:
        if not creds_dir.exists():
            continue
        source = creds_dir.parent.name
        for cred_file in sorted(creds_dir.glob("*.json")):
            if cred_file.name.startswith("."):
                continue
            creds = load_credential_file(cred_file)
            if creds is None:
                continue
            key = creds.refresh_token
            if key in seen:
                continue
            seen.add(key)
            if _has_required_scopes(creds):
                return f"{source}/{cred_file.stem}", creds
    return None


def get_user_email(creds) -> str:
    try:
        import requests as req
        from google.auth.transport.requests import Request

        if creds.expired:
            creds.refresh(Request())
        r = req.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            headers={"Authorization": f"Bearer {creds.token}"},
            timeout=10,
        )
        return r.json().get("email", "unknown")
    except Exception:
        return "unknown"


# ── OAuth client discovery (fallback nếu chưa có token nào) ─────────────────

def find_all_oauth_clients() -> list[dict]:
    configs = []
    seen_ids = set()

    def _load(path: Path):
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text())
            cfg = data.get("installed") or data.get("web") or data
            cid = cfg.get("client_id", "")
            if cid and cid not in seen_ids:
                seen_ids.add(cid)
                configs.append(data if ("installed" in data or "web" in data) else {"installed": data})
        except Exception as e:
            print(f"  Warning: skip {path.name} — {e}", file=sys.stderr)

    OAUTH_CLIENTS_DIR.mkdir(parents=True, exist_ok=True)
    for f in sorted(OAUTH_CLIENTS_DIR.glob("*.json")):
        _load(f)
    _load(SKILL_DIR / "oauth_client.json")
    for skill in ("maps-audit", "site-auditor", "cro-setup", "seo-analyst"):
        _load(SKILLS_ROOT / skill / "oauth_client.json")
        clients_subdir = SKILLS_ROOT / skill / "oauth_clients"
        if clients_subdir.exists():
            for f in sorted(clients_subdir.glob("*.json")):
                _load(f)

    return configs


def auto_oauth(name: str = "default") -> dict:
    from google_auth_oauthlib.flow import InstalledAppFlow

    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    clients = find_all_oauth_clients()
    if not clients:
        return {
            "ok": False,
            "error": (
                "Không tìm thấy OAuth client config.\n"
                f"Đặt file client_secret.json vào: {OAUTH_CLIENTS_DIR}/"
            ),
        }

    token_dir = SKILL_DIR / "credentials"
    token_dir.mkdir(parents=True, exist_ok=True)
    token_path = token_dir / f"{name}.json"

    last_error = None
    for i, client_config in enumerate(clients):
        print(f"  OAuth client {i + 1}/{len(clients)}...", file=sys.stderr, flush=True)
        try:
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(
                port=_REDIRECT_PORT,
                open_browser=True,
                success_message=(
                    "<h2>Đăng nhập thành công!</h2>"
                    "<p>Bạn có thể đóng tab này và quay lại Claude Code.</p>"
                ),
                authorization_prompt_message="",
            )
            data = json.loads(creds.to_json())
            data["type"] = "authorized_user"
            token_path.write_text(json.dumps(data, indent=2))
            os.chmod(token_path, 0o600)

            email = get_user_email(creds)
            return {"ok": True, "token_path": str(token_path), "email": email}

        except Exception as e:
            err = str(e).lower()
            if any(k in err for k in ["access_denied", "accessdenied", "access blocked", "403"]):
                last_error = f"Client {i + 1}: access denied — email chưa được thêm vào Test Users của GCP project"
                print(f"  {last_error}", file=sys.stderr, flush=True)
                continue
            return {"ok": False, "error": str(e)}

    return {
        "ok": False,
        "error": (
            f"Tất cả {len(clients)} OAuth client đều bị từ chối.\n"
            f"Lỗi cuối: {last_error}\n"
            "Fix: GCP Console → OAuth consent screen → Test users → thêm email của bạn.\n"
            "Nếu đây là lần đầu skill này xin scope Docs, cũng kiểm tra Docs API đã được enable "
            "chưa: https://console.cloud.google.com/apis/library/docs.googleapis.com"
        ),
    }


def generate_auth_url(name: str = "default") -> dict:
    from google_auth_oauthlib.flow import Flow

    clients = find_all_oauth_clients()
    if not clients:
        raise FileNotFoundError("Không tìm thấy OAuth client config.")

    client_config = clients[0]
    flow = Flow.from_client_config(client_config, SCOPES, redirect_uri=_REDIRECT_URI)
    state = secrets.token_urlsafe(16)
    auth_url, _ = flow.authorization_url(access_type="offline", prompt="consent", state=state)

    pending = SKILL_DIR / "credentials" / f".{name}_pending.json"
    pending.parent.mkdir(parents=True, exist_ok=True)
    pending.write_text(json.dumps({
        "state": state,
        "redirect_uri": _REDIRECT_URI,
        "client_config": client_config,
    }))

    return {"auth_url": auth_url}


def complete_auth(name: str, redirect_url: str) -> str:
    from google_auth_oauthlib.flow import Flow

    pending_path = SKILL_DIR / "credentials" / f".{name}_pending.json"
    if not pending_path.exists():
        raise ValueError(f"Không tìm thấy pending auth cho '{name}'.")

    pending = json.loads(pending_path.read_text())
    raw = redirect_url.strip()
    if raw.startswith("http"):
        params = parse_qs(urlparse(raw).query)
        code = params.get("code", [None])[0]
        if not code:
            raise ValueError("Không tìm thấy 'code' trong URL.")
    else:
        code = raw

    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    flow = Flow.from_client_config(
        pending["client_config"], SCOPES,
        redirect_uri=pending["redirect_uri"],
        state=pending["state"],
    )
    flow.fetch_token(code=code)

    token_path = SKILL_DIR / "credentials" / f"{name}.json"
    data = json.loads(flow.credentials.to_json())
    data["type"] = "authorized_user"
    token_path.write_text(json.dumps(data, indent=2))
    os.chmod(token_path, 0o600)
    pending_path.unlink(missing_ok=True)
    return str(token_path)
