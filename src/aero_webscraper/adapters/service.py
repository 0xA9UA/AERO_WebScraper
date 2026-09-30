# MMA FILE SUMMARY
# Purpose: Declares the eleven typed tools and their actual write boundaries.
# Public interface: ToolService.definitions and call; transport is deliberately separate.
# Invariants: Administrative policy changes are not callable tools; untrusted data is not code.
from __future__ import annotations
from dataclasses import dataclass
from pydantic import ValidationError
from filelock import Timeout
from aero_webscraper.domain import models as m
from aero_webscraper.domain.identity import AeroError
from aero_webscraper.orchestration.library import Library
from aero_webscraper.orchestration.jobs import Jobs
from aero_webscraper.retrieval.references import References
from aero_webscraper.storage.exports import export_items
from aero_webscraper.storage.validation import validate

@dataclass(frozen=True)
class ToolSpec:
    model: type
    description: str
    read_only: bool
    open_world: bool
    idempotent: bool

SPECS={
    "target_resolve":ToolSpec(m.TargetArgs,"Resolve an explicit target identity. Writes entity records and generated navigation; does not verify scientific facts.",False,False,True),
    "collection_plan":ToolSpec(m.PlanArgs,"Create a durable collection plan from explicit seeds. Writes _jobs request/plan/progress. No web search is invented.",False,False,False),
    "collection_run":ToolSpec(m.RunArgs,"Run bounded synchronous crawl steps; resume by calling again. Writes staging, objects, records, indexes, receipts and progress; uses approved public network destinations.",False,True,False),
    "collection_status":ToolSpec(m.StatusArgs,"Read operational job counts, errors, state and report location. No document excerpts are returned.",True,False,True),
    "library_import":ToolSpec(m.ImportArgs,"Import from an operator-authorized local root. Writes originals, versioned records, derived data and pointer navigation. Cannot grant permissions or execute imported programs.",False,False,True),
    "library_browse":ToolSpec(m.BrowseArgs,"Browse scope/access-filtered manifests while retrieval is ON. May rebuild a disposable index; returns untrusted advisory metadata.",False,False,True),
    "reference_search":ToolSpec(m.SearchArgs,"Search lexical text or an exact literal symbol. Scope/access filters precede source-bound excerpts; retrieval must be ON. May rebuild disposable indexes.",False,False,True),
    "reference_read":ToolSpec(m.ReadArgs,"Resolve a pinned item/revision/chunk citation and verify source bytes. Returns untrusted extracted data, not verified findings. Retrieval must be ON.",True,False,True),
    "reference_capture":ToolSpec(m.CaptureArgs,"Explicitly write a cited passage into a pre-authorized AERO intake directory, with provenance. Never edits scientific records; requires retrieval ON.",False,False,True),
    "library_export":ToolSpec(m.ExportArgs,"Write ordinary named file copies and a provenance manifest under _exports. Requires retrieval ON, model-transmission and redistribution permissions.",False,False,False),
    "library_validate":ToolSpec(m.ValidateArgs,"Audit hashes, manifests and citation references; optionally rebuild indexes and generated pointers. Reports counts/errors, not research correctness.",False,False,True),
}

class ToolService:
    def __init__(self,root):
        self.library=Library(root); self.jobs=Jobs(self.library); self.references=References(self.library)
        self.handlers={"target_resolve":self.library.resolve,"collection_plan":self.jobs.plan,"collection_run":self.jobs.run,"collection_status":self.jobs.status,"library_import":self.library.import_path,"library_browse":self.library.index.browse,"reference_search":self.library.index.search,"reference_read":self.references.read,"reference_capture":self.references.capture,"library_export":lambda args:export_items(self.library,args),"library_validate":lambda args:validate(self.library,args.rebuild_index)}

    def definitions(self):
        return [{"name":name,"description":spec.description,"inputSchema":spec.model.model_json_schema(),"outputSchema":{"type":"object"},"annotations":{"readOnlyHint":spec.read_only,"destructiveHint":False,"idempotentHint":spec.idempotent,"openWorldHint":spec.open_world}} for name,spec in SPECS.items()]

    def call(self,name: str,arguments: dict):
        if name not in SPECS: raise AeroError("UNKNOWN_TOOL")
        try: args=SPECS[name].model.model_validate(arguments)
        except ValidationError: raise AeroError("INVALID_TOOL_ARGUMENTS") from None
        try: return self.handlers[name](args)
        except Timeout: raise AeroError("LIBRARY_OR_JOB_BUSY") from None