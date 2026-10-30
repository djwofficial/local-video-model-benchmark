import concurrent.futures,hashlib,json,os,re,subprocess,threading,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CHUNK=16*1024**2
WORKERS=8
for item,kind in zip(json.loads((ROOT/'models-sources.json').read_text()),['checkpoints','text_encoders']):
    info=item['metadata'][0];size=info['size'];expected=info['lfs']['oid']
    dest=Path('/Users/dyn/AI/models')/kind/Path(item['file']).name
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():
        assert dest.stat().st_size==size and hashlib.file_digest(dest.open('rb'),'sha256').hexdigest()==expected
        continue
    part=dest.with_suffix('.safetensors.ranged-partial');statepath=dest.with_suffix('.chunks.json')
    state=json.loads(statepath.read_text()) if statepath.exists() else {'size':size,'sha256':expected,'chunks':{}}
    assert state['size']==size and state['sha256']==expected
    fd=os.open(part,os.O_RDWR|os.O_CREAT,0o644);os.ftruncate(fd,size)
    lock=threading.Lock();total=(size+CHUNK-1)//CHUNK;t0=time.time()
    url='https://huggingface.co/'+item['repo']+'/resolve/main/'+item['file']+'?download=true'
    print('START',dest.name,'bytes',size,'chunks',total,'workers',WORKERS,flush=True)
    def transfer(i):
        start=i*CHUNK;end=min(size,start+CHUNK)-1;count=end-start+1
        if str(i) in state['chunks'] and hashlib.sha256(os.pread(fd,count,start)).hexdigest()==state['chunks'][str(i)]: return
        tmp=part.with_suffix(f'.chunk-{i}')
        if tmp.exists() and tmp.stat().st_size>count: tmp.unlink()
        offset=tmp.stat().st_size if tmp.exists() else 0
        for attempt in range(20):
            if offset==count: break
            piece=tmp.with_suffix(tmp.suffix+'.piece');headers=tmp.with_suffix(tmp.suffix+'.piece-headers')
            piece.write_bytes(b'')
            code=subprocess.call(['curl','--fail','--location','--silent','--show-error','--connect-timeout','15','--max-time','600','--speed-time','60','--speed-limit','8192','--range',f'{start+offset}-{end}','--dump-header',str(headers),'--output',str(piece),url])
            ranges=re.findall(r'content-range:\s*bytes\s+(\d+)-(\d+)/(\d+)',headers.read_text(),re.I) if headers.exists() else []
            if ranges and tuple(map(int,ranges[-1]))==(start+offset,end,size):
                fragment=piece.read_bytes()
                if 0<len(fragment)<=count-offset:
                    with tmp.open('ab') as f: f.write(fragment);f.flush();os.fsync(f.fileno())
                    offset+=len(fragment)
            if piece.exists(): piece.unlink()
            if headers.exists(): headers.unlink()
            if offset<count:
                print('RESUME',i,'bytes',offset,'/',count,'attempt',attempt+1,'curl_status',code,flush=True)
                time.sleep(3)
        if offset!=count: raise RuntimeError('Chunk failed '+str(i))
        data=tmp.read_bytes();assert len(data)==count
        assert os.pwrite(fd,data,start)==count
        digest=hashlib.sha256(data).hexdigest()
        with lock:
            os.fsync(fd);state['chunks'][str(i)]=digest
            pending=statepath.with_suffix('.json.tmp');pending.write_text(json.dumps(state));pending.replace(statepath)
            downloaded=sum(min(CHUNK,size-int(k)*CHUNK) for k in state['chunks'])
            print(f'{dest.name}: {len(state["chunks"])}/{total} chunks, {downloaded/size:.1%}, {downloaded/1024**2:.1f} MiB, elapsed {time.time()-t0:.1f}s',flush=True)
        tmp.unlink()
        oldheaders=tmp.with_suffix(tmp.suffix+'.headers')
        if oldheaders.exists(): oldheaders.unlink()
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool: list(pool.map(transfer,range(total)))
    finally: os.close(fd)
    actual=hashlib.file_digest(part.open('rb'),'sha256').hexdigest()
    assert actual==expected, 'Final SHA-256 mismatch'
    part.rename(dest)
    print('VERIFIED',dest.name,actual,flush=True)
    results=[]
    integrity=ROOT/'model-integrity.json'
    if integrity.exists(): results=json.loads(integrity.read_text())
    results=[r for r in results if r['path']!=str(dest)]
    results.append({'path':str(dest),'bytes':size,'sha256':actual,'verified':True})
    integrity.write_text(json.dumps(results,indent=2))
