# MMA FILE SUMMARY
# Purpose: Owns immutable content/record commits and redo-journal crash recovery.
# Public interface: Store, lock, put_object, get_object, commit, recover, records.
# Collaborators: files provides durable writes; catalog is a rebuildable consumer.
# Invariants: A single interprocess lock orders commits; recovery never trusts indexes.
from __future__ import annotations
import json, os, uuid
from pathlib import Path
from filelock import FileLock
from aero_webscraper.domain.identity import AeroError, canonical, digest, check_id
from aero_webscraper.storage.files import atomic_bytes, atomic_json, envelope, unwrap, read_bounded, safe_join

class Store:
    def __init__(self, root: Path):
        self.root=root.resolve()
        if not (self.root/"library.yaml").is_file(): raise AeroError("LIBRARY_NOT_INITIALIZED")
        self.lock=FileLock(str(self.root/"_journal/library.lock"),timeout=30)
        with self.lock: self.recover()

    def object_path(self, sha: str) -> Path:
        import re
        if not re.fullmatch("[0-9a-f]{64}",sha): raise AeroError("INVALID_SHA256")
        return safe_join(self.root,f"_objects/sha256/{sha[:2]}/{sha}")

    def put_object(self, data: bytes) -> str:
        sha=digest(data); path=self.object_path(sha)
        with self.lock:
            if path.exists():
                if digest(read_bounded(path,len(data)))!=sha: raise AeroError("OBJECT_INTEGRITY")
            else: atomic_bytes(path,data,0o400)
        return sha

    def get_object(self, sha: str, limit: int=1073741824) -> bytes:
        data=read_bounded(self.object_path(sha),limit)
        if digest(data)!=sha: raise AeroError("OBJECT_INTEGRITY")
        return data

    def commit(self, writes: dict[str,dict], fail_after: int | None=None) -> str:
        """Redo transaction; fail_after is a test-only fault injection, not a tool input."""
        tx=uuid.uuid4().hex
        with self.lock:
            encoded={}
            for relative,value in writes.items():
                if not relative.startswith(("_records/","_derived/")):
                    raise AeroError("INVALID_COMMIT_DESTINATION")
                path=safe_join(self.root,relative)
                e=envelope(value)
                if path.exists() and unwrap(path)!=value: raise AeroError("IMMUTABLE_RECORD_CONFLICT")
                encoded[relative]=e
            journal=self.root/f"_journal/{tx}.pending.json"
            atomic_json(journal,{"tx":tx,"writes":encoded})
            atomic_bytes(self.root/"_indexes/dirty",b"rebuild required\n")
            if fail_after==0: raise AeroError("INJECTED_INTERRUPTION")
            for n,(relative,value) in enumerate(encoded.items(),1):
                atomic_json(safe_join(self.root,relative),value)
                if fail_after==n: raise AeroError("INJECTED_INTERRUPTION")
            atomic_json(self.root/f"_journal/{tx}.committed.json",{"tx":tx,"records":list(encoded)})
            journal.unlink()
        return tx

    def recover(self) -> int:
        recovered=0
        for journal in sorted((self.root/"_journal").glob("*.pending.json")):
            data=json.loads(read_bounded(journal,64*1024*1024))
            for relative,value in data["writes"].items():
                if not relative.startswith(("_records/","_derived/")) or digest(canonical(value["record"]))!=value["sha256"]:
                    raise AeroError("JOURNAL_INTEGRITY")
                path=safe_join(self.root,relative)
                if path.exists() and unwrap(path)!=value["record"]: raise AeroError("RECOVERY_CONFLICT")
                atomic_json(path,value)
            atomic_json(self.root/f"_journal/{data['tx']}.committed.json",{"tx":data["tx"],"records":list(data["writes"]),"recovered":True})
            atomic_bytes(self.root/"_indexes/dirty",b"recovered\n")
            journal.unlink(); recovered+=1
        return recovered

    def records(self, kind: str):
        if kind not in {"items","entities","source_occurrences","relations","collections","processing_runs"}:
            raise AeroError("INVALID_RECORD_KIND")
        for path in sorted((self.root/"_records"/kind).rglob("*.json")):
            yield unwrap(path)

    def item_path(self,item_id: str,revision_id: str) -> Path:
        return self.root/"_records/items"/check_id(item_id)/(check_id(revision_id)+".json")

    def item(self,item_id: str,revision_id: str) -> dict:
        p=self.item_path(item_id,revision_id)
        if not p.is_file(): raise AeroError("ITEM_NOT_FOUND")
        return unwrap(p)