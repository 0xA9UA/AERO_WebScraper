# MMA FILE SUMMARY
# Purpose: Provides local operator setup, approvals, retrieval switching and tool invocation.
# Public interface: main; installed command aero-webscraper.
# Invariants: Policy administration is never exposed through MCP; no secrets in command output.
from __future__ import annotations
import argparse, json, os, sys
from pathlib import Path
from aero_webscraper.domain.identity import AeroError
from aero_webscraper.domain.models import Rights
from aero_webscraper.catalog.taxonomy import init_library
from aero_webscraper.retrieval.policy import Delivery
from aero_webscraper.adapters.service import ToolService

def main(argv=None):
    parser=argparse.ArgumentParser(prog="aero-webscraper")
    parser.add_argument("--root",default=os.environ.get("AERO_LIBRARY_ROOT",str(Path.home()/".local/share/aero/AERO_LIBRARY")))
    sub=parser.add_subparsers(dest="command",required=True)
    sub.add_parser("init")
    gate=sub.add_parser("retrieval"); gate.add_argument("value",choices=["on","off"])
    grant=sub.add_parser("grant"); grant.add_argument("source"); grant.add_argument("--rights",required=True,help="Comma-separated rights; unspecified rights are denied"); grant.add_argument("--license",default=None)
    revoke=sub.add_parser("revoke"); revoke.add_argument("item_id"); revoke.add_argument("--right",choices=list(Rights.model_fields),default="model_transmission")
    host=sub.add_parser("allow-host"); host.add_argument("host")
    rootarg=sub.add_parser("add-root"); rootarg.add_argument("name"); rootarg.add_argument("path"); rootarg.add_argument("--kind",choices=["imports","intakes"],default="imports")
    call=sub.add_parser("call"); call.add_argument("tool"); call.add_argument("--json",default="{}")
    sub.add_parser("tools"); sub.add_parser("serve")
    args=parser.parse_args(argv)
    if "${" in args.root: parser.error("Host did not expand the persistent data location")
    root=Path(args.root).expanduser().resolve()
    try:
        if args.command=="init": result={"root":str(init_library(root)),"retrieval":"OFF unless already configured"}; print(json.dumps(result,indent=2)); return 0
        if args.command=="serve":
            init_library(root)
            from aero_webscraper.adapters.mcp_stdio import serve
            serve(root); return 0
        service=ToolService(root); policy=service.library.policy
        if args.command=="retrieval": result=policy.set_retrieval(args.value=="on")
        elif args.command=="grant":
            wanted=set(filter(None,args.rights.split(",")))
            if not wanted.issubset(Rights.model_fields): raise AeroError("UNKNOWN_PERMISSION")
            rights=Rights(**{k:k in wanted for k in Rights.model_fields})
            policy.grant(args.source,rights,args.license); result={"source":args.source,"rights":rights.model_dump(),"updated":True}
        elif args.command=="revoke": policy.override(args.item_id,{args.right:False}); result={"item_id":args.item_id,"revoked":args.right}
        elif args.command=="allow-host": policy.allow_host(args.host); result={"host":args.host,"allowlisted":True,"acquisition_rights_granted":False}
        elif args.command=="add-root": policy.configure_root(args.name,args.path,args.kind); result={"name":args.name,"kind":args.kind,"configured":True}
        elif args.command=="tools": result={"tools":service.definitions()}
        else:
            try: arguments=json.loads(args.json)
            except Exception: raise AeroError("INVALID_JSON_ARGUMENTS") from None
            result=service.call(args.tool,arguments)
        with service.library.store.lock:
            if isinstance(result,Delivery): result=policy.authorize(result)
            print(json.dumps(result,indent=2,ensure_ascii=False))
        return 0
    except AeroError as e:
        print(json.dumps({"error":e.code}),file=sys.stderr); return 2

if __name__=="__main__": raise SystemExit(main())