# MMA FILE SUMMARY
# Purpose: Verifies release metadata, literal case matching, and reported-discovery provenance.
# Invariants: Tests use synthetic owned fixtures and make no network requests.
import json
from aero_webscraper.storage.files import unwrap

def test_source_role_and_date_roundtrip(service, imported):
    _, scope = imported
    result = service.call("library_import", {"relative_path":"manual.md", "scope":scope,
        "publication_date":"2026-09-30", "provenance_role":"model-generated"})["items"][0]
    record = service.library.store.item(result["item_id"], result["revision_id"])
    assert record["role"] == "model-generated" and record["publication_date"] == "2026-09-30"
    assert record["original_filename"] == "manual.md"
    occurrence = unwrap(service.library.store.root / ("_records/source_occurrences/" + record["source_occurrence_ids"][0] + ".json"))
    assert occurrence["publication_date"] == "2026-09-30"

def test_exact_symbol_is_case_sensitive(service, imported):
    service.library.policy.set_retrieval(True)
    assert service.call("reference_search", {"query":"aero_demo_init", "mode":"exact"}).payload["count"] == 0
    assert service.call("reference_search", {"query":"aero_demo_init", "mode":"lexical"}).payload["count"] == 1

def test_discovery_receipts_are_attributed_not_claimed_verified(service):
    result = service.call("collection_plan", {"target":"Nintendo Wii", "seeds":[],
        "discovery_receipts":[{"provider":"synthetic-operator", "query":"fixture", "returned_urls":["https://fixture.example/manual"]}]})
    path = service.library.store.root / "_jobs" / result["job_id"] / "search_receipts.jsonl"
    receipt = json.loads(path.read_text().strip())
    assert receipt["verified_by_backend"] is False
    assert receipt["provenance"] == "agent_or_operator_reported"
    assert result["state"] == "NEEDS_SEEDS"
    assert list(service.library.store.records("collections"))

def test_validate_exposes_operator_root_not_library_excerpts(service):
    result = service.call("library_validate", {})
    assert result["library_root"] == str(service.library.store.root)
    assert result["retrieval_enabled"] is False and result["valid"] is True