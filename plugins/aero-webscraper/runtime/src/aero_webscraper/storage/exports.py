# MMA FILE SUMMARY
# Purpose: Creates policy-filtered portable exports containing ordinary named files.
# Public interface: export_items; objects are copied, never linked or made writable.
# Invariants: Retrieval and redistribution are rechecked under the shared policy lock.
from __future__ import annotations
import uuid
from pathlib import Path
from aero_webscraper.domain.identity import safe_filename, AeroError
from aero_webscraper.storage.files import atomic_bytes, atomic_json

def export_items(library,args):
    lib=library
    with lib.store.lock:
        lib.policy.snapshot()
        permitted=[]; skipped=[]
        for ref in args.items:
            item=lib.store.item(ref.item_id,ref.revision_id)
            if not lib.policy.allowed(item,redistribution=True) or not item.get("sha256"):
                skipped.append({"item_id":ref.item_id,"revision_id":ref.revision_id,"reason":"NOT_EXPORTABLE"})
            else: permitted.append(item)
        export_id="export-"+uuid.uuid4().hex
        root=lib.store.root/"_exports"/export_id; root.mkdir(parents=True)
        files=[]; pairs=[]
        for item in permitted:
            original=safe_filename(item["original_filename"] or "file.bin")
            p=Path(original)
            name=f"{p.stem}--{item['item_id'][-10:]}--{item['revision_id'][-8:]}{p.suffix}"
            data=lib.store.get_object(item["sha256"])
            atomic_bytes(root/name,data)
            files.append({"filename":name,"item_id":item["item_id"],"revision_id":item["revision_id"],"sha256":item["sha256"],"source_key":item["source_key"],"license":item["license"],"source_occurrence_ids":item["source_occurrence_ids"],"scope":item["scope"]})
            pairs.append((item["item_id"],item["revision_id"]))
        atomic_json(root/"manifest.json",{"export_id":export_id,"files":files,"skipped":skipped,"advisory":True})
        return lib.policy.make_delivery({"export_id":export_id,"location":str(root),"count":len(files),"files":files,"skipped":skipped},pairs,redistribution=True)