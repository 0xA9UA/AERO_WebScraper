# MMA FILE SUMMARY
# Purpose: Creates isolated synthetic libraries and explicit fixture-only permissions.
# Public interface: service, imported, all_rights pytest fixtures.
# Invariants: No live scraping and no copyrighted device binaries in tests.
import pytest
from aero_webscraper.catalog.taxonomy import init_library
from aero_webscraper.adapters.service import ToolService
from aero_webscraper.domain.models import Rights

@pytest.fixture
def all_rights(): return Rights(**{k:True for k in Rights.model_fields})

@pytest.fixture
def service(tmp_path,all_rights):
    root=init_library(tmp_path/"AERO_LIBRARY")
    service=ToolService(root)
    service.library.policy.grant("import:inbox",all_rights,"CC0-1.0")
    return service

@pytest.fixture
def imported(service):
    root=service.library.store.root
    (root/"_inbox/manual.md").write_text("# Synthetic console fixture\nAERO_DEMO_Init initializes the synthetic test transport.\nThis is not Nintendo documentation.\n",encoding="utf-8")
    resolved=service.call("target_resolve",{"target":"Nintendo Wii"})
    scope={"entity_id":resolved["entity"]["entity_id"],"platform":"wii","manufacturer":"nintendo","category":"hardware/architecture_overviews"}
    result=service.call("library_import",{"relative_path":"manual.md","scope":scope})
    return result["items"][0],scope