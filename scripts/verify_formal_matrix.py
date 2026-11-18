"""Read-only four-group verification and real seal/post/accept; never runs a solver."""
import argparse,hashlib,json,shutil,sys,time,zipfile
from pathlib import Path,PurePosixPath
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from planner.no_fault import recheck
from planner.no_fault_source import load_source
from planner.no_fault import verify_tasks
from planner.io_contract import read_complete_tasks

CASES={'H180_BASE_baseline','H180_BASE_improved','H180_IMP_baseline','H180_IMP_improved'}
EXPECTED_SOURCE={
    'H180_BASE':'571bd32b2265aa46f7fa09cfbee9af4cf7be1d5cb57e63916d11e0d04cb12914',
    'H180_IMP':'b9567a450adf332fe587e9e325af0d61654e0268e1a889868e9d396d33e1dfac'}

def read(path):return json.loads(Path(path).read_bytes())
def pretty(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
def identity(raw):return {'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
def file_id(path):return identity(Path(path).read_bytes())
def need(ok,reason):
    if not ok:raise ValueError(reason)
def safe(name):
    p=PurePosixPath(name)
    need(p.as_posix()==name and not p.is_absolute() and '..' not in p.parts and '\\' not in name
         and ':' not in name and name not in ('','.'),'unsafe ZIP path')

def verify_tree(root,out):
    matrix=read(root/'MATRIX.json');groups=matrix['groups']
    need(len(groups)==4 and {row['case'] for row in groups}==CASES,'four distinct formal groups required')
    out.mkdir(parents=True,exist_ok=False);results=[]
    for row in groups:
        name=row['case'];key=name.rsplit('_',1)[0];sha=EXPECTED_SOURCE[key]
        group=root/'evidence'/name/'experiment/natives'/name;run=group/'workflow/run'
        result=read(group/'group_result.json');workflow=read(group/'workflow/workflow.json')
        need(result['status']=='PASS' and result['solver_calls']==1 and result['backend_count']==3,'original formal group failed')
        need(workflow['status']=='PASS' and workflow['original_raw_return_codes']==[0,0,0]
             and workflow['protected_unchanged'] and workflow['run_source_unchanged'],'original formal workflow failed')
        need(result['source_sha256']==row['source_sha256']==sha,'frozen source identity changed')
        need(row['source_commit']=='1e35f9575ba79bd0d25fdfe96f624dce2a4ff5a5','science object changed')
        source=load_source(run/'source',sha)
        reports={label:verify_tasks(source,3600,read_complete_tasks(run/(label+'.csv'))[2],label!='raw_proposal')
                 for label in ('retained','raw_proposal','selected')}
        need([reports[n]['J'] for n in ('retained','raw_proposal','selected')]==
             [row['J_retained'],row['J_raw'],row['J_selected']],'matrix objective not derived from actual CSVs')
        recheck(run,sha,out/name)
        proof=read(out/name/'recheck.json')
        need(proof['status']=='PASS' and proof['solver_calls']==0 and proof['branch']==row['branch'],'fresh recheck failed')
        for filename,keyname in [('geometry.json','geometry'),('geometry_projection.json','conversion')]:
            need(file_id(group/filename)==result[keyname],'original geometry evidence changed')
        evidence=root/'evidence'/name
        need(read(evidence/'PROTECTION.json')['status']=='PASS','original protection failed')
        protection=read(evidence/'PROTECTION_RESULT.json')
        need(protection.get('status')=='PASS' or (protection.get('pass') is True and protection.get('raw_exit')==0),'protection raw result failed')
        results.append({'case':name,'passed':True,'J_retained':reports['retained']['J'],
            'J_raw':reports['raw_proposal']['J'],'J_selected':reports['selected']['J'],
            'branch':proof['branch'],'recheck':file_id(out/name/'recheck.json')})
    for prefix in EXPECTED_SOURCE:
        pair=[r for r in groups if r['case'].startswith(prefix)]
        need(len(pair)==2 and pair[0]['source_files']==pair[1]['source_files']
             and pair[0]['deployed_product_files']==pair[1]['deployed_product_files'],'pair input or product mismatch')
    terminal=read(root/'FOURTH_FORMAL_REVIEW.json')
    need(terminal['passed'] and terminal['science_verdict']=='SCIENTIFIC_AND_PROTECTION_PASS'
         and terminal['conclusion']=='ONE_FORMAL_ATTEMPT_SCIENTIFIC_PROTECTION_C12_C13_PASS_NO_REPLAY',
         'fourth group lacks independently checked formal/native/C12/C13 closure')
    counts=terminal['formal_attempt']
    need(counts['submit_arrivals']==counts['consumer_rows']==counts['dispatch_started']==counts['response_acked']==1,
         'formal one-shot counts not one')
    report={'passed':True,'verified_groups':results,'pairs_verified':2,'solver_invocations':0,
            'fourth_formal_review':file_id(root/'FOURTH_FORMAL_REVIEW.json'),'user_personal_signoff':False}
    (out/'VERIFICATION.json').write_bytes(pretty(report));return report

def check_zip(path):
    with zipfile.ZipFile(path) as z:
        names=z.namelist();need(len(names)==len(set(n.casefold() for n in names)),'duplicate member')
        need(z.testzip() is None,'CRC failed')
        manifest=json.loads(z.read('MANIFEST.json'))
        need(set(names)==set(manifest['files'])|{'MANIFEST.json'},'manifest file set mismatch')
        for name in names:
            safe(name);need((z.getinfo(name).external_attr>>16)&0o170000!=0o120000,'symlink')
            if name!='MANIFEST.json':need(identity(z.read(name))==manifest['files'][name],'member bytes changed')
    return manifest

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('operation',choices=['seal','post','accept'])
    p.add_argument('--source',required=True);p.add_argument('--out',required=True)
    a=p.parse_args();source=Path(a.source).resolve();out=Path(a.out).resolve()
    need(not source.is_dir() or (source!=out and source not in out.parents),'output must be outside sealed evidence')
    need(not out.exists(),'new output path required');out.mkdir(parents=True)
    started=time.perf_counter()
    if a.operation=='seal':
        verified=verify_tree(source,out/'checks')
        paths=list(source.rglob('*'));need(not any(p.is_symlink() for p in paths),'source symlink forbidden')
        files={p.relative_to(source).as_posix():file_id(p) for p in paths if p.is_file()}
        for n in files:
            safe(n);need(not n.lower().endswith(('.key','.pem','.env','.pfx','.p12')),'credential extension forbidden')
        seal={'kind':'FOUR_FORMAL_GROUP_SEAL','matrix':file_id(source/'MATRIX.json'),'files':files,
              'verification':verified,'separate_delivery_validation':True}
        (out/'SEAL.json').write_bytes(pretty(seal))
        payload={n:(source/n).read_bytes() for n in files};payload['SEAL.json']=pretty(seal)
        manifest={'files':{n:identity(b) for n,b in payload.items()},'manifest_excludes_self':True}
        with zipfile.ZipFile(out/'FORMAL_MATRIX.zip','x',compression=zipfile.ZIP_DEFLATED) as z:
            for n,b in payload.items():z.writestr(n,b)
            z.writestr('MANIFEST.json',pretty(manifest))
        check_zip(out/'FORMAL_MATRIX.zip')
        result={'operation':'seal','passed':True,'archive':file_id(out/'FORMAL_MATRIX.zip'),'source':str(source)}
    elif a.operation=='post':
        manifest=check_zip(source);target=out/'全新路径 读回';target.mkdir()
        with zipfile.ZipFile(source) as z:z.extractall(target)
        need(all(file_id(target/n)==v for n,v in manifest['files'].items()),'post bytes differ')
        result={'operation':'post','passed':True,'source_archive':file_id(source),'extracted_root':str(target),
                'manifest':file_id(target/'MANIFEST.json'),'file_count':len(manifest['files'])}
    else:
        manifest=read(source/'MANIFEST.json')
        need(all(file_id(source/n)==v for n,v in manifest['files'].items()),'readback tree changed')
        verified=verify_tree(source,out/'checks')
        result={'operation':'accept','passed':verified['passed'],
                'formal_matrix_accepted':verified['passed'] and len(verified['verified_groups'])==4,
                'fresh_rechecks':verified,'source_manifest':file_id(source/'MANIFEST.json'),
                'user_personal_signoff':False,'scientific_requests_replayed':0}
    result['seconds']=time.perf_counter()-started
    (out/(a.operation.upper()+'.json')).write_bytes(pretty(result));print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':main()
