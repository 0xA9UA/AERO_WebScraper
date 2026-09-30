# MMA FILE SUMMARY
# Purpose: Audits authoritative records, object integrity, pointers, and rebuildability.
# Public interface: validate; results contain counts and error IDs, never source excerpts.
# Invariants: Rebuilds are explicit; validation does not certify research correctness.
from __future__ import annotations
from pathlib import Path
from aero_webscraper.domain.identity import AeroError, digest
from aero_webscraper.domain.models import Item, Occurrence
from aero_webscraper.storage.files import unwrap, read_bounded, safe_join
from aero_webscraper.catalog.taxonomy import materialize_entity, project_item

def validate(library,rebuild_index=False):
    lib=library; errors=[]; counts={"objects":0,"items":0,"occurrences":0,"citations":0,"pointers":0}
    with lib.store.lock:
        for path in (lib.store.root/"_objects/sha256").rglob("*"):
            if not path.is_file(): continue
            counts["objects"]+=1
            try:
                if digest(read_bounded(path,1073741824))!=path.name: raise AeroError("OBJECT_INTEGRITY")
            except AeroError as e: errors.append({"object":path.name,"error":e.code})
        entities={e["entity_id"]:e for e in lib.store.records("entities")}
        for item in lib.store.records("items"):
            counts["items"]+=1
            try:
                Item.model_validate(item)
                if item["sha256"]: lib.store.get_object(item["sha256"])
                for occurrence in item["source_occurrence_ids"]:
                    Occurrence.model_validate(unwrap(lib.store.root/f"_records/source_occurrences/{occurrence}.json")); counts["occurrences"]+=1
                seen=set()
                for chunk in lib.index.chunks_for(item):
                    if chunk["chunk_id"] in seen: raise AeroError("DUPLICATE_CHUNK_ID")
                    seen.add(chunk["chunk_id"])
                    if not chunk.get("anchor") or not isinstance(chunk["text"],str): raise AeroError("INVALID_CITATION")
                    counts["citations"]+=1
                if rebuild_index:
                    entity=entities.get(item["scope"]["entity_id"])
                    if entity:
                        materialize_entity(lib.store.root,entity,f"_records/entities/{entity['entity_id']}.json")
                        project_item(lib.store.root,item,entity)
            except Exception as e:
                errors.append({"item_id":item["item_id"],"error":e.code if isinstance(e,AeroError) else "RECORD_SCHEMA_OR_REFERENCE_ERROR"})
        for prefix in ["devices","games","software_projects","online_services"]:
            for path in (lib.store.root/prefix).rglob("*.ref.json"):
                counts["pointers"]+=1
                try:
                    import json
                    ref=json.loads(read_bounded(path,1048576)); record=unwrap(safe_join(lib.store.root,ref["record"]))
                    if ref.get("sha256") is not None and record.get("sha256")!=ref["sha256"]: raise AeroError("POINTER_SHA_MISMATCH")
                except Exception:
                    errors.append({"pointer":str(path.relative_to(lib.store.root)),"error":"POINTER_INVALID"})
        rebuilt=lib.index.rebuild() if rebuild_index and not errors else None
    return {"library_root":str(lib.store.root),"retrieval_enabled":lib.policy.read("retrieval").get("enabled") is True,"valid":not errors,"counts":counts,"errors":errors,"index_rebuilt":rebuilt,"scientific_correctness_verified":False}