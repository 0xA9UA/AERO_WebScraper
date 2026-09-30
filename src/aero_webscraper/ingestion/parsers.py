# MMA FILE SUMMARY
# Purpose: Parses bounded documents/archives into source-anchored text, never programs.
# Public interface: parse_document, has_secret; run through worker for untrusted inputs.
# Invariants: No archive materialization, recursion, macros, OCR, or binary execution.
from __future__ import annotations
import csv, io, json, re, stat, tarfile, zipfile
from html.parser import HTMLParser
from pathlib import PurePosixPath
from aero_webscraper.domain.identity import AeroError, digest

TEXT_EXT={".txt",".md",".rst",".c",".h",".cpp",".hpp",".py",".rs",".js",".ts",".java",".sh",".asm",".s",".json",".yaml",".yml",".toml",".ini",".cfg",".xml",".csv",".tsv",".log",".patch",".diff"}
SECRET_PATTERNS=[rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",rb"\bAKIA[0-9A-Z]{16}\b",rb"\bgh[pousr]_[A-Za-z0-9]{30,}\b",rb"(?im)^(?:API_KEY|API_TOKEN|PASSWORD|SECRET_KEY)\s*[=:]\s*[^\s]{8,}"]

def has_secret(data: bytes) -> bool:
    return any(re.search(pattern,data) for pattern in SECRET_PATTERNS)

class VisibleHTML(HTMLParser):
    def __init__(self): super().__init__(convert_charrefs=True); self.skip=0; self.parts=[]; self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag in {"script","style","template","noscript"}: self.skip+=1
        if not self.skip:
            if tag in {"p","div","br","li","tr","h1","h2","h3"}: self.parts.append("\n")
            if tag=="a":
                for k,v in attrs:
                    if k=="href" and v and len(v)<4096: self.links.append(v)
    def handle_endtag(self,tag):
        if tag in {"script","style","template","noscript"} and self.skip: self.skip-=1
    def handle_data(self,data):
        if not self.skip: self.parts.append(data)

def chunks(text: str,kind: str,base: dict,limit: int) -> list[dict]:
    text=text[:limit]; result=[]; start=0
    for offset in range(0,len(text),1600):
        fragment=text[offset:offset+1600]
        anchor={"kind":kind,**base,"text_start":offset,"text_end":offset+len(fragment)}
        if kind=="source_text":
            anchor.update({"line_start":text[:offset].count("\n")+1,"line_end":text[:offset+len(fragment)].count("\n")+1})
        result.append({"chunk_id":"chunk-"+digest(json.dumps(anchor,sort_keys=True).encode()+fragment.encode())[:24],"text":fragment,"anchor":anchor})
    return result

def _member_safe(name: str,mode: int=0):
    if not name or "\\" in name or ":" in name or name.startswith("/") or ".." in PurePosixPath(name).parts or "\x00" in name:
        raise AeroError("UNSAFE_ARCHIVE_PATH")
    if stat.S_ISLNK(mode): raise AeroError("ARCHIVE_LINK_REJECTED")

def parse_document(data: bytes,name: str,limits: dict,inside_archive: bool=False) -> dict:
    if has_secret(data): return {"chunks":[],"state":"QUARANTINED","warnings":["POSSIBLE_CREDENTIAL_MATERIAL"],"links":[],"members":[]}
    suffix=PurePosixPath(name.lower()).suffix
    cap=limits["max_text_chars"]
    out={"chunks":[],"state":"STORED_ONLY","warnings":[],"links":[],"members":[]}
    if data.startswith(b"%PDF-"):
        from pypdf import PdfReader
        reader=PdfReader(io.BytesIO(data),strict=False)
        if reader.is_encrypted: return {**out,"warnings":["ENCRYPTED_PDF_NOT_PARSED"]}
        if len(reader.pages)>300: raise AeroError("PDF_PAGE_LIMIT")
        left=cap
        for page_n,page in enumerate(reader.pages,1):
            text=page.extract_text() or ""
            out["chunks"]+=chunks(text,"pdf_page",{"page":page_n,"page_numbering":"physical_1_based"},left)
            if len(text)>left: out["warnings"].append("TEXT_TRUNCATED")
            left-=min(len(text),left)
            if left==0: break
        if not out["chunks"]: out["warnings"].append("OCR_NOT_ENABLED")
    elif data[:4] in {b"PK\x03\x04",b"PK\x05\x06"} or suffix in {".tar",".tgz",".gz"}:
        if inside_archive: return {**out,"warnings":["NESTED_ARCHIVE_NOT_EXPANDED"]}
        entries=[]; total=0
        def accept(filename,payload):
            nonlocal total
            total+=len(payload)
            if total>limits["max_expanded_bytes"]: raise AeroError("ARCHIVE_EXPANSION_LIMIT")
            if has_secret(payload): raise AeroError("ARCHIVE_POSSIBLE_CREDENTIAL_MATERIAL")
            child=parse_document(payload,filename,limits,True)
            if child["state"]=="QUARANTINED": raise AeroError("ARCHIVE_POSSIBLE_CREDENTIAL_MATERIAL")
            out["members"].append({"path":filename,"sha256":digest(payload),"size":len(payload),"state":child["state"]})
            for chunk in child["chunks"]:
                chunk["anchor"]={"kind":"archive_member","member_path":filename,"member_sha256":digest(payload),"inner_anchor":chunk["anchor"]}
                chunk["chunk_id"]="chunk-"+digest(json.dumps(chunk["anchor"],sort_keys=True).encode()+chunk["text"].encode())[:24]
                out["chunks"].append(chunk)
            out["warnings"].extend(child["warnings"])
        if zipfile.is_zipfile(io.BytesIO(data)):
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                infos=z.infolist()
                if len(infos)>limits["max_archive_files"]: raise AeroError("ARCHIVE_MEMBER_LIMIT")
                for info in infos:
                    _member_safe(info.filename,info.external_attr>>16)
                    if info.is_dir(): continue
                    if info.flag_bits&1: raise AeroError("ENCRYPTED_ARCHIVE")
                    if info.file_size>limits["max_expanded_bytes"]-total: raise AeroError("ARCHIVE_EXPANSION_LIMIT")
                    if info.file_size>max(1024,info.compress_size)*100: raise AeroError("ARCHIVE_RATIO_LIMIT")
                    with z.open(info) as f: payload=f.read(limits["max_expanded_bytes"]-total+1)
                    accept(info.filename,payload)
        else:
            with tarfile.open(fileobj=io.BytesIO(data),mode="r:*") as archive:
                for n,info in enumerate(archive,1):
                    if n>limits["max_archive_files"]: raise AeroError("ARCHIVE_MEMBER_LIMIT")
                    _member_safe(info.name)
                    if info.isdir(): continue
                    if not info.isfile(): raise AeroError("ARCHIVE_SPECIAL_FILE_REJECTED")
                    if info.size>limits["max_expanded_bytes"]-total: raise AeroError("ARCHIVE_EXPANSION_LIMIT")
                    member=archive.extractfile(info)
                    if member is None: raise AeroError("ARCHIVE_MEMBER_ERROR")
                    accept(info.name,member.read(limits["max_expanded_bytes"]-total+1))
        text_total=sum(len(c["text"]) for c in out["chunks"])
        if text_total>cap:
            kept=[]; remaining=cap
            for chunk in out["chunks"]:
                if len(chunk["text"])>remaining: break
                kept.append(chunk); remaining-=len(chunk["text"])
            out["chunks"]=kept; out["warnings"].append("TEXT_TRUNCATED")
    elif suffix in {".html",".htm"} or data.lstrip()[:15].lower().startswith((b"<!doctype html",b"<html")):
        text=data.decode("utf-8",errors="replace")
        parser=VisibleHTML(); parser.feed(text)
        visible="".join(parser.parts)
        out["chunks"]=chunks(visible,"extracted_text",{"format":"html","offset_basis":"extracted_unicode_text"},cap)
        out["links"]=parser.links[:1000]
        if len(visible)>cap: out["warnings"].append("TEXT_TRUNCATED")
    elif suffix in TEXT_EXT or (b"\x00" not in data[:4096] and name.upper() in {"README","LICENSE","COPYING","MAKEFILE"}):
        try: text=data.decode("utf-8")
        except UnicodeDecodeError: return {**out,"warnings":["UNSUPPORTED_TEXT_ENCODING"]}
        out["chunks"]=chunks(text,"source_text",{"encoding":"utf-8","offset_basis":"unicode_characters"},cap)
        if len(text)>cap: out["warnings"].append("TEXT_TRUNCATED")
    else:
        out["warnings"].append("OPAQUE_BYTES_RETAINED_NO_EXECUTION")
    if any(has_secret(c["text"].encode()) for c in out["chunks"]):
        return {**out,"chunks":[],"state":"QUARANTINED","warnings":["POSSIBLE_CREDENTIAL_MATERIAL"],"links":[]}
    out["warnings"]=sorted(set(out["warnings"]))
    if out["chunks"]: out["state"]="PARTIAL" if out["warnings"] else "INDEXED"
    return out