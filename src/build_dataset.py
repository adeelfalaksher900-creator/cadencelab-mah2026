from pathlib import Path
import sys,json,re,html,urllib.request,subprocess,hashlib
import numpy as np
import soundfile as sf
from alignment import Aligner
from acoustics import features,compare,json_features
ROOT=Path(__file__).resolve().parent.parent;OUT=ROOT/'web/public/dataset';OUT.mkdir(parents=True,exist_ok=True)
SR=16000
SOURCES=[('jfk-1961','https://commons.wikimedia.org/wiki/File:JFK_inaugural_address.ogg','AND SO MY FELLOW AMERICANS ASK NOT WHAT YOUR COUNTRY CAN DO FOR YOU ASK WHAT YOU CAN DO FOR YOUR COUNTRY'),('obama-20170114','2017/01/14/weekly-address-honor-serving-you-president','This week, I traveled'),('obama-20170107','2017/01/07/weekly-address-president-obamas-farewell-address-nation','Since the days of George Washington')]
def decode(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-f','f32le','-ac','1','-ar',str(SR),'-']),np.float32).copy()
def normalize(t):return ' '.join(re.sub(r"[^A-Z' ]",' ',t.replace('’',"'").upper()).split())
def tempo(y,factor):
 b=subprocess.check_output(['ffmpeg','-v','error','-f','f32le','-ac','1','-ar',str(SR),'-i','pipe:0','-af',f'atempo={factor}','-f','f32le','pipe:1'],input=y.astype(np.float32).tobytes());return np.frombuffer(b,np.float32).copy()
a=Aligner();manifest=[];refs=[]
for source,url_path,anchor in SOURCES:
 if source=='jfk-1961':
  url=url_path;text=anchor;y=decode(ROOT/'data/jfk.wav');speaker='John F. Kennedy';segments=[(0,22)]
 else:
  url='https://obamawhitehouse.archives.gov/the-press-office/'+url_path
  cache=ROOT/'data'/f'{source}-transcript.html'
  if not cache.exists():cache.write_bytes(urllib.request.urlopen(url,timeout=40).read())
  s=cache.read_text();paras=[html.unescape(re.sub('<[^>]+>','',x)).strip() for x in re.findall(r'<p\b[^>]*>(.*?)</p>',s,re.S)]
  matches=[i for i,x in enumerate(paras) if x.startswith(anchor)]
  if not matches:raise ValueError('Source transcript anchor unavailable: '+source)
  ix=matches[0];end_ix=next(i for i in range(ix,len(paras)) if paras[i]=='###');transcript=' '.join(paras[ix:end_ix]).replace('20 million','twenty million');text=normalize(transcript)
  y=decode(ROOT/'data'/f'{source}.mp3');speaker='Barack Obama';segments=[(0,38),(38,76)]
 logp,tt=a.emissions(y);words=a.align(logp,tt,text)
 for j,(lo,hi) in enumerate(segments):
  selected=words[lo:hi];start=max(0,selected[0]['start']-.15);end=selected[-1]['end']+.15
  r=y[int(start*SR):int(end*SR)];rtext=' '.join(w['word'] for w in selected);name=f'{source}-{j+1}';rp=OUT/f'{name}-reference.flac';sf.write(rp,r,SR);r=sf.read(rp,dtype='float32')[0]
  lp,t=a.emissions(r);rw=a.align(lp,t,rtext);rf=features(r)
  refs.append({'id':name,'speaker':speaker,'speech':source,'source_url':url,'original_interval':[start,end],'transcript':rtext,'reference_file':rp.name,'duration':len(r)/SR,'words':rw,'features':json_features(rf),'license':'US federal-government work; public-domain source, no endorsement.'})
  variants=[('control',0,0),('gain',0,.5),('pitchcontrol',0,3)]
  for kind,values in [('pace',[1.15,1.4,1.8]),('energy',[.5,.25,.1]),('pause',[.4,.9,1.8]),('noise',[20,10,0]),('pitch',[2,4,7])]:variants.extend((kind,k+1,v) for k,v in enumerate(values))
  for kind,level,param in variants:
   x=r.copy();begin=rw[min(12,len(rw)//3)]['start'];stop=rw[min(25,2*len(rw)//3)]['end'];aa=int(begin*SR);bb=int(stop*SR);truth=[]
   if kind=='pace':
    mid=tempo(x[aa:bb],param);x=np.r_[x[:aa],mid,x[bb:]];truth=[{'kind':'pace','start':begin,'end':begin+len(mid)/SR,'reference_start':begin,'reference_end':stop,'factor':param}]
   elif kind=='energy':x[aa:bb]*=param;truth=[{'kind':'energy','start':begin,'end':stop,'gain':param}]
   elif kind=='noise':
    rng=np.random.default_rng(2026+j);noise=rng.standard_normal(bb-aa);scale=np.sqrt(np.mean(x[aa:bb]**2))/10**(param/20);x[aa:bb]+=noise/(np.std(noise)+1e-9)*scale;truth=[{'kind':'texture','start':begin,'end':stop,'snr_db':param}]
   elif kind=='pause':
    k=min(18,len(rw)-2);at=int(rw[k]['end']*SR);x=np.r_[x[:at],np.zeros(round(param*SR)),x[at:]];truth=[{'kind':'pause','start':rw[k]['end'],'end':rw[k+1]['start']+param,'inserted_seconds':param}]
   elif kind in ['pitch','pitchcontrol']:
    za,zb=(aa,bb) if kind=='pitch' else (0,len(x));mid=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-f','f32le','-ac','1','-ar',str(SR),'-i','pipe:0','-af',f'rubberband=pitch={2**(param/12)}','-f','f32le','pipe:1'],input=x[za:zb].astype(np.float32).tobytes()),np.float32);x=np.r_[x[:za],mid,x[zb:]]
    if kind=='pitch':truth=[{'kind':'pitch','start':begin,'end':begin+len(mid)/SR,'semitones':param}]
   elif kind=='gain':x*=param
   x=np.clip(x,-.999,.999).astype(np.float32);vid=f'{name}-{kind}-{level}';fn=OUT/f'{vid}.flac';sf.write(fn,x,SR);x=sf.read(fn,dtype='float32')[0]
   try:
    pl,pt=a.emissions(x);pw=a.align(pl,pt,rtext);pf=features(x);result=compare(rf,pf,rw,pw);wer=a.transcript_error(pl,rtext);result['transcript_error']=wer;result['status']='abstained' if wer>.55 or result['alignment_confidence']<.35 else 'analyzed'
    if result['status']=='abstained':result['events']=[e for e in result['events'] if e['metrics'].get('basis')=='recording-texture'];result['status']='partial' if result['events'] else 'abstained';result['rubric']['comparison_score']=None;result['reason']='Insufficient acoustic support for the transcript; try cleaner audio.'
    result.update({'reference_id':name,'id':vid,'kind':kind,'severity':level,'parameter':param,'audio':fn.name,'transcript':rtext,'ground_truth':truth,'duration':len(x)/SR,'words':pw,'features':json_features(pf),'sha256':hashlib.sha256(fn.read_bytes()).hexdigest()})
   except ValueError as e:result={'id':vid,'reference_id':name,'kind':kind,'severity':level,'audio':fn.name,'ground_truth':truth,'error':str(e)}
   (OUT/f'{vid}.json').write_text(json.dumps(result,allow_nan=False,separators=(',',':')));manifest.append({k:result[k] for k in ['id','reference_id','kind','severity','audio','ground_truth']});print(vid,len(result.get('events',[])),flush=True)
refs.sort(key=lambda r:(r['speaker']!='Barack Obama',r['id']));(OUT/'references.json').write_text(json.dumps(refs,allow_nan=False,separators=(',',':')))
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));print('Dataset cases:',len(manifest))
