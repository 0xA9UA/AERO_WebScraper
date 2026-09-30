# MMA FILE SUMMARY
# Purpose: Tests robots, redirect boundaries and actual HTTP reader bounds without the internet.
# Responsibilities: Deterministic security-contract checks for the production fetcher.
import io, socket, time
import pytest
from aero_webscraper.acquisition.network import SafeFetcher, PinnedHTTPS
from aero_webscraper.domain.identity import AeroError

@pytest.fixture
def fetcher(service,all_rights,monkeypatch):
    service.library.policy.grant("host:fixture.example",all_rights)
    service.library.policy.allow_host("fixture.example")
    monkeypatch.setattr(socket,"getaddrinfo",lambda *a,**k:[(socket.AF_INET,socket.SOCK_STREAM,6,"",("8.8.8.8",443))])
    return SafeFetcher(service.library.policy)

def test_robots_disallow_blocks_page(fetcher,monkeypatch):
    requested=[]
    def fake(url,*args):
        requested.append(url)
        return 200,{},b"User-agent: *\nDisallow: /private\n",{"status":200}
    monkeypatch.setattr(fetcher,"_request",fake)
    with pytest.raises(AeroError,match="ROBOTS_DISALLOWED"): fetcher.fetch("https://fixture.example/private",1024)
    assert requested==["https://fixture.example/robots.txt"]

def test_robots_failure_is_closed(fetcher,monkeypatch):
    monkeypatch.setattr(fetcher,"_request",lambda *a:(503,{},b"",{"status":503}))
    with pytest.raises(AeroError,match="ROBOTS_UNAVAILABLE_OR_DENIED"): fetcher.fetch("https://fixture.example/doc",1024)

def test_redirect_rechecks_allowlist(fetcher,monkeypatch):
    def fake(url,*args):
        if url.endswith("robots.txt"): return 404,{},b"",{"status":404}
        return 302,{"location":"http://169.254.169.254/latest/meta-data/"},b"",{"status":302}
    monkeypatch.setattr(fetcher,"_request",fake)
    with pytest.raises(AeroError,match="HOST_NOT_ALLOWLISTED"): fetcher.fetch("https://fixture.example/doc",1024)

def test_redirect_loop_detected(fetcher,monkeypatch):
    def fake(url,*args):
        if url.endswith("robots.txt"): return 404,{},b"",{"status":404}
        return 302,{"location":"/doc"},b"",{"status":302}
    monkeypatch.setattr(fetcher,"_request",fake)
    with pytest.raises(AeroError,match="REDIRECT_LOOP"): fetcher.fetch("https://fixture.example/doc",1024)

def test_actual_reader_enforces_size_and_pins_ip(fetcher,monkeypatch):
    observed={}
    class Response:
        status=200
        def __init__(self): self.body=io.BytesIO(b"x"*200)
        def getheaders(self): return []
        def read(self,n): return self.body.read(n)
    class Connection:
        def __init__(self,host,port,ip,timeout): observed.update(host=host,ip=ip)
        def request(self,*a,**kw): pass
        def getresponse(self): return Response()
        def close(self): pass
    monkeypatch.setattr("aero_webscraper.acquisition.network.PinnedHTTPS",Connection)
    monkeypatch.setattr(fetcher,"rate_wait",lambda *a:None)
    with pytest.raises(AeroError,match="DOWNLOAD_LIMIT"): fetcher._request("https://fixture.example/doc",50,time.monotonic()+5)
    assert observed=={"host":"fixture.example","ip":"8.8.8.8"}

def test_storage_revocation_blocks_model_access(service,imported):
    item,_=imported; service.library.policy.set_retrieval(True)
    service.library.policy.override(item["item_id"],{"storage":False})
    assert service.call("library_browse",{}).payload["total"]==0

def test_redirect_authority_revocation_blocks_read(service,all_rights):
    from aero_webscraper.domain.models import Scope
    for host in ["one.example","two.example"]: service.library.policy.grant("host:"+host,all_rights)
    service.library.ingest(b"AERO_REDIRECT_TEST", "https://one.example/a.txt", "a.txt",Scope(),requested_url="https://one.example/a.txt",resolved_url="https://two.example/a.txt",source_authority_keys=["https://one.example/a.txt","https://two.example/a.txt"])
    service.library.policy.set_retrieval(True)
    assert service.call("reference_search",{"query":"AERO_REDIRECT_TEST"}).payload["count"]==1
    service.library.policy.grant("host:two.example",all_rights.model_copy(update={"model_transmission":False}))
    assert service.call("reference_search",{"query":"AERO_REDIRECT_TEST"}).payload["count"]==0