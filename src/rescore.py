"""Reapply the transparent rubric to the saved acoustic/word evidence."""
from pathlib import Path
import json,numpy as np
from acoustics import compare
D=Path(__file__).resolve().parent.parent/'web/public/dataset'
def features(x):
 return {k:np.asarray(v,dtype=float) if isinstance(v,list) else v for k,v in x.items()}
refs={r['id']:r for r in json.loads((D/'references.json').read_text())}
for case in json.loads((D/'manifest.json').read_text()):
 p=D/(case['id']+'.json');x=json.loads(p.read_text());r=refs[x['reference_id']]
 result=compare(features(r['features']),features(x['features']),r['words'],x['words'])
 if x['transcript_error']>.55 or result['alignment_confidence']<.35:
  result['events']=[e for e in result['events'] if e['metrics'].get('basis')=='recording-texture'];result['rubric']['comparison_score']=None;x['status']='partial' if result['events'] else 'abstained';x['reason']='Only acoustic texture can be reported; word alignment and scoring have insufficient support.'
 x.update(result);p.write_text(json.dumps(x,allow_nan=False,separators=(',',':')))
