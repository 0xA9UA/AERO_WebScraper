# MMA FILE SUMMARY
# Purpose: Acquires approved HTTP(S) sources with pinned public-IP connections.
# Public interface: SafeFetcher.fetch; Fetched holds original bytes and receipts.
# Collaborators: Operator Policy, durable host-rate reservations, robots.txt parser.
# Invariants: No proxies/cookies/credentials; revalidate every redirect; fail closed on robots errors.
from __future__ import annotations
from dataclasses import dataclass
import http.client, ipaddress, json, socket, ssl, time
from urllib.parse import urlsplit, urljoin
from urllib.robotparser import RobotFileParser
from aero_webscraper.domain.identity import AeroError, clean_url, utcnow, stable_id
from aero_webscraper.storage.files import atomic_json, read_bounded

@dataclass
class Fetched:
    data: bytes
    requested_url: str
    resolved_url: str
    content_type: str | None
    authorities: list[str]
    receipts: list[dict]

class PinnedHTTPS(http.client.HTTPSConnection):
    def __init__(self,host,port,ip,timeout):
        super().__init__(host,port,timeout=timeout,context=ssl.create_default_context()); self.ip=ip
    def connect(self):
        raw=socket.create_connection((self.ip,self.port),timeout=self.timeout)
        try: self.sock=self._context.wrap_socket(raw,server_hostname=self.host)
        except BaseException: raw.close(); raise

class PinnedHTTP(http.client.HTTPConnection):
    def __init__(self,host,port,ip,timeout): super().__init__(host,port,timeout=timeout); self.ip=ip
    def connect(self): self.sock=socket.create_connection((self.ip,self.port),timeout=self.timeout)

