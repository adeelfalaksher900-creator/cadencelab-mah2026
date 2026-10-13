"""Audio features and transparent contrastive rubric. No subjective talent score."""
import numpy as np
from scipy.fft import rfft,irfft
from scipy.signal import find_peaks

def features(y,sr=16000):
 y=np.asarray(y,np.float32);frame=640;hop=320
 if len(y)<frame:raise ValueError('Recording is too short')
 x=np.lib.stride_tricks.sliding_window_view(y,frame)[::hop].copy()
 rms=np.sqrt(np.mean(x*x,axis=1)+1e-12);db=20*np.log10(rms+1e-12)
 spec=np.abs(rfft(x*np.hanning(frame),1024));power=spec*spec+1e-12
 flat=np.exp(np.mean(np.log(power[:,4:320]),axis=1))/np.mean(power[:,4:320],axis=1)
 ac=irfft(np.abs(rfft(x-x.mean(axis=1,keepdims=True),2048))**2,2048)[:,:frame]
 ac/=np.maximum(ac[:,0,None],1e-12);low=sr//500;high=sr//65
 lags=np.argmax(ac[:,low:high],axis=1)+low;strength=ac[np.arange(len(ac)),lags]
 voiced=(strength>.6)&(db>max(-65,float(np.percentile(db,80)-30)))
 pitch=np.where(voiced,sr/lags,np.nan);valid=pitch[voiced]
 center=float(np.median(valid)) if len(valid) else 0
 semitones=np.where(voiced,12*np.log2(pitch/max(center,1)),np.nan)
 # Cepstral coefficients: mel-filtered log powers followed by orthogonal DCT.
 from scipy.fft import dct
 hz=lambda m:700*(10**(m/2595)-1); mel=lambda h:2595*np.log10(1+h/700)
 edges=hz(np.linspace(mel(0),mel(sr/2),28));freq=np.linspace(0,sr/2,power.shape[1]);bank=[]
 for a,b,c in zip(edges,edges[1:],edges[2:]):bank.append(np.maximum(0,np.minimum((freq-a)/(b-a),(c-freq)/(c-b))))
 mfcc=dct(np.log(power@np.asarray(bank).T+1e-9),type=2,norm='ortho',axis=1)[:,:13]
 median_db=float(np.percentile(db,90))
 return {'time':(np.arange(len(x))*hop+frame/2)/sr,'rms':rms,'db':db,'relative_db':db-median_db,'pitch_hz':pitch,'pitch_semitones':semitones,'voiced':voiced,'flatness':flat,'mfcc':mfcc,'voiced_fraction':float(voiced.mean()),'median_pitch_hz':center,'duration':len(y)/sr}

