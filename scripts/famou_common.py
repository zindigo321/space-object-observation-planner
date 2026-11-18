"""Portable delivery contract. Fixed files and authoritative input are reopened."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def identity(path):
    raw=Path(path).read_bytes()
    return dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
def verify_fixed():
    manifest=read(ROOT/'FIXED_MANIFEST.json')
    for name,expected in manifest['files'].items():
        path=ROOT/name
        if path.is_symlink() or identity(path)!=expected:
            raise ValueError('fixed evaluator/input file changed: '+name)
    return identity(ROOT/'FIXED_MANIFEST.json')
def case_config(name):
    config=read(ROOT/'configs/famou_cases.json')[name]
    return ROOT/config['source'],config['source_sha256'],config['decision_s']
def write(path,value):
    Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
