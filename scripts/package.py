# MMA FILE SUMMARY
# Purpose: Builds and checks the private plugin and source archives from canonical source.
# Public interface: python scripts/package.py --output DIRECTORY; --smoke tests packaged stdio.
# Collaborators: Canonical src, plugin manifests, tool/record schemas, and Python subprocess.
# Invariants: Excludes corpus, caches, symlinks, credentials and installed dependencies.
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'plugins/aero-webscraper'
EXCLUDED = {'__pycache__','.pytest_cache','.git','.venv','venv','node_modules','.DS_Store'}


def files_under(root: Path):
    for path in sorted(root.rglob('*')):
        if any(part in EXCLUDED for part in path.relative_to(root).parts):
            continue
        if path.is_symlink():
            raise ValueError(f'Symlink forbidden: {path}')
        if path.is_file() and path.suffix not in {'.pyc','.pyo'}:
            yield path


def copy_runtime():
    runtime = PLUGIN / 'runtime'
    runtime.mkdir(exist_ok=True)
    if (runtime / 'src').exists():
        shutil.rmtree(runtime / 'src')
    for source in files_under(ROOT / 'src'):
        target = runtime / 'src' / source.relative_to(ROOT / 'src')
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,target)
    shutil.copyfile(ROOT / 'pyproject.toml',runtime / 'pyproject.toml')
    (runtime / 'launch.py').write_text('''# MMA FILE SUMMARY
# Purpose: Starts the packaged local MCP backend using its bundled canonical source copy.
# Public interface: python runtime/launch.py; AERO_LIBRARY_ROOT selects persistent storage.
# Invariants: Protocol stdout belongs to the backend; no dependency download or imported execution.
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from aero_webscraper.adapters.cli import main
if __name__ == "__main__":
    raise SystemExit(main(["serve"]))
''',encoding='utf-8')
    (runtime / 'README.md').write_text('# Generated runtime copy\n\nRegenerate with `scripts/package.py`; edit canonical source, not this copy.\n'
        'Install this directory into the Python interpreter used by your MCP host.\n'
        'Persistent library data must remain outside the package.\n')


def validate_package():
    manifest = json.loads((PLUGIN / 'plugin.json').read_text())
    allowed = {'$schema','name','version','description','author','homepage','repository','license','keywords','extensions'}
    assert set(manifest).issubset(allowed)
    assert manifest['$schema'] == 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json'
    assert manifest['name'] == PLUGIN.name
    assert len(manifest['name']) <= 64 and re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',manifest['name'])
    assert re.fullmatch(r'\d+\.\d+\.\d+',manifest['version'])
    interface = manifest['extensions']['com.openai']['interface']
    assert len(interface['shortDescription']) <= 30
    skills = []
    for path in sorted((PLUGIN / 'skills').glob('*/SKILL.md')):
        text = path.read_text()
        assert text.startswith('---\n')
        metadata = yaml.safe_load(text.split('---',2)[1])
        assert metadata['name'] == path.parent.name and metadata['description']
        skills.append(metadata['name'])
    assert len(skills) == 8
    mcp = json.loads((PLUGIN / 'mcp.json').read_text())
    assert set(mcp) == {'$schema','mcpServers'}
    assert mcp['$schema'] == 'https://agent-plugins.org/schemas/1.0.0/mcp.schema.json'
    server = mcp['mcpServers']['aero-library']
    assert server['type'] == 'stdio' and server['command'] == 'python'
    assert server['args'] == ['${PLUGIN_ROOT}/runtime/launch.py']
    assert not ({'PLUGIN_ROOT','PLUGIN_DATA'} & set(server.get('env',{})))
    assert server['cwd'] == '${PLUGIN_ROOT}'
    assert (PLUGIN / 'runtime/launch.py').is_file()
    schema_count = 0
    for path in (ROOT / 'schemas').rglob('*.json'):
        Draft202012Validator.check_schema(json.loads(path.read_text()))
        schema_count += 1
    sys.path.insert(0,str(ROOT / 'src'))
    from aero_webscraper.adapters.service import SPECS
    for name,spec in SPECS.items():
        archived = json.loads((ROOT / 'schemas/tools' / (name+'.schema.json')).read_text())
        assert archived == spec.model.model_json_schema(), name+' schema is stale'
    source_count = 0
    for prefix in (ROOT/'src', ROOT/'tests', ROOT/'scripts'):
        for path in files_under(prefix):
            if path.suffix == '.py':
                assert 'MMA FILE SUMMARY' in '\n'.join(path.read_text().splitlines()[:12]),str(path)
                compile(path.read_text(),str(path),'exec')
                source_count += 1
    assert (ROOT/'MMA_SKILL_INDEX.md').is_file()
    for path in files_under(PLUGIN):
        assert 'AERO_LIBRARY' not in path.relative_to(PLUGIN).parts
        assert path.name not in {'.env','credentials.json','token.json'}
    return {'validation_kind':'local structural, schema, syntax and MMA checks; not independent host certification',
            'version':manifest['version'],'skills':skills,'tool_count':len(SPECS),
            'json_schemas_checked':schema_count,'handwritten_python_files_checked':source_count,
            'corpus_bundled':False,'secrets_or_dependencies_bundled':False}


