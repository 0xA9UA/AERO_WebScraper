# MMA FILE SUMMARY
# Purpose: Enforces operator-owned rights and revocable, generation-bound delivery.
# Public interface: Policy, Delivery; operator methods are not registered as MCP tools.
# Collaborators: Store lock linearizes policy changes and final transport writes.
# Invariants: Default-deny content; queued results cannot survive OFF/ON or policy changes.
from __future__ import annotations
from dataclasses import dataclass, field
from urllib.parse import urlsplit
import json
import yaml
from aero_webscraper.domain.models import Rights
from aero_webscraper.domain.identity import AeroError
from aero_webscraper.storage.files import atomic_json, atomic_bytes, read_bounded

@dataclass
class Delivery:
    payload: dict
    generation: int
    policy_epoch: int
    items: list[tuple[str,str]] = field(default_factory=list)
    redistribution: bool = False

class Policy:
    def __init__(self,store): self.store=store

    def read(self,name: str) -> dict:
        if name not in {"permissions","retrieval","collection_policies","source_allowlists","retention"}:
            raise AeroError("INVALID_POLICY")
        value=yaml.safe_load(read_bounded(self.store.root/f"_policies/{name}.yaml",4*1024*1024))
        if not isinstance(value,dict): raise AeroError("INVALID_POLICY")
        return value

    def source_rule(self,source: str) -> dict:
        sources=self.read("permissions")["sources"]
        p=urlsplit(source)
        root="import:"+p.netloc if p.scheme=="import" else "host:"+(p.hostname or "")
        return sources.get(source,sources.get(root,{"rights":{},"license":None}))

    def rights(self,source: str,item_id: str | None=None) -> Rights:
        rule=dict(self.source_rule(source).get("rights",{}))
        if item_id:
            rule.update(self.read("permissions").get("item_overrides",{}).get(item_id,{}))
        return Rights.model_validate(rule)

    def require_source(self,source: str,*rights: str) -> Rights:
        value=self.rights(source)
        if any(getattr(value,r,None) is not True for r in rights):
            raise AeroError("SOURCE_PERMISSION_DENIED")
        return value

    def allowed(self,item: dict,redistribution: bool=False) -> bool:
        if item["state"] in {"QUARANTINED","FAILED"}: return False
        authorities=item.get("source_authority_keys") or [item["source_key"]]
        return all(self.rights(source,item["item_id"]).model_transmission is True and (not item.get("sha256") or self.rights(source,item["item_id"]).storage is True) and (not redistribution or self.rights(source,item["item_id"]).redistribution is True) for source in authorities)

    def snapshot(self) -> tuple[int,int]:
        gate=self.read("retrieval")
        if gate.get("enabled") is not True: raise AeroError("RETRIEVAL_OFF")
        return gate["generation"],gate.get("policy_epoch",0)

    def make_delivery(self,payload: dict,items=(),redistribution=False) -> Delivery:
        generation,epoch=self.snapshot()
        d=Delivery(payload,generation,epoch,list(items),redistribution)
        self.authorize(d)
        return d

    def authorize(self,d: Delivery) -> dict:
        generation,epoch=self.snapshot()
        if (generation,epoch)!=(d.generation,d.policy_epoch): raise AeroError("STALE_DELIVERY_REVOKED")
        for item_id,revision_id in d.items:
            if not self.allowed(self.store.item(item_id,revision_id),d.redistribution):
                raise AeroError("ITEM_PERMISSION_DENIED")
        return d.payload

    def set_retrieval(self,enabled: bool) -> dict:
        with self.store.lock:
            p=self.read("retrieval"); p["enabled"]=enabled; p["generation"]+=1
            atomic_json(self.store.root/"_policies/retrieval.yaml",p)
            return {"enabled":enabled,"generation":p["generation"],"previous_context_erased":False}

    def _bump(self):
        g=self.read("retrieval"); g["policy_epoch"]=g.get("policy_epoch",0)+1
        atomic_json(self.store.root/"_policies/retrieval.yaml",g)
        atomic_bytes(self.store.root/"_indexes/dirty",b"policy changed\n")

    def grant(self,source: str,rights: Rights,license_id: str | None=None) -> None:
        """Trusted operator boundary, intentionally absent from the tool registry."""
        if source.startswith(("http:","https:")):
            from aero_webscraper.domain.identity import clean_url
            source=clean_url(source)
        with self.store.lock:
            p=self.read("permissions"); p["sources"][source]={"rights":rights.model_dump(),"license":license_id}
            atomic_json(self.store.root/"_policies/permissions.yaml",p); self._bump()

    def override(self,item_id: str,rights: dict) -> None:
        Rights.model_validate(rights)
        with self.store.lock:
            p=self.read("permissions"); p["item_overrides"][item_id]=rights
            atomic_json(self.store.root/"_policies/permissions.yaml",p); self._bump()

    def configure_root(self,name: str,path,kind: str="imports") -> None:
        from pathlib import Path
        from aero_webscraper.domain.identity import check_id
        check_id(name)
        if kind not in {"imports","intakes"}: raise AeroError("INVALID_ROOT_KIND")
        path=Path(path).expanduser().resolve()
        if not path.is_dir(): raise AeroError("ROOT_NOT_DIRECTORY")
        # Only the designated inbox may overlap the persistent library.
        if path.is_relative_to(self.store.root) or self.store.root.is_relative_to(path):
            raise AeroError("ROOT_OVERLAPS_LIBRARY")
        with self.store.lock:
            p=self.read("permissions"); p[kind][name]=str(path)
            atomic_json(self.store.root/"_policies/permissions.yaml",p); self._bump()

    def allow_host(self,host: str) -> None:
        import re
        host=host.encode("idna").decode().lower()
        if not re.fullmatch(r"[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?",host): raise AeroError("INVALID_HOST")
        with self.store.lock:
            p=self.read("source_allowlists"); p["hosts"]=sorted(set(p["hosts"]+[host]))
            atomic_json(self.store.root/"_policies/source_allowlists.yaml",p); self._bump()