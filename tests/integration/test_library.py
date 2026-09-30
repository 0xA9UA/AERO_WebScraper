# MMA FILE SUMMARY
# Purpose: Exercises end-to-end import, retrieval, citation, export, repository and rebuild flows.
# Invariants: All device claims and bytes in these tests are deliberately synthetic.
import io, json, os, shutil, subprocess, zipfile
from pathlib import Path
import pytest
from aero_webscraper.domain.identity import AeroError, digest
from aero_webscraper.retrieval.policy import Delivery
from aero_webscraper.storage.files import unwrap, atomic_json

def test_idempotent_import(service,imported):
    old,scope=imported
    repeat=service.call("library_import",{"relative_path":"manual.md","scope":scope})
    assert repeat["idempotent"] is True
    assert repeat["items"][0]["revision_id"]==old["revision_id"]
    assert len(list(service.library.store.records("items")))==1

def test_changed_bytes_new_revision(service,imported):
    old,scope=imported
    (service.library.store.root/"_inbox/manual.md").write_text("A different synthetic build")
    new=service.call("library_import",{"relative_path":"manual.md","scope":scope})["items"][0]
    assert old["item_id"]==new["item_id"] and old["revision_id"]!=new["revision_id"]
    assert service.library.store.get_object(old["sha256"]).startswith(b"# Synthetic")

def test_scope_version_new_revision(service,imported):
    old,scope=imported
    for region,system,component in [("US","4.3","60"),("EU","4.3","60"),("EU","4.3","61")]:
        service.call("library_import",{"relative_path":"manual.md","scope":scope|{"region":region,"system_version":system,"component_version":component}})
    items=list(service.library.store.records("items"))
    assert len(items)==4 and len({x["revision_id"] for x in items})==4

def test_same_bytes_dedup_preserves_occurrences(service,imported):
    old,scope=imported; root=service.library.store.root
    shutil.copyfile(root/"_inbox/manual.md",root/"_inbox/mirror.md")
    new=service.call("library_import",{"relative_path":"mirror.md","scope":scope})["items"][0]
    assert old["sha256"]==new["sha256"] and old["item_id"]!=new["item_id"]
    assert len(list(service.library.store.records("source_occurrences")))==2
    assert len(list((root/"_objects/sha256").rglob(old["sha256"])))==1

def test_cited_read_exact_symbol(service,imported):
    service.library.policy.set_retrieval(True)
    delivery=service.call("reference_search",{"query":"AERO_DEMO_Init","mode":"exact"})
    result=delivery.payload["results"][0]
    read=service.call("reference_read",{k:result[k] for k in ["item_id","revision_id","chunk_id"]})
    assert read.payload["text"]==result["excerpt"]
    assert read.payload["anchor"]["kind"]=="source_text"
    assert read.payload["advisory"] is True

def test_search_scope_filter(service,imported):
    service.library.policy.set_retrieval(True)
    assert service.call("reference_search",{"query":"AERO_DEMO_Init","scope":{"platform":"ps3"}}).payload["count"]==0

def test_export_named_copies_not_aliases(service,imported):
    receipt,scope=imported; service.library.policy.set_retrieval(True)
    exported=service.call("library_export",{"items":[{"item_id":receipt["item_id"],"revision_id":receipt["revision_id"]}]})
    result=exported.payload; assert result["count"]==1
    copied=Path(result["location"])/result["files"][0]["filename"]
    assert copied.suffix==".md"
    assert digest(copied.read_bytes())==receipt["sha256"]
    copied.write_text("modified export copy")
    assert digest(service.library.store.get_object(receipt["sha256"]))==receipt["sha256"]

def test_export_denies_redistribution(service,imported):
    item,_=imported; service.library.policy.set_retrieval(True)
    service.library.policy.override(item["item_id"],{"redistribution":False})
    out=service.call("library_export",{"items":[{k:item[k] for k in ["item_id","revision_id"]}]}).payload
    assert out["count"]==0 and len(out["skipped"])==1