class SafeFetcher:
    user_agent="AERO-WebScraper/0.1 (permission-gated archival reference collector)"
    def __init__(self,policy): self.policy=policy

    def validate(self,url: str) -> tuple[str,list[str]]:
        url=clean_url(url); p=urlsplit(url)
        config=self.policy.read("source_allowlists")
        if p.hostname not in config.get("hosts",[]): raise AeroError("HOST_NOT_ALLOWLISTED")
        if p.scheme=="http" and not config.get("allow_http",False): raise AeroError("PLAINTEXT_HTTP_DISABLED")
        self.policy.require_source(url,"acquisition","storage")
        try:
            addresses=sorted({entry[4][0] for entry in socket.getaddrinfo(p.hostname,p.port or (443 if p.scheme=="https" else 80),type=socket.SOCK_STREAM)})
        except Exception: raise AeroError("DNS_FAILED") from None
        if not addresses or any(not ipaddress.ip_address(addr).is_global for addr in addresses):
            raise AeroError("NON_PUBLIC_DESTINATION")
        return url,addresses

    def rate_wait(self,host: str,deadline: float):
        interval=float(self.policy.read("collection_policies")["rate_interval_seconds"])
        store=self.policy.store
        with store.lock:
            path=store.root/"_jobs/host-rate-reservations.json"
            table=json.loads(read_bounded(path,4*1024*1024)) if path.exists() else {}
            now=time.time(); due=max(now,float(table.get(host,0)))
            table[host]=due+interval
            atomic_json(path,table)
        delay=max(0,due-time.time())
        if time.monotonic()+delay>=deadline: raise AeroError("NETWORK_DEADLINE")
        if delay: time.sleep(delay)

    def _request(self,url: str,limit: int,deadline: float):
        url,addresses=self.validate(url); p=urlsplit(url)
        self.rate_wait(p.hostname,deadline)
        timeout=min(float(self.policy.read("collection_policies")["network_timeout_seconds"]),max(0.1,deadline-time.monotonic()))
        cls=PinnedHTTPS if p.scheme=="https" else PinnedHTTP
        conn=cls(p.hostname,p.port or (443 if p.scheme=="https" else 80),addresses[0],timeout)
        try:
            path=p.path+("?"+p.query if p.query else "")
            conn.request("GET",path,headers={"User-Agent":self.user_agent,"Accept-Encoding":"identity","Connection":"close"})
            response=conn.getresponse()
            headers={k.lower():v for k,v in response.getheaders()}
            if headers.get("content-encoding","").lower() not in {"","identity"}: raise AeroError("ENCODED_RESPONSE_REJECTED")
            if headers.get("content-length"):
                try: declared=int(headers["content-length"])
                except ValueError: raise AeroError("INVALID_CONTENT_LENGTH") from None
                if declared<0 or declared>limit: raise AeroError("DOWNLOAD_LIMIT")
            parts=[]; size=0
            while True:
                if time.monotonic()>=deadline: raise AeroError("NETWORK_DEADLINE")
                part=response.read(min(65536,limit-size+1))
                if not part: break
                size+=len(part)
                if size>limit: raise AeroError("DOWNLOAD_LIMIT")
                parts.append(part)
            receipt={"requested_url":url,"at":utcnow(),"status":response.status,"bytes":size,"transport":"pinned_public_ip_tls" if p.scheme=="https" else "pinned_public_ip_http"}
            return response.status,headers,b"".join(parts),receipt
        except AeroError: raise
        except Exception: raise AeroError("HTTP_TRANSPORT_FAILED") from None
        finally: conn.close()

    def robots(self,url: str,deadline: float,receipts: list):
        p=urlsplit(url); robot_url=f"{p.scheme}://{p.netloc}/robots.txt"
        seen=set()
        for _ in range(4):
            if robot_url in seen: raise AeroError("ROBOTS_REDIRECT_LOOP")
            seen.add(robot_url)
            status,headers,data,receipt=self._request(robot_url,65536,deadline); receipts.append({**receipt,"purpose":"robots"})
            if status in {301,302,303,307,308}:
                if not headers.get("location"): raise AeroError("ROBOTS_REDIRECT_INVALID")
                redirected=clean_url(urljoin(robot_url,headers["location"]))
                if urlsplit(redirected).netloc!=p.netloc: raise AeroError("ROBOTS_CROSS_ORIGIN_REDIRECT")
                robot_url=redirected; continue
            if status==404: return
            if status!=200: raise AeroError("ROBOTS_UNAVAILABLE_OR_DENIED")
            parser=RobotFileParser(); parser.parse(data.decode("utf-8",errors="replace").splitlines())
            if not parser.can_fetch("AERO-WebScraper",url): raise AeroError("ROBOTS_DISALLOWED")
            delay=parser.crawl_delay("AERO-WebScraper")
            request_rate=parser.request_rate("AERO-WebScraper")
            extra=max(float(delay or 0),request_rate.seconds/request_rate.requests if request_rate and request_rate.requests else 0)
            if extra:
                if time.monotonic()+extra>=deadline: raise AeroError("ROBOTS_DELAY_EXCEEDS_BUDGET")
                time.sleep(extra)
            return
        raise AeroError("ROBOTS_REDIRECT_LIMIT")

    def fetch(self,url: str,max_bytes: int,deadline: float | None=None) -> Fetched:
        requested=clean_url(url); current=requested; receipts=[]; authorities=[]; seen=set()
        deadline=deadline or (time.monotonic()+25)
        for _ in range(self.policy.read("collection_policies")["max_redirects"]+1):
            if current in seen: raise AeroError("REDIRECT_LOOP")
            seen.add(current); authorities.append(current)
            self.validate(current)
            self.robots(current,deadline,receipts)
            status,headers,data,receipt=self._request(current,max_bytes,deadline); receipts.append({**receipt,"purpose":"acquisition"})
            if status in {301,302,303,307,308}:
                if not headers.get("location"): raise AeroError("REDIRECT_INVALID")
                current=clean_url(urljoin(current,headers["location"])); continue
            if status!=200: raise AeroError("HTTP_STATUS_"+str(status))
            return Fetched(data,requested,current,headers.get("content-type"),authorities,receipts)
        raise AeroError("REDIRECT_LIMIT")