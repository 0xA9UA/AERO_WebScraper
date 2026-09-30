# MMA FILE SUMMARY
# Purpose: Executes trusted parsers in a bounded child process over untrusted bytes.
# Public interface: main; invoked only by ingestion.runner.
# Invariants: No input is executed; worker has no configured network access or credentials.
import json, os, sys

def main():
    request=json.loads(sys.stdin.buffer.read(32768))
    if os.name=="posix":
        import resource
        resource.setrlimit(resource.RLIMIT_CPU,(8,8))
        resource.setrlimit(resource.RLIMIT_AS,(768*1024*1024,768*1024*1024))
        resource.setrlimit(resource.RLIMIT_FSIZE,(64*1024*1024,64*1024*1024))
        resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    # This is a process boundary, not a security sandbox against parser RCE.
    from aero_webscraper.ingestion.parsers import parse_document
    from aero_webscraper.domain.identity import AeroError
    from aero_webscraper.storage.files import read_bounded
    from pathlib import Path
    try:
        data=read_bounded(Path(request["path"]),request["limits"]["max_file_bytes"])
        result=parse_document(data,request["name"],request["limits"])
    except AeroError as e:
        result={"chunks":[],"state":"QUARANTINED","warnings":[e.code],"links":[],"members":[]}
    except ImportError:
        result={"chunks":[],"state":"STORED_ONLY","warnings":["OPTIONAL_PARSER_MISSING"],"links":[],"members":[]}
    except Exception:
        result={"chunks":[],"state":"PARTIAL","warnings":["PARSER_FAILED"],"links":[],"members":[]}
    sys.stdout.write(json.dumps(result))

if __name__=="__main__": main()