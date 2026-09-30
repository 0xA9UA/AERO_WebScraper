# MMA FILE SUMMARY
# Purpose: Bounds parser wall time and output without inheriting service secrets.
# Public interface: run_parser; orchestration supplies a verified immutable object.
# Invariants: Does not launch imported programs; kills timed-out trusted parser workers.
from __future__ import annotations
import json, os, subprocess, sys, tempfile
from pathlib import Path

def run_parser(path: Path,name: str,limits: dict) -> dict:
    package_root=str(Path(__file__).resolve().parents[2])
    env={"PYTHONPATH":package_root,"PYTHONIOENCODING":"utf-8","PYTHONNOUSERSITE":"1"}
    if os.name=="nt":
        for key in ["SYSTEMROOT","WINDIR"]:
            if key in os.environ: env[key]=os.environ[key]
    request=json.dumps({"path":str(path),"name":name,"limits":limits}).encode()
    with tempfile.TemporaryDirectory(prefix="aero-parser-") as work:
        try:
            process=subprocess.run([sys.executable,"-m","aero_webscraper.ingestion.worker"],input=request,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=limits["parser_timeout_seconds"],cwd=work,env=env,check=False)
            if process.returncode or len(process.stdout)>16*1024*1024: raise ValueError()
            value=json.loads(process.stdout)
            value["processor"]={"name":"aero-bounded-parser","version":"0.1.0","python":sys.version.split()[0]}
            return value
        except subprocess.TimeoutExpired:
            code="PARSER_TIMEOUT"
        except Exception:
            code="PARSER_PROCESS_FAILED"
    return {"chunks":[],"state":"PARTIAL","warnings":[code],"links":[],"members":[],"processor":{"name":"aero-bounded-parser","version":"0.1.0"}}