def compare(ref,practice,rwords,pwords):
 if [x['word'] for x in rwords]!=[x['word'] for x in pwords]:raise ValueError('Both recordings must align to the same transcript')
 events=[];rows=[]
 for i,(r,p) in enumerate(zip(rwords,pwords)):
  rs=(ref['time']>=r['start'])&(ref['time']<=r['end']);ps=(practice['time']>=p['start'])&(practice['time']<=p['end'])
  if not rs.any() or not ps.any():continue
  lo=max(0,i-1);hi=min(len(rwords),i+3)
  rd=max(.05,rwords[hi-1]['end']-rwords[lo]['start']);pd=max(.05,pwords[hi-1]['end']-pwords[lo]['start'])
  pace=rd/pd;energy=float(np.median(practice['relative_db'][ps])-np.median(ref['relative_db'][rs]))
  flat=float(np.median(practice['flatness'][ps])-np.median(ref['flatness'][rs]))
  rp=ref['pitch_semitones'][rs];pp=practice['pitch_semitones'][ps]
  pitch=float(np.nanmedian(pp)-np.nanmedian(rp)) if np.isfinite(rp).any() and np.isfinite(pp).any() else None
  row={'word':r['word'],'ref_start':r['start'],'ref_end':r['end'],'start':p['start'],'end':p['end'],'pace_ratio':float(pace),'energy_delta_db':energy,'flatness_delta':flat,'pitch_delta_semitones':pitch,'confidence':min(r['confidence'],p['confidence'])};rows.append(row)
 # Remove a robust whole-recording pitch offset across matched words.
 valid_pitch=[z['pitch_delta_semitones'] for z in rows if z['pitch_delta_semitones'] is not None and z['confidence']>.25]
 pitch_offset=float(np.median(valid_pitch)) if valid_pitch else 0
 for row in rows:
  if row['pitch_delta_semitones'] is not None:row['pitch_delta_semitones']-=pitch_offset
 # Merge adjacent flagged words into temporally grounded evidence regions.
 checks=[('pace','Pacing changes',lambda x:abs(np.log2(x['pace_ratio']))>.35),('energy','Energy drops',lambda x:x['energy_delta_db']<-7),('texture','Spectral texture changes',lambda x:x['flatness_delta']>.05),('pitch','Pitch pattern changes',lambda x:x['pitch_delta_semitones'] is not None and abs(x['pitch_delta_semitones'])>4)]
 for kind,title,predicate in checks:
  groups=[]
  for row in rows:
   if row['confidence']<.25 or not predicate(row):continue
   if groups and row['start']-groups[-1][-1]['end']<.5:groups[-1].append(row)
   else:groups.append([row])
  for g in groups:
   if len(g)<2:continue
   metrics={'pace_ratio':float(np.median([x['pace_ratio'] for x in g])),'energy_delta_db':float(np.median([x['energy_delta_db'] for x in g])),'flatness_delta':float(np.median([x['flatness_delta'] for x in g])),'pitch_delta_semitones':float(np.median([x['pitch_delta_semitones'] for x in g if x['pitch_delta_semitones'] is not None])) if any(x['pitch_delta_semitones'] is not None for x in g) else None}
   events.append({'kind':kind,'title':title,'start':g[0]['start'],'end':g[-1]['end'],'reference_start':g[0]['ref_start'],'reference_end':g[-1]['ref_end'],'words':' '.join(x['word'] for x in g),'metrics':metrics,'confidence':float(np.mean([x['confidence'] for x in g]))})
 for i in range(1,len(pwords)):
  pg=pwords[i]['start']-pwords[i-1]['end'];rg=rwords[i]['start']-rwords[i-1]['end']
  if pg-rg>.9 and min(pwords[i]['confidence'],pwords[i-1]['confidence'],rwords[i]['confidence'],rwords[i-1]['confidence'])>.25:events.append({'kind':'pause','title':'An extended pause','start':pwords[i-1]['end'],'end':pwords[i]['start'],'reference_start':rwords[i-1]['end'],'reference_end':rwords[i]['start'],'words':pwords[i]['word'],'metrics':{'pause_seconds':pg,'reference_pause_seconds':rg},'confidence':min(pwords[i]['confidence'],pwords[i-1]['confidence'])})
 # Acoustic-only fallback: texture can remain measurable when phonetic alignment fails.
 baseline=ref['flatness'][ref['relative_db']>-25]
 ceiling=float(np.percentile(baseline,95))+.05 if len(baseline) else 1.05
 ids=np.where((practice['flatness']>ceiling)&(practice['relative_db']>-25))[0]
 groups=[]
 for i in ids:
  if groups and practice['time'][i]-practice['time'][groups[-1][-1]]<=.20:groups[-1].append(int(i))
  else:groups.append([int(i)])
 acoustic_events=[]
 for g in groups:
  start=max(0,float(practice['time'][g[0]]-.02));end=min(practice['duration'],float(practice['time'][g[-1]]+.02))
  if end-start<.30:continue
  value=float(np.median(practice['flatness'][g]))
  acoustic_events.append({'kind':'texture','title':'Spectral texture changes','start':start,'end':end,'reference_start':0,'reference_end':ref['duration'],'words':'Acoustic evidence against the whole reference baseline.','metrics':{'flatness_delta':value-(ceiling-.05),'practice_flatness':value,'reference_flatness_p95':ceiling-.05,'threshold':ceiling,'basis':'recording-texture'},'confidence':0,'alignment_required':False})
 if acoustic_events:events=[e for e in events if e['kind']!='texture']+acoustic_events
 penalties={k:min(100,sum(e['end']-e['start'] for e in events if e['kind']==k)/max(practice['duration'],1)*100) for k in ['pace','energy','texture','pitch','pause']}
 weights={'pace':.30,'energy':.25,'texture':.15,'pitch':.15,'pause':.15}
 score=100-sum(penalties[k]*weights[k] for k in weights)
 return {'events':sorted(events,key=lambda x:x['start']),'word_evidence':rows,'rubric':{'comparison_score':round(score,1),'penalties':penalties,'weights':weights,'meaning':'Reference similarity under the documented acoustic rubric, not rhetorical quality or ability.'},'alignment_confidence':float(np.mean([x['confidence'] for x in rows])) if rows else 0}

def json_features(f):
 def convert(x):
  if isinstance(x,np.ndarray):return [convert(z) for z in x.tolist()]
  if isinstance(x,list):return [convert(z) for z in x]
  if isinstance(x,float) and not np.isfinite(x):return None
  return x
 return {k:convert(v) for k,v in f.items() if k!='mfcc'}
