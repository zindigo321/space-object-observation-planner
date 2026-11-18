"""Build only committed, whitelisted source plus explicitly hashed test inputs."""
import argparse,csv,hashlib,io,json,subprocess
from pathlib import Path
from build_handoff import safe_name,archive
ROOT=Path(__file__).resolve().parents[1]
def pretty(x):return (json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode()
def fp(raw):return dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
def main():
    p=argparse.ArgumentParser()
    for n in ('out','inputs','input-allowlist','wheelhouse'):p.add_argument('--'+n,required=True)
    p.add_argument('--s02-inputs',type=Path,help='S02 directory containing spec.json and raw/')
    p.add_argument('--test-wheelhouse',required=True)
    p.add_argument('--commit',default='HEAD');a=p.parse_args()
    out=Path(a.out).absolute();out.mkdir(parents=True,exist_ok=False)
    def git(*args):return subprocess.check_output(['git','-c','safe.directory='+str(ROOT),'-C',str(ROOT),*args])
    commit=git('rev-parse',a.commit+'^{commit}').decode().strip()
    def document(name):
        return json.loads(git('cat-file','blob',commit+':'+name))
    release=document('famou/release_files.json')
    contract=document('configs/s02_contract.json')
    selected=set(release['git_files'])
    payload={}
    def add(n,raw,purpose,source):
        safe_name(n)
        if n in payload:raise ValueError('duplicate payload '+n)
        payload[n]=(raw,purpose,source)
    for item in git('ls-tree','-r','-z',commit).split(b'\0'):
        if not item:continue
        header,name=item.split(b'\t',1);mode,kind,oid=header.decode().split();name=name.decode()
        if name not in selected:continue
        if mode not in ('100644','100755') or kind!='blob' or name.startswith('research/'):raise ValueError('source outside whitelist: '+name)
        add(name,git('cat-file','blob',oid),'committed application source/test/documentation',commit+':'+name)
    inputs=Path(a.inputs);allow=json.loads(Path(a.input_allowlist).read_bytes())
    if set(payload)!=selected:raise ValueError('missing explicitly listed Git release file')
    if {n:{k:r[k] for k in ('bytes','sha256')} for n,r in allow['files'].items()}!=release['legacy_data']:
        raise ValueError('H180 / synthetic input allowlist differs from accepted release')
    for name,entry in allow['files'].items():
        safe_name(name)
        if not name.startswith('data/') or Path(name).suffix not in ('.csv','.json'):raise ValueError('data outside whitelist')
        raw=(inputs/name.removeprefix('data/')).read_bytes()
        if fp(raw)!={k:entry[k] for k in ('bytes','sha256')}:raise ValueError('input changed '+name)
        add(name,raw,entry['purpose'],'frozen input: '+name)
    s02=Path(a.s02_inputs or inputs/'S02')
    for name,expected in {'spec.json':contract['spec'],**{'raw/'+k:v for k,v in contract['raw'].items()}}.items():
        raw=(s02/name).read_bytes()
        if fp(raw)!=expected:raise ValueError('S02 frozen raw material changed: '+name)
        add('data/S02/'+name,raw,'frozen S02 instance or raw material','c118d8e frozen S02')
    if fp(payload['famou/native/frozen_native.dll'][0])!=contract['native']:
        raise ValueError('S02 committed DLL hash mismatch')
    abi=json.loads(payload['famou/native/ABI.json'][0])
    source=fp(payload['famou/native/frozen_native.cpp'][0])
    if source!=contract['native_source'] or source!=abi['build']['source'] or contract['native']!=abi['build']['output']:
        raise ValueError('S02 C++ export, DLL and embedded compiler/ABI receipt must match')
    wheels=[]
    for wheel in sorted(Path(a.wheelhouse).glob('*.whl')):
        add('wheelhouse/'+wheel.name,wheel.read_bytes(),'offline Windows CPython3.11 dependency','PyPI exact pinned wheel')
        wheels.append(wheel.name)
    if len(wheels)!=6:raise ValueError('six locked runtime wheels required')
    test_wheels=[]
    for wheel in sorted(Path(a.test_wheelhouse).glob('*.whl')):
        add('wheelhouse/'+wheel.name,wheel.read_bytes(),'offline CPython3.11 regression dependency','exact pinned test wheel')
        test_wheels.append(wheel.name)
    if len(test_wheels)!=6:raise ValueError('six locked test wheels required')
    actual_wheels={n.removeprefix('wheelhouse/'):fp(v[0]) for n,v in payload.items() if n.startswith('wheelhouse/')}
    if actual_wheels!=contract['wheels']:raise ValueError('offline wheel set or locked wheel hash differs')
    add('FAMOU_START_PROMPT.txt',payload['famou/FAMOU_START_PROMPT.txt'][0],'paste after upload restoration','committed famou/FAMOU_START_PROMPT.txt')
    add('SOURCE_IDENTITY.json',pretty(dict(source_commit=commit,git_tree=git('rev-parse',commit+'^{tree}').decode().strip(),
        research_commit=contract['research_commit'],h180_commit=contract['h180_commit'],native=contract['native'],
        git_files={n:fp(payload[n][0]) for n in release['git_files']},s02_entry='scripts/famou_run.py --case S02',
        runtime='Windows x64 / CPython 3.11',baidu='PENDING')),'effective source attribution','committed Git blobs')
    fixed={n:fp(payload[n][0]) for n in release['legacy_fixed']}
    add('FIXED_MANIFEST.json',pretty(dict(files=fixed,manifest_excludes_self=True)),
        'fixed legacy runtime and input expected hashes','committed H180 scope')
    runtime=payload.copy()
    rows=[]
    for index,(name,(raw,purpose,origin)) in enumerate(sorted(runtime.items()),1):
        flat=f'f{index:03d}__'+name.replace('/','__')
        rows.append(dict(upload_file=flat,restore_path=name,**fp(raw),purpose=purpose))
        add('upload/'+flat,raw,'flat upload for '+name,origin)
    bootstrap=[
      ('restore_upload.py',payload['scripts/restore_upload.py'][0],'restore verified flat files'),
      ('UPLOAD_MANIFEST.json',pretty(dict(schema='FAMOU_FLAT_UPLOAD_V2',platform='Windows x64 / CPython 3.11',capabilities=['S02','synthetic','H180_BASE','H180_IMP','pytest'],source_commit=commit,files=rows,
         bootstrap_files=['restore_upload.py','UPLOAD_MANIFEST.json'],max_files_per_batch=30)),'upload mapping and expected hashes')]
    for name,raw,purpose in bootstrap:add('upload/'+name,raw,purpose,'build metadata')
    ordered=[x[0] for x in bootstrap]+[r['upload_file'] for r in rows]
    table=io.StringIO(newline='');writer=csv.writer(table)
    writer.writerow(['batch','upload_file','restore_path','bytes','sha256','purpose'])
    for i,name in enumerate(ordered):
        batch=i//30+1
        row=next((r for r in rows if r['upload_file']==name),None)
        raw,purpose,_=payload['upload/'+name]
        writer.writerow([batch,name,row['restore_path'] if row else '(bootstrap)',len(raw),hashlib.sha256(raw).hexdigest(),purpose])
    add('UPLOAD_LIST.csv',table.getvalue().encode('utf-8-sig'),'per-file upload checklist','build metadata')
    batches=['# 上传批次','',f'共 {len(ordered)} 个上传文件，分 {(len(ordered)+29)//30} 批；每批最多 30 个。全部到齐后粘贴 FAMOU_START_PROMPT.txt。','']
    for i in range(0,len(ordered),30):
        batches += [f'## 第 {i//30+1} 批','']+['- '+n for n in ordered[i:i+30]]+['']
    add('UPLOAD_BATCHES.md','\n'.join(batches).encode(),'explicit batches','build metadata')
    add('PACKAGE_ALLOWLIST.json',pretty(dict(source_whitelist='famou/release_files.json',git_files=sorted(selected),source_commit=commit,
        data_files=sorted(n for n in payload if n.startswith('data/')),wheel_files=wheels,test_wheel_files=test_wheels,upload_files=ordered,
        audit_files_uploaded=False)), 'explicit packaging allowlist','build metadata')
    receipt=archive(out/'FAMOU_TEST_PACKAGE.zip',payload,dict(source_commit=commit,
       schema='FAMOU_TEST_PACKAGE_V2',research_commit=contract['research_commit'],h180_commit=contract['h180_commit'],
       validation_status='see external acceptance report bound to this exact ZIP',platform_status='待用户在百度伐谋测试'))
    # External upload copies are exactly the packaged bytes, with no hidden files.
    for n,(raw,_,_) in payload.items():
        if n.startswith('upload/') or n in ('UPLOAD_LIST.csv','UPLOAD_BATCHES.md','FAMOU_START_PROMPT.txt'):
            target=out/n;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    (out/'TEST_PACKAGE_BUILD_RECEIPT.json').write_bytes(pretty(receipt))
    print(json.dumps(receipt))
if __name__=='__main__':main()
