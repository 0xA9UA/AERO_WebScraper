# MMA FILE SUMMARY
# Purpose: Preserves supplied library/entity templates and creates pointer-only views.
# Public interface: init_library, materialize_entity, project_item, taxonomy.
# Invariants: Navigation is generated, advisory, and never a verified scientific record.
from __future__ import annotations
import json, os
from pathlib import Path
from aero_webscraper.domain.identity import slug, stable_id, canonical
from aero_webscraper.storage.files import atomic_bytes, atomic_json, safe_join

def taxonomy() -> dict:
    return json.loads(Path(__file__).with_name("taxonomy.json").read_text())

def init_library(root: Path) -> Path:
    root=root.expanduser().resolve()
    root.mkdir(parents=True,exist_ok=True)
    os.chmod(root,0o700)
    if (root/"library.yaml").exists(): return root
    t=taxonomy()
    for rel in t["library"]:
        if "<" in rel: rel=rel.split("<",1)[0].rstrip("/")
        if rel and not rel.rsplit("/",1)[-1].count("."):
            (root/rel).mkdir(parents=True,exist_ok=True)
    for name in ["_policies","_staging","_journal","_indexes","_quarantine","_jobs","_inbox","_exports","_derived","_objects/sha256"]:
        (root/name).mkdir(parents=True,exist_ok=True)
    for kind in ["entities","items","source_occurrences","relations","collections","processing_runs"]:
        (root/"_records"/kind).mkdir(parents=True,exist_ok=True)
    atomic_json(root/"library.yaml",{"schema_version":"1.0.0","library_id":stable_id("library",str(root)),"source_authority":"_records","objects":"_objects/sha256"})
    atomic_json(root/"_policies/taxonomy.yaml",t)
    atomic_json(root/"_policies/permissions.yaml",{"schema_version":"1.0.0","sources":{},"item_overrides":{},"imports":{"inbox":str(root/"_inbox")},"intakes":{}})
    atomic_json(root/"_policies/source_allowlists.yaml",{"hosts":[],"allow_http":False})
    atomic_json(root/"_policies/collection_policies.yaml",{"max_file_bytes":33554432,"max_folder_files":200,"max_folder_bytes":134217728,"parser_timeout_seconds":10,"max_archive_files":200,"max_expanded_bytes":33554432,"max_text_chars":1000000,"rate_interval_seconds":1.0,"network_timeout_seconds":10,"max_redirects":5,"max_job_seconds":3600,"max_job_requests":4000})
    atomic_json(root/"_policies/retrieval.yaml",{"enabled":False,"generation":0,"semantic_enabled":False,"policy_epoch":0})
    atomic_json(root/"_policies/retention.yaml",{"automatic_deletion":False,"orphan_objects":"report_only","quarantine":"operator_review"})
    atomic_bytes(root/"README.md",b"# AERO reference library\n\nAdvisory references only. Records and original bytes are authoritative for provenance, not scientific correctness. Navigation and indexes are generated.\n")
    return root

def entity_base(entity: dict) -> str:
    kind=entity["kind"]; p=slug(entity["platform"]); m=slug(entity.get("manufacturer") or "unknown")
    return {"game_console":f"devices/game_consoles/{m}/{p}","game":f"games/{p}","software_project":f"software_projects/{p}","online_service":f"online_services/{p}","peripheral":f"devices/peripherals/{m}/{p}"}[kind]

def materialize_entity(root: Path, entity: dict, record_path: str) -> str:
    base=entity_base(entity); target=safe_join(root,base); target.mkdir(parents=True,exist_ok=True)
    key={"game_console":"console"}.get(entity["kind"],entity["kind"])
    for rel in taxonomy()[key]:
        if "<" in rel: rel=rel.split("<",1)[0].rstrip("/")
        if rel and not rel.endswith((".json",".md")):
            safe_join(target,rel).mkdir(parents=True,exist_ok=True)
    ref_name={"game_console":"platform","game":"game","software_project":"project","online_service":"service","peripheral":"peripheral"}[entity["kind"]]+".ref.json"
    atomic_json(target/ref_name,{"record":record_path,"entity_id":entity["entity_id"],"advisory":True})
    atomic_bytes(target/"README.md",("# "+entity["title"]+"\n\nGenerated navigation, not verified findings. Contents are pinned .ref.json pointers; use library_export for ordinary files.\n").encode())
    return base

def project_item(root: Path, item: dict, entity: dict | None) -> str | None:
    if not entity: return None
    category=item["scope"].get("category") or "reports/collection_inventory"
    # Categories may be extended, but cannot escape their entity.
    target=safe_join(root,entity_base(entity)+"/"+category)
    target.mkdir(parents=True,exist_ok=True)
    name=item["item_id"]+"--"+item["revision_id"]+".ref.json"
    path=target/name
    atomic_json(path,{"item_id":item["item_id"],"revision_id":item["revision_id"],"record":f"_records/items/{item['item_id']}/{item['revision_id']}.json","sha256":item["sha256"]})
    return str(path.relative_to(root))