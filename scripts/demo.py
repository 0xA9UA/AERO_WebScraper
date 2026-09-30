# MMA FILE SUMMARY
# Purpose: Reproduces a complete library workflow using only synthetic, explicitly labeled fixtures.
# Public interface: python scripts/demo.py --output NEW_DIRECTORY.
# Collaborators: ToolService runs real import, citation, intake, export, and validation operations.
# Invariants: Refuses existing output directories; never connects to the internet or real AERO records.
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from aero_webscraper.adapters.service import ToolService
from aero_webscraper.catalog.taxonomy import init_library
from aero_webscraper.domain.identity import AeroError
from aero_webscraper.domain.models import Rights
from aero_webscraper.retrieval.policy import Delivery


def run_demo(output: Path) -> dict:
    output = output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=False)
    root = init_library(output / 'AERO_LIBRARY')
    service = ToolService(root)
    policy = service.library.policy
    policy.grant('import:inbox', Rights(**{k: True for k in Rights.model_fields}), 'CC0-1.0')

    def call(name, args):
        result = service.call(name, args)
        with service.library.store.lock:
            return policy.authorize(result) if isinstance(result, Delivery) else result

    entity = call('target_resolve', {'target': 'Nintendo Wii', 'console_class': 'home'})['entity']
    scope = {'entity_id': entity['entity_id'], 'platform': 'wii', 'manufacturer': 'nintendo',
             'category': 'hardware/architecture_overviews'}
    inbox = root / '_inbox'
    (inbox / 'synthetic-manual.md').write_text(
        '# Synthetic AERO demonstration\n\nNot Nintendo documentation or hardware evidence.\n'
        'AERO_DEMO_Init initializes a fictional test transport.\n'
        'License: CC0-1.0. Created only to test this library.\n', encoding='utf-8')
    document = call('library_import', {'relative_path': 'synthetic-manual.md', 'scope': scope,
            'provenance_role': 'model-generated', 'publication_date': '2026-09-30'})['items'][0]
    (inbox / 'inert-sample.bin').write_bytes(b'AERO_SYNTHETIC_BINARY\x00\x01\x02\x03NOT_FIRMWARE_NOT_EXECUTABLE\x00')
    binary = call('library_import', {'relative_path': 'inert-sample.bin',
        'scope': scope | {'category': 'system_firmware/unknown_or_unattributed'},
        'provenance_role': 'model-generated'})['items'][0]
    assert binary['state'] == 'STORED_ONLY'

    repo = inbox / 'synthetic-project'; repo.mkdir()
    (repo / 'README.md').write_text('# Synthetic repository\nNot actual Wii code. CC0-1.0.\n')
    (repo / 'demo.c').write_text('/* MMA FILE SUMMARY\n * Purpose: Provides a fictional symbol for source-search testing.\n'
        ' * Public interface: AERO_DEMO_Init.\n * Invariants: Synthetic only; this demo never builds or executes it.\n */\n'
        'int AERO_DEMO_Init(void) { return 42; }\n')
    env = os.environ.copy()
    env.update({'GIT_AUTHOR_DATE':'2026-09-30T00:00:00+00:00', 'GIT_COMMITTER_DATE':'2026-09-30T00:00:00+00:00'})
    def git(*args):
        return subprocess.check_output(['git', '-C', str(repo), *args], stderr=subprocess.DEVNULL, env=env).decode().strip()
    git('init'); git('add', '.')
    git('-c','user.name=AERO Synthetic Fixture','-c','user.email=fixture@example.invalid','commit','-m','Synthetic test fixture')
    commit = git('rev-parse','HEAD')
    snapshot = call('library_import', {'relative_path':'synthetic-project', 'kind':'repository',
        'repository_revision':commit, 'provenance_role':'model-generated',
        'scope':scope | {'category':'sdks_and_toolchains/community_sdks'}})
    assert snapshot['repository_commit'] == commit

    from reportlab.pdfgen.canvas import Canvas
    pdf = inbox / 'synthetic-pages.pdf'
    canvas = Canvas(str(pdf), pagesize=(612,792), invariant=1)
    canvas.setTitle('Synthetic AERO citation fixture - not device evidence')
    for page, line in [(1, 'Synthetic PDF page one. Not Nintendo documentation.'),
                       (2, 'AERO_PDF_PageTwo is a fictional citation test marker.')]:
        canvas.setFont('Helvetica-Bold',18); canvas.drawString(54,730,'AERO / Synthetic citation fixture')
        canvas.setFont('Helvetica',11); canvas.drawString(54,693,line)
        canvas.drawString(54,672,'CC0-1.0. Generated solely to validate physical-page citations.')
        canvas.setFont('Helvetica',9); canvas.drawString(54,45,f'Physical page {page} / 2')
        canvas.showPage()
    canvas.save()
    pdf_item = call('library_import',{'relative_path':'synthetic-pages.pdf', 'scope':scope,
                                     'provenance_role':'model-generated'})['items'][0]
    policy.set_retrieval(True)
    search = call('reference_search',{'query':'AERO_DEMO_Init','mode':'exact'})
    citation = next(x for x in search['results'] if x['item_id'] == document['item_id'])
    pointer = {k:citation[k] for k in ('item_id','revision_id','chunk_id')}
    passage = call('reference_read', pointer)
    page_result = call('reference_search',{'query':'AERO_PDF_PageTwo','mode':'exact'})['results'][0]
    assert page_result['anchor']['page'] == 2
    intake = output / 'ACTIVE_AERO/reference-intake'; intake.mkdir(parents=True)
    policy.configure_root('demo-intake',intake,'intakes')
    captured = call('reference_capture',pointer | {'intake':'demo-intake'})
    records = [document, snapshot['items'][0], binary, pdf_item]
    exported = call('library_export',{'items':[{k:i[k] for k in ('item_id','revision_id')} for i in records]})
    assert exported['count'] == 4
    pending = service.call('reference_search',{'query':'AERO_DEMO_Init','mode':'exact'})
    gate = policy.set_retrieval(False)
    blocked = {}
    for label, operation in [('new_search', lambda:call('reference_search',{'query':'AERO_DEMO_Init'})),
                             ('queued_result',lambda:policy.authorize(pending))]:
        try:
            operation()
            raise AssertionError('Retrieval OFF did not block ' + label)
        except AeroError as error:
            blocked[label] = error.code
            assert error.code == 'RETRIEVAL_OFF'
    validation = call('library_validate',{'rebuild_index':True})
    assert validation['valid'] is True
    report = {'fixture_only':True,'live_network_tested':False,'device_evidence':False,
        'library_root':str(root),'entity_id':entity['entity_id'],'imports':records,
        'repository_commit':commit,'citation':citation['citation'],'cited_passage':passage,
        'pdf_page_anchor':page_result['anchor'],'advisory_capture':captured,
        'export':exported,'retrieval_at_end':gate,'retrieval_off_checks':blocked,'validation':validation}
    (output / 'demo-report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True,help='New directory; never an existing library')
    args = parser.parse_args()
    try:
        report = run_demo(args.output)
    except FileExistsError:
        parser.error('Output already exists; choose a fresh directory.')
    print(json.dumps({'demo_report':str(args.output.resolve()/'demo-report.json'),
        'export':report['export']['location'],'imported_items':len(report['imports']),
        'validation_passed':report['validation']['valid'],'retrieval_enabled':False},indent=2))

if __name__ == '__main__':
    main()