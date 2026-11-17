"""Restore a flat, hash-checked upload without archives or original-machine paths."""
import argparse,hashlib,json
from pathlib import Path,PurePosixPath
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--uploads',default=str(Path(__file__).resolve().parent))
    p.add_argument('--out',required=True);a=p.parse_args()
    uploaded=Path(a.uploads).resolve();out=Path(a.out).absolute()
    if out.exists():raise ValueError('restore destination must be new')
    for ancestor in out.parents:
        if ancestor.is_symlink():raise ValueError('link destination')
    manifest=json.loads((uploaded/'UPLOAD_MANIFEST.json').read_text(encoding='utf-8'))
    seen=set();payload=[]
    for row in manifest['files']:
        n=PurePosixPath(row['restore_path'])
        if n.is_absolute() or n.as_posix()!=row['restore_path'] or any(x in ('.','..') or ':' in x or '\\' in x for x in n.parts):
            raise ValueError('unsafe restore path')
        if str(n).casefold() in seen:raise ValueError('duplicate restore path')
        seen.add(str(n).casefold())
        filename=row['upload_file']
        if Path(filename).name!=filename:raise ValueError('flat upload file required')
        f=uploaded/filename
        if f.is_symlink():raise ValueError('upload links rejected')
        data=f.read_bytes()
        if len(data)!=row['bytes'] or hashlib.sha256(data).hexdigest()!=row['sha256']:raise ValueError('missing/changed upload: '+filename)
        payload.append((n,data))
    out.mkdir(parents=True)
    for n,data in payload:
        dst=out/str(n);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
    print(json.dumps({'status':'PASS','restored_files':len(payload),'root':str(out)},ensure_ascii=False))
if __name__=='__main__':main()
