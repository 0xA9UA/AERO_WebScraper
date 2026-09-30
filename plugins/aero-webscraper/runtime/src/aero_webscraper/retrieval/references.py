# MMA FILE SUMMARY
# Purpose: Resolves cited passages and performs explicit, provenance-preserving intake.
# Public interface: References.read and capture.
# Invariants: Captures write only to pre-authorized intake roots, never scientific records.
from __future__ import annotations
import json
from pathlib import Path
from aero_webscraper.domain.identity import AeroError, stable_id, canonical
from aero_webscraper.storage.files import atomic_json, safe_join

class References:
    def __init__(self,library): self.library=library

    def read(self,args):
        lib=self.library
        with lib.store.lock:
            lib.policy.snapshot()
            item=lib.store.item(args.item_id,args.revision_id)
            if not lib.policy.allowed(item): raise AeroError("ITEM_PERMISSION_DENIED")
            if lib.policy.rights(item["source_key"],item["item_id"]).indexing is not True:
                raise AeroError("INDEX_PERMISSION_DENIED")
            if item["sha256"]: lib.store.get_object(item["sha256"])
            chunk=next((c for c in lib.index.chunks_for(item) if c["chunk_id"]==args.chunk_id),None)
            if chunk is None: raise AeroError("CITATION_NOT_FOUND")
            payload={"item_id":item["item_id"],"revision_id":item["revision_id"],**chunk,"original_sha256":item["sha256"],"source_key":item["source_key"],"source_occurrence_ids":item["source_occurrence_ids"],"processing_run_id":item["processing_run_id"],"citation":f"aero://{item['item_id']}/{item['revision_id']}#{chunk['chunk_id']}","role":"extracted","source_role":item["role"],"scope":item["scope"],"publication_date":item["publication_date"],"warnings":item["warnings"],"advisory":True,"instruction_trust":"untrusted_source_data"}
            return lib.policy.make_delivery(payload,[(item["item_id"],item["revision_id"])])

    def capture(self,args):
        lib=self.library
        with lib.store.lock:
            roots=lib.policy.read("permissions")["intakes"]
            if args.intake not in roots: raise AeroError("INTAKE_NOT_AUTHORIZED")
            delivery=self.read(args)
            payload=lib.policy.authorize(delivery)
            capture_id=stable_id("capture",payload["citation"]+":"+args.intake)
            path=safe_join(Path(roots[args.intake]),capture_id+".reference.json")
            atomic_json(path,{"capture_id":capture_id,"role":"advisory_reference_intake","scientific_record_modified":False,"reference":payload})
            return lib.policy.make_delivery({"capture_id":capture_id,"location":str(path),"scientific_record_modified":False},delivery.items)