def smoke_test():
    with tempfile.TemporaryDirectory(prefix='aero-package-smoke-') as temp:
        env = os.environ.copy()
        env.pop('PYTHONPATH',None)
        env['AERO_LIBRARY_ROOT'] = str(Path(temp)/'AERO_LIBRARY')
        messages = [
            {'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'package-smoke','version':'1'}}},
            {'jsonrpc':'2.0','method':'notifications/initialized'},
            {'jsonrpc':'2.0','id':2,'method':'tools/list','params':{}},
            {'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'library_validate','arguments':{}}},
            {'jsonrpc':'2.0','id':4,'method':'tools/call','params':{'name':'reference_search','arguments':{'query':'must be blocked'}}},
        ]
        process = subprocess.run([sys.executable,str(PLUGIN/'runtime/launch.py')],
            input='\n'.join(json.dumps(m) for m in messages)+'\n',text=True,capture_output=True,
            cwd=PLUGIN,env=env,timeout=20)
        assert process.returncode == 0,process.stderr
        replies = [json.loads(x) for x in process.stdout.splitlines()]
        assert len(replies) == 4
        assert replies[0]['result']['protocolVersion'] == '2025-06-18'
        assert len(replies[1]['result']['tools']) == 11
        validation = replies[2]['result']['structuredContent']
        assert validation['valid'] and not validation['retrieval_enabled']
        assert replies[3]['result']['isError'] is True
        return {'passed':True,'protocol_version':'2025-06-18','tools_discovered':11,
                'fresh_root_initialized':True,'retrieval_default_off':True,'user_host_tested':False}


def archive(root: Path, destination: Path):
    with zipfile.ZipFile(destination,'w',compression=zipfile.ZIP_DEFLATED) as output:
        for path in files_under(root):
            output.write(path,root.name+'/'+path.relative_to(root).as_posix())
    with zipfile.ZipFile(destination) as check:
        assert check.testzip() is None
        assert {n.split('/')[0] for n in check.namelist()} == {root.name}
    return {'path':str(destination),'bytes':destination.stat().st_size,
            'sha256':hashlib.sha256(destination.read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--smoke',action='store_true')
    args = parser.parse_args()
    output = args.output.expanduser().resolve(); output.mkdir(parents=True,exist_ok=True)
    if output.is_relative_to(ROOT):
        parser.error('Archive output must be outside the source repository.')
    copy_runtime()
    report = validate_package()
    if args.smoke:
        report['packaged_runtime_smoke'] = smoke_test()
    report['archives'] = [archive(PLUGIN,output/'AERO-WebScraper-plugin-0.1.0.zip'),
                          archive(ROOT,output/'AERO-WebScraper-source-0.1.0.zip')]
    (output/'AERO-WebScraper-package-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__ == '__main__':
    main()