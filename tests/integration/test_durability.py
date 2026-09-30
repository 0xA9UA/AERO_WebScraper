# MMA FILE SUMMARY
# Purpose: Fault-injects redo commits and checks concurrent import idempotence.
# Responsibilities: Thread/process concurrency and authoritative-record recovery tests.
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing
import pytest
from aero_webscraper.domain.identity import AeroError
from aero_webscraper.storage.store import Store
from aero_webscraper.storage.files import unwrap
from aero_webscraper.adapters.service import ToolService

def import_in_process(root):
    return ToolService(root).call("library_import",{"relative_path":"parallel.md"})

@pytest.mark.parametrize("fail_after",[0,1])
def test_interrupted_journal_recovery(service,fail_after):
    store=service.library.store
    writes={"_records/entities/entity-test-a.json":{"entity_id":"entity-test-a"},"_records/entities/entity-test-b.json":{"entity_id":"entity-test-b"}}
    with pytest.raises(AeroError,match="INJECTED_INTERRUPTION"): store.commit(writes,fail_after=fail_after)
    recovered=Store(store.root)
    assert not list((store.root/"_journal").glob("*.pending.json"))
    assert len(list(recovered.records("entities")))==2

def test_concurrent_identical_imports(service):
    root=service.library.store.root
    (root/"_inbox/parallel.md").write_text("AERO concurrent synthetic fixture")
    with ThreadPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(lambda _:import_in_process(root),range(4)))
    assert len({r["items"][0]["revision_id"] for r in results})==1
    assert len(list(service.library.store.records("items")))==1

def test_process_concurrent_imports(service):
    root=service.library.store.root
    (root/"_inbox/parallel.md").write_text("AERO process synthetic fixture")
    with ProcessPoolExecutor(max_workers=2,mp_context=multiprocessing.get_context("spawn")) as pool:
        results=list(pool.map(import_in_process,[root,root]))
    assert results[0]["items"][0]["revision_id"]==results[1]["items"][0]["revision_id"]
    assert len(list(service.library.store.records("items")))==1

def test_immutable_record_conflict(service):
    s=service.library.store
    s.commit({"_records/entities/entity-c.json":{"x":1}})
    with pytest.raises(AeroError,match="IMMUTABLE_RECORD_CONFLICT"):
        s.commit({"_records/entities/entity-c.json":{"x":2}})