"""Build only committed, whitelisted source plus explicitly hashed test inputs."""
import argparse,csv,hashlib,io,json,subprocess,sys,zipfile
from pathlib import Path,PurePosixPath
from datetime import datetime,timezone
from build_handoff import source_allowed,safe_name,verify_archive,archive
ROOT=Path(__file__).resolve().parents[1]
RUNTIME_SCRIPTS={'team3_run.py','no_fault_backend.py','make_no_fault_example.py','famou_common.py',
                 'famou_run.py','famou_evaluator.py','famou_candidate_runner.py'}
def pretty(x):return (json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode()
def fp(raw):return dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
def main():
    p=argparse.ArgumentParser()
    for n in ('out','inputs','input-allowlist','wheelhouse'):p.add_argument('--'+n,required=True)
    p.add_argument('--commit',default='HEAD');a=p.parse_args()
    out=Path(a.out).absolute();out.mkdir(parents=True,exist_ok=False)
    def git(*args):return subprocess.check_output(['git','-c','safe.directory='+str(ROOT),'-C',str(ROOT),*args])
    commit=git('rev-parse',a.commit+'^{commit}').decode().strip()
    payload={}
    def add(n,raw,purpose,source):
        safe_name(n)
        if n in payload:raise ValueError('duplicate payload '+n)
        payload[n]=(raw,purpose,source)
    for item in git('ls-tree','-r','-z',commit).split(b'\0'):
        if not item:continue
        header,name=item.split(b'\t',1);mode,kind,oid=header.decode().split();name=name.decode()
        if mode not in ('100644','100755') or kind!='blob' or not source_allowed(name):raise ValueError('source outside whitelist: '+name)
        add(name,git('cat-file','blob',oid),'committed application source/test/documentation',commit+':'+name)
    inputs=Path(a.inputs);allow=json.loads(Path(a.input_allowlist).read_bytes())
    for name,entry in allow['files'].items():
        safe_name(name)
        if not name.startswith('data/') or Path(name).suffix not in ('.csv','.json'):raise ValueError('data outside whitelist')
        raw=(inputs/name.removeprefix('data/')).read_bytes()
        if fp(raw)!={k:entry[k] for k in ('bytes','sha256')}:raise ValueError('input changed '+name)
        add(name,raw,entry['purpose'],'frozen input: '+name)
    wheels=[]
    for wheel in sorted(Path(a.wheelhouse).glob('*.whl')):
        add('wheelhouse/'+wheel.name,wheel.read_bytes(),'offline Windows CPython3.11 dependency','PyPI exact pinned wheel')
        wheels.append(wheel.name)
    if len(wheels)!=6:raise ValueError('six locked runtime wheels required')
    add('FAMOU_START_PROMPT.txt',payload['famou/FAMOU_START_PROMPT.txt'][0],'paste after upload restoration','committed famou/FAMOU_START_PROMPT.txt')
    add('SOURCE_IDENTITY.json',pretty(dict(source_commit=commit,science_commit='1e35f9575ba79bd0d25fdfe96f624dce2a4ff5a5',
       science_core_unchanged=not bool(git('diff','1e35f9575ba79bd0d25fdfe96f624dce2a4ff5a5',commit,'--','planner')),
       platform_status='待用户在百度伐谋测试',source_export='git cat-file blobs; no working tree recursion')),
       'source attribution','build metadata')
    def upload_allowed(name):
        p=PurePosixPath(name)
        return ((p.parts[0]=='planner' and p.suffix=='.py') or
          (p.parts[0]=='scripts' and p.name in RUNTIME_SCRIPTS) or p.parts[0] in ('data','famou') or
          name in ('configs/famou_cases.json','FAMOU_START_PROMPT.txt','SOURCE_IDENTITY.json') or
          (name.startswith('examples/synthetic/no_fault_') and p.suffix in ('.json','.csv')))
    fixed={n:fp(v[0]) for n,v in payload.items() if upload_allowed(n) and
           (n.startswith(('planner/','scripts/','data/','configs/')) or n=='famou/requirements-lock.txt')}
    add('FIXED_MANIFEST.json',pretty(dict(files=fixed,manifest_excludes_self=True,
      policy='only external candidate script may vary; reject any fixed asset mutation')),
      'fixed runtime/input expected hashes','build metadata')
    runtime={n:v for n,v in payload.items() if upload_allowed(n) or n=='FIXED_MANIFEST.json'}
    rows=[]
    for index,(name,(raw,purpose,origin)) in enumerate(sorted(runtime.items()),1):
        suffix=PurePosixPath(name).suffix
        if suffix not in ('.py','.csv','.json','.md','.txt'):suffix='.txt'
        stem=name.replace('/','__')
        if not stem.endswith(suffix):stem+=suffix
        flat=f'f{index:03d}__'+stem
        rows.append(dict(upload_file=flat,restore_path=name,**fp(raw),purpose=purpose))
        add('upload/'+flat,raw,'flat upload for '+name,origin)
    bootstrap=[
      ('restore_upload.py',payload['scripts/restore_upload.py'][0],'restore verified flat files'),
      ('UPLOAD_MANIFEST.json',pretty(dict(schema='FAMOU_FLAT_UPLOAD_V1',source_commit=commit,files=rows,
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
    add('PACKAGE_ALLOWLIST.json',pretty(dict(source_whitelist='scripts/build_handoff.py source_allowed',source_commit=commit,
        data_files=list(allow['files']),wheel_files=wheels,upload_files=ordered,
        audit_files_uploaded=False)), 'explicit packaging allowlist','build metadata')
    receipt=archive(out/'FAMOU_TEST_PACKAGE.zip',payload,dict(source_commit=commit,
       schema='FAMOU_TEST_PACKAGE_V1',science_commit='1e35f9575ba79bd0d25fdfe96f624dce2a4ff5a5',
       validation_status='see external acceptance report bound to this exact ZIP',platform_status='待用户在百度伐谋测试'))
    # External upload copies are exactly the packaged bytes, with no hidden files.
    for n,(raw,_,_) in payload.items():
        if n.startswith('upload/') or n in ('UPLOAD_LIST.csv','UPLOAD_BATCHES.md','FAMOU_START_PROMPT.txt'):
            target=out/n;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    (out/'TEST_PACKAGE_BUILD_RECEIPT.json').write_bytes(pretty(receipt))
    print(json.dumps(receipt))
if __name__=='__main__':main()
