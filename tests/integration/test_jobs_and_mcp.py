# MMA FILE SUMMARY
# Purpose: Tests deterministic crawler state transitions and real stdio process negotiation.
# Invariants: HTTP is a synthetic adapter; stdio test launches the actual local backend.
import io, json, os, subprocess, sys
from pathlib import Path
from aero_webscraper.acquisition.network import Fetched
from aero_webscraper.orchestration.jobs import Jobs
from aero_webscraper.domain.models import PlanArgs, RunArgs, StatusArgs
from aero_webscraper.domain.identity import AeroError

class FakeFetcher:
    def __init__(self): self.calls=[]
    def fetch(self,url,max_bytes,deadline=None):
        self.calls.append(url)
        if url.endswith("bad"): raise AeroError("HTTP_STATUS_503")
        data=b'<html><p>AERO_CRAWL_FIXTURE</p><a href="/second">second</a></html>' if url.endswith("first") else b'<html><p>Second synthetic page.</p></html>'
        if len(data)>max_bytes: raise AeroError("DOWNLOAD_LIMIT")
        return Fetched(data,url,url,"text/html",[url],[{"status":200,"bytes":len(data),"requested_url":url}])

def test_resumable_fixture_crawl(service,all_rights):
    service.library.policy.grant("host:fixture.example",all_rights,"CC0-1.0")
    fake=FakeFetcher(); jobs=Jobs(service.library,fake)
    plan=jobs.plan(PlanArgs(target="Nintendo Wii",seeds=["https://fixture.example/first"],max_depth=1))
    one=jobs.run(RunArgs(job_id=plan["job_id"],step_items=1)); assert one["remaining"]==1 and one["state"]=="READY"
    two=Jobs(service.library,fake).run(RunArgs(job_id=plan["job_id"],step_items=1))
    assert two["completed_items"]==2 and two["state"]=="COMPLETED"
    receipt_file=jobs.directory(plan["job_id"])/"search_receipts.jsonl"
    assert len(receipt_file.read_text().splitlines())==2

def test_metadata_only_no_authority(service):
    jobs=Jobs(service.library,FakeFetcher())
    p=jobs.plan(PlanArgs(target="Nintendo Wii",seeds=["https://fixture.example/manual"]))
    out=jobs.run(RunArgs(job_id=p["job_id"]))
    assert out["completed_items"]==1 and out["bytes_acquired"]==0
    assert next(service.library.store.records("items"))["state"]=="METADATA_ONLY"

def test_no_seeds_not_fake_search(service):
    out=service.call("collection_plan",{"target":"Nintendo Wii"})
    assert out["state"]=="NEEDS_SEEDS" and out["seed_count"]==0

def test_failed_fetch_reported(service,all_rights):
    service.library.policy.grant("host:fixture.example",all_rights)
    jobs=Jobs(service.library,FakeFetcher()); p=jobs.plan(PlanArgs(target="Nintendo Wii",seeds=["https://fixture.example/bad"]))
    out=jobs.run(RunArgs(job_id=p["job_id"]))
    assert out["state"]=="PARTIAL" and out["failures"][0]["error"]=="HTTP_STATUS_503"

def test_item_budget(service,all_rights):
    service.library.policy.grant("host:fixture.example",all_rights)
    jobs=Jobs(service.library,FakeFetcher()); p=jobs.plan(PlanArgs(target="Nintendo Wii",seeds=["https://fixture.example/first"],max_items=1))
    jobs.run(RunArgs(job_id=p["job_id"]))
    out=jobs.run(RunArgs(job_id=p["job_id"]))
    assert out["state"]=="BUDGET_EXHAUSTED" and out["completed_items"]==1

def test_stdio_protocol_actual_process(service):
    root=service.library.store.root
    messages=[{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"fixture","version":"1"}}},{"jsonrpc":"2.0","method":"notifications/initialized"},{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}},{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"target_resolve","arguments":{"target":"Nintendo Wii"}}},{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"reference_search","arguments":{"query":"anything"}}}]
    data="\n".join(json.dumps(m) for m in messages)+"\n"
    env=os.environ.copy(); env["PYTHONPATH"]=str(Path(__file__).resolve().parents[2]/"src")
    p=subprocess.run([sys.executable,"-m","aero_webscraper","--root",str(root),"serve"],input=data,text=True,capture_output=True,env=env,timeout=15)
    assert p.returncode==0,p.stderr
    responses=[json.loads(line) for line in p.stdout.splitlines()]
    assert len(responses)==4
    assert responses[0]["result"]["protocolVersion"]=="2025-06-18"
    assert len(responses[1]["result"]["tools"])==11
    assert responses[2]["result"]["structuredContent"]["status"]=="RESOLVED"
    assert responses[3]["result"]["isError"] is True