def test_explicit_capture_intake_only(service,imported,tmp_path):
    service.library.policy.set_retrieval(True)
    result=service.call("reference_search",{"query":"AERO_DEMO_Init"}).payload["results"][0]
    args={k:result[k] for k in ["item_id","revision_id","chunk_id"]}|{"intake":"aero-intake"}
    with pytest.raises(AeroError,match="INTAKE_NOT_AUTHORIZED"): service.call("reference_capture",args)
    intake=tmp_path/"aero-workspace/reference-intake"; intake.mkdir(parents=True)
    service.library.policy.configure_root("aero-intake",intake,"intakes")
    capture=service.call("reference_capture",args).payload
    assert Path(capture["location"]).parent==intake
    assert capture["scientific_record_modified"] is False
    assert json.loads(Path(capture["location"]).read_text())["reference"]["original_sha256"]==imported[0]["sha256"]

def test_opaque_binary_stored_not_run(service,tmp_path):
    root=service.library.store.root
    (root/"_inbox/sample.bin").write_bytes(b"\x7fELF\x00AERO synthetic bytes only\x00")
    result=service.call("library_import",{"relative_path":"sample.bin"})["items"][0]
    assert result["state"]=="STORED_ONLY"
    assert "OPAQUE_BYTES_RETAINED_NO_EXECUTION" in result["warnings"]

def test_repository_commit_snapshot(service):
    if not shutil.which("git"): pytest.skip("git not installed")
    root=service.library.store.root; repo=root/"_inbox/synthetic-repo"; repo.mkdir()
    (repo/"README.md").write_text("CC0 synthetic fixture, not actual device code")
    (repo/"demo.c").write_text("/* Synthetic fixture */\nint AERO_DEMO_Init(void) { return 42; }\n")
    def git(*args): return subprocess.check_output(["git","-C",str(repo),*args],stderr=subprocess.DEVNULL).decode().strip()
    git("init"); git("add","."); git("-c","user.name=AERO Fixture","-c","user.email=fixture@example.invalid","commit","-m","Synthetic fixture")
    commit=git("rev-parse","HEAD")
    result=service.call("library_import",{"relative_path":"synthetic-repo","kind":"repository"})
    assert result["repository_commit"]==commit
    record=service.library.store.item(result["items"][0]["item_id"],result["items"][0]["revision_id"])
    assert record["repository_revision"]==commit
    service.library.policy.set_retrieval(True)
    found=service.call("reference_search",{"query":"return 42","mode":"exact"}).payload["results"]
    assert any(x["anchor"]["kind"]=="archive_member" for x in found)

def test_pdf_physical_page_anchor(service):
    from reportlab.pdfgen.canvas import Canvas
    p=service.library.store.root/"_inbox/synthetic.pdf"
    c=Canvas(str(p)); c.drawString(72,720,"Synthetic fixture page one. Not hardware evidence."); c.showPage(); c.drawString(72,720,"AERO_PDF_PageTwo citation fixture."); c.save()
    result=service.call("library_import",{"relative_path":"synthetic.pdf"})
    assert result["items"][0]["state"]=="INDEXED"
    service.library.policy.set_retrieval(True)
    found=service.call("reference_search",{"query":"AERO_PDF_PageTwo","mode":"exact"}).payload["results"][0]
    assert found["anchor"]["kind"]=="pdf_page" and found["anchor"]["page"]==2

def test_delete_index_rebuild_from_authority(service,imported):
    service.library.policy.set_retrieval(True)
    before=service.call("reference_search",{"query":"AERO_DEMO_Init"}).payload
    service.library.index.path.unlink()
    after=service.call("reference_search",{"query":"AERO_DEMO_Init"}).payload
    assert before==after
    assert service.call("library_validate",{"rebuild_index":True})["valid"] is True

def test_html_visible_text_only(service):
    p=service.library.store.root/"_inbox/page.html"
    p.write_text('<html><script>DO_NOT_INDEX_123</script><p>Visible AERO_HTML_Test</p><a href="/next">next</a></html>')
    service.call("library_import",{"relative_path":"page.html"}); service.library.policy.set_retrieval(True)
    assert service.call("reference_search",{"query":"DO_NOT_INDEX_123"}).payload["count"]==0
    assert service.call("reference_search",{"query":"AERO_HTML_Test"}).payload["count"]==1

def test_folder_import(service):
    p=service.library.store.root/"_inbox/folder"; p.mkdir()
    (p/"first.txt").write_text("alpha"); (p/"second.txt").write_text("beta")
    result=service.call("library_import",{"relative_path":"folder","kind":"folder"})
    assert result["count"]==2 and not result["failures"]