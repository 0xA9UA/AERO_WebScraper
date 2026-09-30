# MMA FILE SUMMARY
# Purpose: Creates bounded snapshots of explicit commits from authorized local Git repos.
# Public interface: snapshot; no checkout, hooks, LFS hydration, or remote Git execution.
# Invariants: Resolves a full commit ID, archives that object, and records its identity.
from __future__ import annotations
import os, re, shutil, subprocess, tempfile, time
from pathlib import Path
from aero_webscraper.domain.identity import AeroError

def bounded_command(command,env,limit,timeout=15):
    with tempfile.TemporaryFile() as output:
        p=subprocess.Popen(command,stdout=output,stderr=subprocess.DEVNULL,env=env,stdin=subprocess.DEVNULL)
        start=time.monotonic()
        try:
            while p.poll() is None:
                if os.fstat(output.fileno()).st_size>limit: raise AeroError("REPOSITORY_SIZE_LIMIT")
                if time.monotonic()-start>timeout: raise AeroError("REPOSITORY_TIMEOUT")
                time.sleep(0.01)
            if p.returncode: raise AeroError("REPOSITORY_COMMAND_FAILED")
            output.seek(0); data=output.read(limit+1)
            if len(data)>limit: raise AeroError("REPOSITORY_SIZE_LIMIT")
            return data
        finally:
            if p.poll() is None: p.kill(); p.wait()

def snapshot(path: Path,revision: str | None,limit: int) -> tuple[bytes,str]:
    if path.is_symlink() or (path/".git").is_symlink() or not (path/".git").is_dir():
        raise AeroError("LOCAL_GIT_DIRECTORY_REQUIRED")
    if revision and not re.fullmatch(r"[0-9a-fA-F]{40}|[0-9a-fA-F]{64}",revision):
        raise AeroError("FULL_COMMIT_ID_REQUIRED")
    git=shutil.which("git")
    if not git: raise AeroError("GIT_NOT_INSTALLED")
    env={"GIT_CONFIG_NOSYSTEM":"1","GIT_CONFIG_GLOBAL":os.devnull,"GIT_TERMINAL_PROMPT":"0","GIT_NO_REPLACE_OBJECTS":"1","LC_ALL":"C"}
    for k in ["SYSTEMROOT","WINDIR"]:
        if k in os.environ: env[k]=os.environ[k]
    base=[git,"--no-pager","--no-replace-objects","-c","core.fsmonitor=false","-c","core.hooksPath="+os.devnull,"-c","core.attributesFile="+os.devnull,"-C",str(path)]
    commit=bounded_command(base+["rev-parse","--verify",(revision or "HEAD")+"^{commit}"],env,256).decode().strip()
    if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}",commit): raise AeroError("INVALID_COMMIT")
    data=bounded_command(base+["archive","--format=tar",commit],env,limit)
    return data,commit