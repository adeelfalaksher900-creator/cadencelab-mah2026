"""Recompute evidence from serialized audio and check transcript support."""
from pathlib import Path
import json
import soundfile as sf
from alignment import Aligner
from acoustics import features, compare, json_features
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'web/public/dataset'
a=Aligner()
refs=json.loads((OUT/'references.json').read_text())
manifest=json.loads((OUT/'manifest.json').read_text())
for ref in refs:
 y,sr=sf.read(OUT/ref['reference_file'],dtype='float32')
 rf=features(y);lp,t=a.emissions(y);rw=a.align(lp,t,ref['transcript'])
 ref['words']=rw;ref['features']=json_features(rf)
 ref['transcript_error']=a.transcript_error(lp,ref['transcript'])
 for case in [c for c in manifest if c['reference_id']==ref['id']]:
  p=OUT/(case['id']+'.json');x=json.loads(p.read_text())
  wave,sr=sf.read(OUT/x['audio'],dtype='float32')
  lp,t=a.emissions(wave);pw=a.align(lp,t,ref['transcript']);pf=features(wave)
  result=compare(rf,pf,rw,pw);wer=a.transcript_error(lp,ref['transcript'])
  result['transcript_error']=wer
  result['status']='abstained' if wer>.55 or result['alignment_confidence']<.35 else 'analyzed'
  if result['status']=='abstained':
   result['events']=[e for e in result['events'] if e['metrics'].get('basis')=='recording-texture'];result['status']='partial' if result['events'] else 'abstained';result['rubric']['comparison_score']=None
   result['reason']='Insufficient acoustic support for the transcript; try cleaner audio.'
  x.update(result);x['words']=pw;x['features']=json_features(pf)
  p.write_text(json.dumps(x,allow_nan=False,separators=(',',':')))
  print(x['id'],result['status'],len(result['events']),round(wer,2),flush=True)
refs.sort(key=lambda r:(r['speaker']!='Barack Obama',r['id']))
(OUT/'references.json').write_text(json.dumps(refs,allow_nan=False,separators=(',',':')))
