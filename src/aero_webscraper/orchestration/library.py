# MMA FILE SUMMARY
# Purpose: Coordinates provenance-preserving import and target identity, not retrieval UI.
# Public interface: Library.resolve, import_path, ingest, metadata_only; store/policy/index.
# Collaborators: CAS storage, bounded parsers, taxonomy projections, repository adapter.
# Invariants: Tool callers cannot grant rights; originals and scientific workspaces stay separate.
from __future__ import annotations
import json, mimetypes, os
from pathlib import Path
from urllib.parse import quote
from aero_webscraper.domain.models import Item, Occurrence, Scope, TargetArgs, ImportArgs
from aero_webscraper.domain.identity import AeroError, canonical, digest, stable_id, slug, utcnow, safe_filename, check_id
from aero_webscraper.storage.store import Store
from aero_webscraper.storage.files import atomic_json, atomic_bytes, read_bounded, safe_join, unwrap, read_import
from aero_webscraper.retrieval.policy import Policy
from aero_webscraper.catalog.index import Index
from aero_webscraper.catalog.taxonomy import materialize_entity, project_item
from aero_webscraper.ingestion.runner import run_parser
from aero_webscraper.ingestion.parsers import has_secret
from aero_webscraper.acquisition.repository import snapshot

class Library:
    def __init__(self,root: Path):
        self.store=Store(root); self.policy=Policy(self.store); self.index=Index(self.store,self.policy)

    def entity(self,entity_id: str | None):
        if not entity_id: return None
        path=self.store.root/"_records/entities"/(check_id(entity_id)+".json")
        if not path.is_file(): raise AeroError("ENTITY_NOT_FOUND")
        return unwrap(path)

    def resolve(self,args: TargetArgs) -> dict:
        platform=args.platform; manufacturer=args.manufacturer; title=args.target
        normalized=" ".join(args.target.casefold().strip(" .").split())
        if not platform and normalized in {"wii","nintendo wii","document the nintendo wii system","document nintendo wii","nintendo wii system"}:
            platform="wii"; manufacturer="nintendo"; title="Nintendo Wii"
        if not platform or (args.kind in {"game_console","peripheral"} and not manufacturer):
            return {"status":"UNRESOLVED","required":["explicit platform/project identifier","manufacturer for console/peripheral"],"no_collection_started":True}
        eid=stable_id("entity",args.kind+":"+(manufacturer or "")+":"+platform)
        path=self.store.root/"_records/entities"/(eid+".json")
        with self.store.lock:
            if path.exists(): entity=unwrap(path)
            else:
                entity={"schema_version":"1.0.0","entity_id":eid,"kind":args.kind,"platform":slug(platform),"manufacturer":slug(manufacturer) if manufacturer else None,"console_class":args.console_class,"title":title,"identity_basis":"operator_requested","verified_finding":False}
                self.store.commit({str(path.relative_to(self.store.root)):entity})
            base=materialize_entity(self.store.root,entity,str(path.relative_to(self.store.root)))
        return {"status":"RESOLVED","entity":entity,"library_path":base,"identity_verification":"not established"}

    @staticmethod
    def receipt(item: dict) -> dict:
        return {"item_id":item["item_id"],"revision_id":item["revision_id"],"state":item["state"],"size":item["size"],"sha256":item["sha256"],"record_location":f"_records/items/{item['item_id']}/{item['revision_id']}.json","warnings":item["warnings"]}

    def ingest(self,data: bytes | None,source: str,name: str,scope: Scope,requested_url=None,resolved_url=None,repository_revision=None,revision_verification=None,source_authority_keys=None,title=None,metadata_state="METADATA_ONLY",publication_date=None,provenance_role="original") -> dict:
        limits=self.policy.read("collection_policies")
        if data is not None and len(data)>limits["max_file_bytes"]: raise AeroError("FILE_LIMIT")
        entity=self.entity(scope.entity_id)
        # A category is validated even for records that do not yet have an entity projection.
        if scope.category: safe_join(self.store.root/"_staging",scope.category)
        rights=self.policy.rights(source)
        authorities=source_authority_keys or [source]
        if data is not None:
            for authority in authorities: self.policy.require_source(authority,"acquisition","storage")
        sha=digest(data) if data is not None else None
        original_name=name
        name=safe_filename(name)
        item_id=stable_id("item",source)
        fingerprint={"sha256":sha,"scope":scope.model_dump(),"repository_revision":repository_revision,"name":name,"parser":"0.1.0","metadata_state":metadata_state if data is None else None,"resolved_url":resolved_url,"authorities":authorities,"publication_date":publication_date,"title":title,"provenance_role":provenance_role}
        revision_id="rev-"+digest(canonical(fingerprint))[:32]
        occurrence_id=stable_id("occurrence",source+":"+revision_id+":"+(resolved_url or ""))
        now=utcnow()
        path=self.store.item_path(item_id,revision_id)
        with self.store.lock:
            if path.exists():
                existing=self.store.item(item_id,revision_id)
                if sha: self.store.get_object(sha,limits["max_file_bytes"])
                return {"item":existing,"idempotent":True,"links":[]}
        warnings=[]; processing=None; parsed={"links":[]}; writes={}
        state=metadata_state
        if data is not None:
            stage=self.store.root/"_staging"/stable_id("import",source+":"+revision_id)
            stage.mkdir(parents=True,exist_ok=True)
            atomic_bytes(stage/"original.part",data)
            self.store.put_object(data)
            state="STORED_ONLY"
            if has_secret(data): state="QUARANTINED"; warnings=["POSSIBLE_CREDENTIAL_MATERIAL"]
            elif rights.analysis is True and rights.indexing is True:
                parsed=run_parser(self.store.object_path(sha),name,limits)
                state=parsed["state"]; warnings=parsed["warnings"]
                run_id=stable_id("run",item_id+":"+revision_id)
                processing={"schema_version":"1.0.0","processing_run_id":run_id,"item_id":item_id,"revision_id":revision_id,"parent_objects":[sha],"tool":parsed["processor"],"role":"extracted","warnings":warnings,"state":state,"citation_coordinate_systems":"per-chunk; never binary virtual addresses"}
                chunks_sha=self.store.put_object(canonical(parsed["chunks"]))
                text_sha=self.store.put_object("\n".join(c["text"] for c in parsed["chunks"]).encode())
                manifest={**processing,"chunks_object":chunks_sha,"text_object":text_sha,"members":parsed.get("members",[])}
                writes[f"_records/processing_runs/{run_id}.json"]=processing
                prefix=f"_derived/{item_id}/{run_id}"
                writes[prefix+"/extraction_manifest.json"]=manifest
                writes[prefix+"/chunks.ref.json"]={"sha256":chunks_sha,"parent_sha256":sha,"role":"extracted"}
                writes[prefix+"/text.ref.json"]={"sha256":text_sha,"parent_sha256":sha,"role":"extracted"}
                for output in ["tables","page_images","code_analysis"]:
                    writes[prefix+f"/{output}.ref.json"]={"sha256":None,"state":"NOT_PRODUCED","reason":"optional dedicated analysis not enabled"}
            else: warnings=["ANALYSIS_OR_INDEXING_NOT_AUTHORIZED"]
        version=scope.component_version or scope.system_version or repository_revision
        release_id=stable_id("release",canonical({"entity_id":scope.entity_id,"platform":scope.platform,"component_id":scope.component_id,"version":version,"region":scope.region,"game_edition":scope.game_edition,"game_build":scope.game_build,"unattributed_sha256":sha if version is None else None}).decode())
        item=Item(item_id=item_id,revision_id=revision_id,title=title or name,original_filename=original_name,publication_date=publication_date,role=provenance_role,media_type=mimetypes.guess_type(name)[0],size=len(data) if data is not None else None,sha256=sha,source_key=source,source_occurrence_ids=[occurrence_id],scope=scope,license=self.policy.source_rule(source).get("license"),permissions_at_acquisition=rights,state=state,processing_run_id=processing["processing_run_id"] if processing else None,warnings=warnings,first_acquired_at=now,original_version=version,release_key=slug(version or "unknown")+"--"+release_id,repository_revision=repository_revision,repository_revision_verification=revision_verification).model_dump()
        item["source_authority_keys"]=authorities
        occurrence=Occurrence(occurrence_id=occurrence_id,item_id=item_id,revision_id=revision_id,source_key=source,requested_url=requested_url,resolved_url=resolved_url,acquired_at=now,publication_date=publication_date,repository_revision=repository_revision,sha256=sha).model_dump()
        writes[f"_records/items/{item_id}/{revision_id}.json"]=item
        writes[f"_records/source_occurrences/{occurrence_id}.json"]=occurrence
        if entity:
            rel_id=stable_id("relation",item_id+":"+revision_id+":"+entity["entity_id"])
            writes[f"_records/relations/{rel_id}.json"]={"relation_id":rel_id,"subject":item_id,"subject_revision":revision_id,"predicate":"reported_applicability","object":entity["entity_id"],"confidence":None,"verified":False}
        with self.store.lock:
            # Concurrent collectors may have completed this exact acquisition while parsing.
            if path.exists(): return {"item":self.store.item(item_id,revision_id),"idempotent":True,"links":[]}
            for authority in authorities:
                if data is not None: self.policy.require_source(authority,"acquisition","storage")
            self.store.commit(writes)
            if state=="QUARANTINED":
                atomic_json(self.store.root/f"_quarantine/{item_id}--{revision_id}.ref.json",{"record":f"_records/items/{item_id}/{revision_id}.json","access":"operator-only","indexed":False})
            project_item(self.store.root,item,entity)
            if data is not None:
                staged=stage/"original.part"
                if staged.exists(): staged.unlink()
                if stage.exists() and not any(stage.iterdir()): stage.rmdir()
        self.index.ensure()
        return {"item":item,"idempotent":False,"links":parsed.get("links",[])}

    def metadata_only(self,source: str,name: str,scope: Scope,state="METADATA_ONLY"):
        return self.ingest(None,source,name,scope,requested_url=source if source.startswith("http") else None,metadata_state=state)

    def import_path(self,args: ImportArgs) -> dict:
        imports=self.policy.read("permissions")["imports"]
        if args.import_root not in imports: raise AeroError("IMPORT_ROOT_NOT_AUTHORIZED")
        root=Path(imports[args.import_root]); path=safe_join(root,args.relative_path)
        limits=self.policy.read("collection_policies")
        source="import://"+args.import_root+"/"+quote(args.relative_path,safe="/")
        self.policy.require_source(source,"acquisition","storage")
        if args.kind=="repository":
            data,commit=snapshot(path,args.repository_revision,limits["max_file_bytes"])
            result=self.ingest(data,source,path.name+"--"+commit[:12]+".tar",args.scope,repository_revision=commit,revision_verification="git_rev_parse_and_git_archive_same_commit",title=args.title,publication_date=args.publication_date,provenance_role=args.provenance_role)
            return {"count":1,"items":[self.receipt(result["item"])],"idempotent":result["idempotent"],"repository_commit":commit}
        if args.kind=="file":
            data=read_import(root,args.relative_path,limits["max_file_bytes"])
            result=self.ingest(data,source,path.name,args.scope,title=args.title,publication_date=args.publication_date,provenance_role=args.provenance_role)
            return {"count":1,"items":[self.receipt(result["item"])],"idempotent":result["idempotent"]}
        if not path.is_dir(): raise AeroError("FOLDER_REQUIRED")
        files=[]; total=0
        for base,dirs,names in os.walk(path,followlinks=False):
            if any((Path(base)/d).is_symlink() for d in dirs): raise AeroError("SYMLINK_REJECTED")
            dirs[:]=sorted(d for d in dirs if d not in {".git","node_modules",".venv","__pycache__"})
            for name in sorted(names):
                file=Path(base)/name
                if file.is_symlink(): raise AeroError("SYMLINK_REJECTED")
                files.append(file)
                if len(files)>limits["max_folder_files"]: raise AeroError("FOLDER_FILE_LIMIT")
        receipts=[]; failures=[]
        for file in files:
            rel=file.relative_to(root).as_posix()
            try:
                data=read_import(root,rel,limits["max_file_bytes"])
                total+=len(data)
                if total>limits["max_folder_bytes"]: raise AeroError("FOLDER_BYTE_LIMIT")
                result=self.ingest(data,"import://"+args.import_root+"/"+quote(rel,safe="/"),file.name,args.scope)
                receipts.append(self.receipt(result["item"]))
            except AeroError as e:
                failures.append({"input_id":stable_id("input",rel),"error":e.code})
                if e.code=="FOLDER_BYTE_LIMIT": break
        return {"count":len(receipts),"items":receipts,"failures":failures,"state":"PARTIAL" if failures else "COMPLETED","bytes_read":total}