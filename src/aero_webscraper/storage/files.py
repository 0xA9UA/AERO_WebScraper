# MMA FILE SUMMARY
# Purpose: Owns bounded filesystem access, atomic durable writes, and envelopes.
# Public interface: safe_join, read_bounded, atomic_json, envelope, unwrap.
# Invariants: Reject symlinks and traversal; originals are never writable aliases.
from __future__ import annotations
import json, os, stat, tempfile
from pathlib import Path, PurePosixPath
from aero_webscraper.domain.identity import AeroError, canonical, digest

def safe_join(root: Path, relative: str) -> Path:
    if not relative or "\\" in relative or "\x00" in relative or ":" in relative:
        raise AeroError("UNSAFE_PATH")
    p=PurePosixPath(relative)
    if p.is_absolute() or any(x in {".",".."} for x in relative.split("/")):
        raise AeroError("UNSAFE_PATH")
    root=root.resolve()
    current=root
    for part in p.parts:
        current=current/part
        if current.is_symlink():
            raise AeroError("SYMLINK_REJECTED")
    if not current.resolve().is_relative_to(root):
        raise AeroError("PATH_ESCAPE")
    return current

def fsync_dir(path: Path) -> None:
    if os.name=="posix":
        fd=os.open(path,os.O_RDONLY | getattr(os,"O_DIRECTORY",0))
        try: os.fsync(fd)
        finally: os.close(fd)

def atomic_bytes(path: Path, data: bytes, mode: int=0o600) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=".aero-",dir=path.parent)
    try:
        with os.fdopen(fd,"wb") as f:
            f.write(data); f.flush(); os.fsync(f.fileno())
        os.chmod(tmp,mode)
        os.replace(tmp,path); fsync_dir(path.parent)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def atomic_json(path: Path, value: object) -> None:
    atomic_bytes(path,canonical(value)+b"\n")

def read_bounded(path: Path, limit: int) -> bytes:
    if path.is_symlink(): raise AeroError("SYMLINK_REJECTED")
    fd=os.open(path,os.O_RDONLY | getattr(os,"O_NOFOLLOW",0) | getattr(os,"O_NONBLOCK",0))
    try:
        st=os.fstat(fd)
        if not stat.S_ISREG(st.st_mode): raise AeroError("NON_REGULAR_FILE")
        if st.st_size>limit: raise AeroError("FILE_LIMIT")
        with os.fdopen(fd,"rb",closefd=False) as f: data=f.read(limit+1)
        if len(data)>limit: raise AeroError("FILE_LIMIT")
        after=os.fstat(fd)
        if len(data)!=st.st_size or after.st_mtime_ns!=st.st_mtime_ns or after.st_size!=st.st_size: raise AeroError("SOURCE_CHANGED_DURING_READ")
        return data
    finally: os.close(fd)

def envelope(record: dict) -> dict:
    return {"sha256":digest(canonical(record)),"record":record}

def unwrap(path: Path) -> dict:
    try:
        e=json.loads(read_bounded(path,16*1024*1024))
        if digest(canonical(e["record"]))!=e["sha256"]:
            raise AeroError("RECORD_INTEGRITY")
        return e["record"]
    except AeroError: raise
    except Exception: raise AeroError("RECORD_INVALID") from None


def read_import(root: Path, relative: str, limit: int) -> bytes:
    """Pin every directory descriptor on POSIX, eliminating ancestor-symlink races."""
    path=safe_join(root,relative)
    if os.name!="posix": return read_bounded(path,limit)
    flags=os.O_RDONLY | os.O_NOFOLLOW
    directory=os.open(root,flags | os.O_DIRECTORY)
    try:
        parts=PurePosixPath(relative).parts
        for part in parts[:-1]:
            next_fd=os.open(part,flags | os.O_DIRECTORY,dir_fd=directory)
            os.close(directory); directory=next_fd
        fd=os.open(parts[-1],flags | os.O_NONBLOCK,dir_fd=directory)
        try:
            before=os.fstat(fd)
            if not stat.S_ISREG(before.st_mode): raise AeroError("NON_REGULAR_FILE")
            if before.st_size>limit: raise AeroError("FILE_LIMIT")
            with os.fdopen(fd,"rb",closefd=False) as source: data=source.read(limit+1)
            after=os.fstat(fd)
            if len(data)>limit: raise AeroError("FILE_LIMIT")
            if len(data)!=before.st_size or before.st_mtime_ns!=after.st_mtime_ns or before.st_size!=after.st_size:
                raise AeroError("SOURCE_CHANGED_DURING_READ")
            return data
        finally: os.close(fd)
    except OSError: raise AeroError("UNSAFE_OR_UNREADABLE_IMPORT") from None
    finally: os.close(directory)