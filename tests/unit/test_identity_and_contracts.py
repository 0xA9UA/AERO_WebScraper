# MMA FILE SUMMARY
# Purpose: Tests deterministic identity, strict tool inputs, taxonomy and version scope.
# Responsibilities: Fast domain/contract regression coverage with no network.
import json, pytest
from aero_webscraper.domain.identity import stable_id, slug, safe_filename, clean_url, AeroError
from aero_webscraper.domain.models import Scope
from aero_webscraper.catalog.taxonomy import taxonomy

@pytest.mark.parametrize("bad",["file:///etc/passwd","http://u:p@example.org/a","https://example.org:22/x","https://example.org/x?api_key=secret","https://example.org/\nInjected"])
def test_unsafe_url_rejected(bad):
    with pytest.raises(AeroError): clean_url(bad)

def test_ids_are_stable():
    assert stable_id("item","a")==stable_id("item","a")
    assert stable_id("item","a")!=stable_id("item","b")

def test_filename_portable():
    assert safe_filename("../../CON")=="unnamed-file"
    assert "/" not in safe_filename("a/b.txt")

def test_all_eleven_tools_typed(service):
    definitions=service.definitions()
    assert len(definitions)==11
    for tool in definitions:
        assert tool["inputSchema"]["type"]=="object"
        assert tool["inputSchema"].get("additionalProperties") is False
        assert "readOnlyHint" in tool["annotations"]

def test_cannot_smuggle_permission_grant(service):
    with pytest.raises(AeroError,match="INVALID_TOOL_ARGUMENTS"):
        service.call("library_import",{"relative_path":"x","rights":{"storage":True}})

def test_unknown_target_not_invented(service):
    assert service.call("target_resolve",{"target":"Ambiguous hardware"})["status"]=="UNRESOLVED"

def test_taxonomy_preserved():
    t=taxonomy()
    assert "system_firmware/components/<component_id>/releases/<release_key>" in t["console"]
    assert "releases/<release_id>/multiplayer_service_refs" in t["game"]
    assert "_records/source_occurrences" in t["library"]
    assert "dated_availability_observations" in t["online_service"]

def test_distinct_version_coordinates():
    s=Scope(system_version="4.3",component_version="60",game_edition="special",game_build="1")
    assert s.system_version!=s.component_version
    assert s.hardware_revision is None