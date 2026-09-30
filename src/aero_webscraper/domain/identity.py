# MMA FILE SUMMARY
# Purpose: Provides deterministic IDs, safe labels, and source identities.
# Public interface: stable_id, digest, canonical, slug, safe_filename, clean_url.
# Invariants: Credentials and secret-bearing URLs never enter ordinary records.
from __future__ import annotations
import hashlib, json, re, unicodedata, uuid
from datetime import datetime, timezone
from urllib.parse import urlsplit, urlunsplit, parse_qsl

class AeroError(Exception):
    """Safe, stable error code with no imported content or credentials."""
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)

def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

def canonical(value: object) -> bytes:
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def stable_id(kind: str, key: str) -> str:
    return kind + "-" + uuid.uuid5(uuid.NAMESPACE_URL,"aero:"+kind+":"+key).hex

def slug(text: str, default: str="unknown") -> str:
    text=unicodedata.normalize("NFKD",text).encode("ascii","ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+","-",text).strip("-")[:80] or default

def safe_filename(name: str) -> str:
    name = name.replace("\\","/").rsplit("/",1)[-1]
    name = re.sub(r"[^A-Za-z0-9._ -]","_",name).strip(" .")[:150]
    if not name or name.split(".")[0].upper() in {"CON","PRN","AUX","NUL",*(f"COM{i}" for i in range(10)),*(f"LPT{i}" for i in range(10))}:
        return "unnamed-file"
    return name

def check_id(value: str) -> str:
    if not re.fullmatch(r"[a-z][a-z0-9-]{1,100}",value):
        raise AeroError("INVALID_ID")
    return value

def clean_url(url: str) -> str:
    try:
        if len(url)>4096 or any(ord(c)<33 or ord(c)==127 for c in url):
            raise ValueError()
        p=urlsplit(url)
        if p.scheme not in {"http","https"} or not p.hostname or p.username or p.password or "\\" in url:
            raise ValueError()
        host=p.hostname.encode("idna").decode("ascii").lower()
        port=p.port
        if port not in {None,80,443}:
            raise ValueError()
        for k,v in parse_qsl(p.query,keep_blank_values=True):
            if re.search(r"token|secret|password|signature|api.?key|credential|authorization",k,re.I):
                raise AeroError("SECRET_URL_REJECTED")
        netloc=("["+host+"]" if ":" in host else host)+(":"+str(port) if port else "")
        return urlunsplit((p.scheme,netloc,p.path or "/",p.query,""))
    except AeroError:
        raise
    except Exception:
        raise AeroError("UNSAFE_URL") from None