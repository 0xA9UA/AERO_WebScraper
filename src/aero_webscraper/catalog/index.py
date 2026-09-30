# MMA FILE SUMMARY
# Purpose: Builds replaceable lexical/exact-symbol indexes from pinned source records.
# Public interface: Index.ensure, rebuild, browse, search, chunks_for.
# Collaborators: Store verifies bytes; Policy filters scope and permissions before matches.
# Invariants: Indexes never establish correctness; permission checks precede returned excerpts.
from __future__ import annotations
import json, os, re, sqlite3, uuid
from aero_webscraper.domain.identity import AeroError, canonical
from aero_webscraper.storage.files import unwrap

class Index:
    def __init__(self,store,policy): self.store=store; self.policy=policy; self.path=store.root/"_indexes/catalog.sqlite"

    def chunks_for(self,item):
        if not item.get("processing_run_id"): return []
        p=self.store.root/f"_derived/{item['item_id']}/{item['processing_run_id']}/chunks.ref.json"
        ref=unwrap(p)
        return json.loads(self.store.get_object(ref["sha256"]))

    def rebuild(self) -> dict:
        with self.store.lock:
            tmp=self.path.with_name("catalog-"+uuid.uuid4().hex+".sqlite")
            c=sqlite3.connect(tmp)
            counts={"items":0,"chunks":0}
            try:
                c.executescript("CREATE TABLE items(item_id TEXT,revision_id TEXT,acquired TEXT,record TEXT,PRIMARY KEY(item_id,revision_id)); CREATE TABLE chunks(item_id TEXT,revision_id TEXT,chunk_id TEXT,text TEXT,anchor TEXT);")
                for item in self.store.records("items"):
                    c.execute("INSERT INTO items VALUES(?,?,?,?)",(item["item_id"],item["revision_id"],item["first_acquired_at"],json.dumps(item)))
                    counts["items"]+=1
                    rights=self.policy.rights(item["source_key"],item["item_id"])
                    if rights.indexing is True and item["state"] in {"INDEXED","PARTIAL"}:
                        for chunk in self.chunks_for(item):
                            c.execute("INSERT INTO chunks VALUES(?,?,?,?,?)",(item["item_id"],item["revision_id"],chunk["chunk_id"],chunk["text"],json.dumps(chunk["anchor"])))
                            counts["chunks"]+=1
                c.commit(); c.close(); os.replace(tmp,self.path)
                dirty=self.store.root/"_indexes/dirty"
                if dirty.exists(): dirty.unlink()
            finally:
                try: c.close()
                except Exception: pass
                if tmp.exists(): tmp.unlink()
            return counts

    def ensure(self):
        if not self.path.exists() or (self.store.root/"_indexes/dirty").exists(): self.rebuild()

    @staticmethod
    def scope_matches(item,scope):
        for k,v in scope.model_dump().items():
            if v is None or v==[]: continue
            actual=item["scope"].get(k)
            if k=="related_entities":
                if not set(v).issubset(actual or []): return False
            elif actual!=v: return False
        return True

    def candidates(self,scope,include_history=False):
        self.ensure()
        c=sqlite3.connect(self.path)
        try:
            rows=c.execute("SELECT record FROM items ORDER BY acquired DESC,revision_id DESC").fetchall()
        finally: c.close()
        seen=set(); result=[]
        for (raw,) in rows:
            indexed=json.loads(raw)
            # Authoritative manifest is reread; stale index permissions are never trusted.
            item=self.store.item(indexed["item_id"],indexed["revision_id"])
            if not self.scope_matches(item,scope): continue
            identity=(item["item_id"],canonical(item["scope"]))
            if not include_history and identity in seen: continue
            seen.add(identity)
            if self.policy.allowed(item): result.append(item)
        return result

    def browse(self,args):
        with self.store.lock:
            self.policy.snapshot()
            candidates=self.candidates(args.scope,args.include_history)
            selected=candidates[args.offset:args.offset+args.limit]
            return self.policy.make_delivery({"items":selected,"total":len(candidates),"next_offset":args.offset+len(selected) if args.offset+len(selected)<len(candidates) else None,"advisory":True},[(x["item_id"],x["revision_id"]) for x in selected])

    def search(self,args):
        with self.store.lock:
            self.policy.snapshot()
            allowed=self.candidates(args.scope,True)
            results=[]; needle=args.query if args.mode=="exact" else args.query.casefold()
            tokens=re.findall(r"[\w]+",needle)
            for item in allowed:
                if item.get("sha256"): self.store.get_object(item["sha256"])
                if self.policy.rights(item["source_key"],item["item_id"]).indexing is not True: continue
                for chunk in self.chunks_for(item):
                    text=chunk["text"] if args.mode=="exact" else chunk["text"].casefold()
                    match=needle in text if args.mode=="exact" else bool(tokens) and all(t in text for t in tokens)
                    if match:
                        results.append({"item_id":item["item_id"],"revision_id":item["revision_id"],"chunk_id":chunk["chunk_id"],"excerpt":chunk["text"],"anchor":chunk["anchor"],"sha256":item["sha256"],"source_key":item["source_key"],"source_occurrence_ids":item["source_occurrence_ids"],"scope":item["scope"],"warnings":item["warnings"],"state":item["state"],"license":item["license"],"citation":f"aero://{item['item_id']}/{item['revision_id']}#{chunk['chunk_id']}","advisory":True})
                        if len(results)>=args.limit: break
                if len(results)>=args.limit: break
            return self.policy.make_delivery({"results":results,"count":len(results),"search_backend":"lexical-literal-v1","semantic_search":False},[(x["item_id"],x["revision_id"]) for x in results])