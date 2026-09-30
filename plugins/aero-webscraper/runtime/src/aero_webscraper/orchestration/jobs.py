# MMA FILE SUMMARY
# Purpose: Persists bounded, resumable seed-crawl plans and honest collection receipts.
# Public interface: Jobs.plan, run, status; calls perform work synchronously in bounded steps.
# Collaborators: Library handles all ingestion; SafeFetcher alone performs network I/O.
# Invariants: No invented discovery, no detached execution, no unbounded retries or crawling.
from __future__ import annotations
import json, time, uuid
from pathlib import Path
from urllib.parse import urljoin,urlsplit
from filelock import FileLock
from aero_webscraper.domain.models import TargetArgs, Scope
from aero_webscraper.domain.identity import AeroError, clean_url, utcnow, check_id, safe_filename, stable_id, canonical, digest
from aero_webscraper.storage.files import atomic_json, atomic_bytes, read_bounded
from aero_webscraper.catalog.taxonomy import taxonomy
from aero_webscraper.acquisition.network import SafeFetcher

class Jobs:
    def __init__(self,library,fetcher=None): self.lib=library; self.fetcher=fetcher or SafeFetcher(library.policy)

    def directory(self,job_id):
        root=self.lib.store.root/"_jobs"/check_id(job_id)
        if not (root/"request.json").is_file(): raise AeroError("JOB_NOT_FOUND")
        return root

    @staticmethod
    def read(root,name): return json.loads(read_bounded(root/name,16*1024*1024))

    def plan(self,args):
        seeds=list(dict.fromkeys(clean_url(url) for url in args.seeds))
        scope=args.scope.model_copy(deep=True)
        if not scope.entity_id:
            result=self.lib.resolve(TargetArgs(target=args.target,platform=scope.platform,manufacturer=scope.manufacturer))
            if result["status"]=="RESOLVED":
                entity=result["entity"]; scope.entity_id=entity["entity_id"]; scope.platform=entity["platform"]; scope.manufacturer=entity["manufacturer"]
        else: self.lib.entity(scope.entity_id)
        jid="job-"+uuid.uuid4().hex; root=self.lib.store.root/"_jobs"/jid; root.mkdir()
        categories=sorted({p.split("/")[0] for p in taxonomy()["console"] if "." not in p.split("/")[0]})
        request=args.model_dump(); request["scope"]=scope.model_dump()
        plan={"job_id":jid,"scope":scope.model_dump(),"categories":categories,"discovery":"operator_or_agent_supplied_seeds_then_same_origin_links","search_engine_api_required":False,"seeds":seeds,"budgets":{"max_items":args.max_items,"max_bytes":args.max_bytes,"max_depth":args.max_depth}}
        progress={"job_id":jid,"state":"READY" if seeds and scope.entity_id else "NEEDS_SEEDS" if scope.entity_id else "NEEDS_TARGET","queue":[{"url":u,"depth":0} for u in seeds],"inflight":None,"done":[],"attempted":0,"bytes_acquired":0,"elapsed_seconds":0,"request_count":0,"failures":[],"discovered":len(seeds),"started_at":utcnow()}
        for name,value in [("request.json",request),("plan.json",plan),("progress.json",progress)]: atomic_json(root/name,value)
        discovery=[]
        for reported in args.discovery_receipts:
            row=reported.model_dump()
            row["returned_urls"]=[clean_url(u) for u in row["returned_urls"]]
            from aero_webscraper.ingestion.parsers import has_secret
            if has_secret(canonical(row)): raise AeroError("SENSITIVE_DISCOVERY_RECEIPT")
            discovery.append({"kind":"discovery","verified_by_backend":False,"provenance":"agent_or_operator_reported",**row})
        atomic_bytes(root/"search_receipts.jsonl",b"".join(canonical(row)+b"\n" for row in discovery))
        collection_id=stable_id("collection",jid)
        self.lib.store.commit({f"_records/collections/{collection_id}/plan.json":{"collection_id":collection_id,"job_id":jid,"role":"collection_plan","plan":plan}})
        atomic_bytes(root/"report.md",b"# Collection report\n\nNo acquisition has run. Supplied URLs are seeds, not evidence of completed search.\n")
        return {"job_id":jid,"state":progress["state"],"plan_location":str(root/"plan.json"),"seed_count":len(seeds),"budgets":plan["budgets"],"unresolved_category_count":len(categories)}

    def status(self,args):
        root=self.directory(args.job_id); p=self.read(root,"progress.json")
        result={k:p[k] for k in ["job_id","state","attempted","bytes_acquired","elapsed_seconds","request_count","discovered"]}|{"completed_items":len(p["done"]),"remaining":len(p["queue"]),"inflight":p["inflight"] is not None,"report_location":str(root/"report.md")}
        result["failures"]=[{k:v for k,v in x.items() if k!="url"} for x in p["failures"]]
        return result

    def run(self,args):
        root=self.directory(args.job_id)
        with FileLock(str(root/"job.lock"),timeout=1):
            progress=self.read(root,"progress.json"); plan=self.read(root,"plan.json"); scope=Scope.model_validate(plan["scope"])
            limits=self.lib.policy.read("collection_policies"); budgets=plan["budgets"]
            if not scope.entity_id: return {"job_id":args.job_id,"state":"NEEDS_TARGET","completed_items":0}
            if progress["inflight"]:
                # A crash can replay ingestion, whose stable identity makes replay idempotent.
                progress["queue"].insert(0,progress["inflight"]); progress["inflight"]=None
            if args.retry_failed:
                retriable=[x for x in progress["failures"] if x.get("url")]
                progress["queue"].extend({"url":x["url"],"depth":x.get("depth",0)} for x in retriable)
                progress["failures"]=[]
            began=time.monotonic(); count=0
            for _ in range(args.step_items):
                if not progress["queue"]: break
                if len(progress["done"])>=budgets["max_items"] or progress["bytes_acquired"]>=budgets["max_bytes"] or progress["elapsed_seconds"]>=limits["max_job_seconds"] or progress["request_count"]>=limits["max_job_requests"]:
                    progress["state"]="BUDGET_EXHAUSTED"; break
                entry=progress["queue"].pop(0); url=entry["url"]; progress["inflight"]=entry; progress["attempted"]+=1
                atomic_json(root/"progress.json",progress)
                receipt={"kind":"acquisition_attempt","source_id":stable_id("source",url),"requested_url":url,"at":utcnow(),"depth":entry["depth"]}
                try:
                    rights=self.lib.policy.rights(url)
                    if rights.acquisition is not True or rights.storage is not True:
                        result=self.lib.metadata_only(url,safe_filename(Path(urlsplit(url).path).name or "reference.html"),scope)
                        receipt.update({"state":"METADATA_ONLY","reason":"SOURCE_AUTHORITY_UNRESOLVED"})
                    else:
                        available=min(limits["max_file_bytes"],budgets["max_bytes"]-progress["bytes_acquired"])
                        fetched=self.fetcher.fetch(url,available,deadline=time.monotonic()+25)
                        progress["bytes_acquired"]+=len(fetched.data); progress["request_count"]+=len(fetched.receipts)
                        name=safe_filename(Path(urlsplit(fetched.resolved_url).path).name or "index.html")
                        if "." not in name and fetched.content_type and "html" in fetched.content_type: name+=".html"
                        result=self.lib.ingest(fetched.data,url,name,scope,requested_url=url,resolved_url=fetched.resolved_url,source_authority_keys=fetched.authorities)
                        receipt.update({"state":result["item"]["state"],"bytes":len(fetched.data),"resolved_url":fetched.resolved_url,"requests":fetched.receipts})
                        if entry["depth"]<budgets["max_depth"]:
                            known={x["url"] for x in progress["queue"]}|{x["source"] for x in progress["done"]}|{url}
                            for link in result["links"]:
                                try: candidate=clean_url(urljoin(fetched.resolved_url,link))
                                except AeroError: continue
                                if urlsplit(candidate).netloc!=urlsplit(fetched.resolved_url).netloc or candidate in known: continue
                                if len(known)>=budgets["max_items"]*5: break
                                known.add(candidate); progress["queue"].append({"url":candidate,"depth":entry["depth"]+1}); progress["discovered"]+=1
                    receipt["item_id"]=result["item"]["item_id"]; receipt["revision_id"]=result["item"]["revision_id"]
                    progress["done"].append({"source":url,**self.lib.receipt(result["item"])}); count+=1
                except AeroError as e:
                    receipt.update({"state":"FAILED","error":e.code})
                    progress["failures"].append({"source_id":stable_id("source",url),"url":url,"depth":entry["depth"],"error":e.code})
                    progress["request_count"]+=1
                finally:
                    with open(root/"search_receipts.jsonl","ab") as f:
                        f.write(json.dumps(receipt,sort_keys=True).encode()+b"\n"); f.flush()
                        import os; os.fsync(f.fileno())
                    progress["inflight"]=None
                    now=time.monotonic(); progress["elapsed_seconds"]+=now-began; began=now
                    atomic_json(root/"progress.json",progress)
            if progress["state"]!="BUDGET_EXHAUSTED": progress["state"]="PARTIAL" if progress["failures"] and not progress["queue"] else "COMPLETED" if not progress["queue"] else "READY"
            atomic_json(root/"progress.json",progress)
            lines=["# Collection report","",f"Job: {args.job_id}",f"State: {progress['state']}",f"Acquired or metadata-only item receipts: {len(progress['done'])}",f"Failures: {len(progress['failures'])}",f"Queue remaining: {len(progress['queue'])}","","## Unresolved coverage","No category is certified complete. Discovery uses supplied seeds and bounded links, not an exhaustive web search.","","## Category review checklist"]
            lines.extend("- "+cat+": review required" for cat in plan["categories"])
            lines.extend(["","## Result receipts",*['- '+x['item_id']+' / '+x['revision_id']+': '+x['state'] for x in progress['done']],"","## Failures",*['- '+x['source_id']+': '+x['error'] for x in progress['failures']]])
            atomic_bytes(root/"report.md",("\n".join(lines)+"\n").encode())
            collection_id=stable_id("collection",args.job_id)
            snapshot={"collection_id":collection_id,"job_id":args.job_id,"state":progress["state"],"scope":scope.model_dump(),"items":[{"item_id":i["item_id"],"revision_id":i["revision_id"],"state":i["state"]} for i in progress["done"]],"bytes_acquired":progress["bytes_acquired"],"failure_count":len(progress["failures"]),"scientific_completion_asserted":False}
            revision=digest(canonical(snapshot))[:32]
            self.lib.store.commit({f"_records/collections/{collection_id}/{revision}.json":snapshot})
            result=self.status(args); result["processed_this_call"]=count
            # Failure URLs remain in operator logs, not unrestricted tool responses.
            result["failures"]=[{k:v for k,v in x.items() if k!="url"} for x in result["failures"]]
            return result