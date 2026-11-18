"""Run historical development calibration under the same research controller."""
import argparse,json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from expansion_run import read,write,monitor,execute_case,ROOT

def main():
    p=argparse.ArgumentParser();p.add_argument('--batch',required=True);a=p.parse_args();batch=read(a.batch)
    work=Path(batch['root'])/'work';out=work/'calibration';out.mkdir(exist_ok=False)
    script=ROOT/'research/calibrate_worker.py';source=batch['historical_payload'];worker=batch['worker_python']
    common=[worker,'-B','-X','utf8',str(script)]
    r=monitor(common+['historical','--source',source,'--out',str(out/'H180_input'),'--spec',str(out/'dev_spec.json')],120,out/'historical.log',batch['root'],batch)
    if r['status']!='PASS':raise RuntimeError('historical fixture failed')
    results=[]
    for method in ('baseline','improved'):
        case=dict(case_id='H180_DEV_INIT_'+method,kind='initial',method=method,unit_id='H180_DEV',development_only=True)
        results.append(execute_case(batch,None,case,out/(case['case_id']+'_a01'),out/'H180_input'))
        print(json.dumps(dict(case=case['case_id'],status=results[-1]['status'],J=results[-1].get('J_selected'))),flush=True)
    for origin in ('baseline','improved'):
        initial=out/f'H180_DEV_INIT_{origin}_a01/evaluate/selected.json'
        if not initial.exists():continue
        for scene in ('C','F'):
            for method in ('baseline','improved'):
                case=dict(case_id=f'H180_DEV_{origin}_{scene}_{method}',kind='replan',method=method,unit_id='H180_DEV',
                    origin=origin,scenario=scene,development_only=True)
                results.append(execute_case(batch,None,case,out/(case['case_id']+'_a01'),out/'H180_input',initial))
                print(json.dumps(dict(case=case['case_id'],status=results[-1]['status'],J=results[-1].get('J_selected'))),flush=True)
    write(out/'CASE_SUMMARY.json',results)
    for label,cmd,seconds in [
        ('stream3',[worker,'-B','-X','utf8',str(ROOT/'research/expansion_worker.py'),'produce','--spec',str(out/'dev_spec.json'),
            '--inventory',batch['inventory'],'--out',str(out/'stream3'),'--seconds','300'],300),
        ('equivalence',common+['equivalence','--source',str(out/'stream3'),'--out',str(out/'monolithic3')],300),
        ('native_compare',common+['native_compare','--source',source,'--calibration',str(out),'--out',str(out/'native_compare')],120),
        ('hard30',[worker,'-B','-c','import time; time.sleep(31.25)'],30),
        ('memory_guard',[worker,'-B','-c','import time; a=bytearray(256*1024*1024); time.sleep(5)'],10)]:
        r=monitor(cmd,seconds,out/(label+'.log'),batch['root'],batch,rss_cap=128*1024**2 if label=='memory_guard' else None)
        write(out/(label+'_RECEIPT.json'),r);print(json.dumps(dict(calibration=label,status=r['status'])),flush=True)
    write(out/'CALIBRATION_FINISHED.json',dict(case_count=len(results),all_cases_pass=all(r['status']=='PASS' for r in results),time=time.time()))
if __name__=='__main__':main()
