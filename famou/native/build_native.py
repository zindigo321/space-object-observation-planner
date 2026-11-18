"""Build with the local UCRT64 toolchain. No problem inputs are opened by the build."""
from pathlib import Path
import argparse, subprocess, hashlib, json, datetime
def ident(p):
    p=Path(p);return dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--compiler',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True)
    a=p.parse_args();root=Path(__file__).resolve().parent
    target=root/'frozen_native.dll'
    if target.exists(): raise FileExistsError(target)
    args=[str(a.compiler),'-std=c++17','-O3','-fno-fast-math','-ffp-contract=off','-shared','-static','-Wl,--no-insert-timestamp',
          '-o',target.name,'frozen_native.cpp']
    r=subprocess.run(args,cwd=root,capture_output=True)
    obj=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),argv=args,cwd=str(root),compiler=ident(a.compiler),
             compiler_version=subprocess.check_output([a.compiler,'--version'],text=True),source=ident(root/'frozen_native.cpp'),
             stdout=r.stdout.decode(errors='replace'),stderr=r.stderr.decode(errors='replace'),returncode=r.returncode,
             output=ident(target) if target.is_file() else None)
    a.receipt.write_text(json.dumps(obj,indent=2),encoding='utf-8')
    raise SystemExit(r.returncode)

