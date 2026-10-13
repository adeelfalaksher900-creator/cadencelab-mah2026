"""Evaluation against injection labels, including misses and abstentions."""
from pathlib import Path
from collections import defaultdict
import json,numpy as np
ROOT=Path(__file__).resolve().parent.parent
D=ROOT/'web/public/dataset'
cases=[json.loads((D/(x['id']+'.json')).read_text()) for x in json.loads((D/'manifest.json').read_text())]
rows=[]
for x in cases:
 truth=x['ground_truth'];pred=x.get('events',[])
 if not truth:
  rows.append({'id':x['id'],'kind':x['kind'],'severity':0,'control':True,'regions':len(pred),'abstained':x.get('status')=='abstained','partial':x.get('status')=='partial','score':x['rubric']['comparison_score']});continue
 g=truth[0];grid=np.arange(0,x['duration'],.01)
 gold=(grid>=g['start'])&(grid<=g['end']);mask=np.zeros(len(grid),bool)
 for e in pred:
  if e['kind']==g['kind']:mask|=(grid>=e['start'])&(grid<=e['end'])
 union=(gold|mask).sum();intersection=(gold&mask).sum()
 iou=float(intersection/max(union,1))
 relevant=[e for e in pred if e['kind']==g['kind']]
 boundary=None
 if relevant:
  boundary=(abs(min(e['start'] for e in relevant)-g['start'])+abs(max(e['end'] for e in relevant)-g['end']))/2
 rows.append({'id':x['id'],'kind':x['kind'],'severity':x['severity'],'control':False,'iou':round(iou,4),'matched':iou>=.3,'time_precision':round(float(intersection/max(mask.sum(),1)),4),'time_recall':round(float(intersection/max(gold.sum(),1)),4),'boundary_mae_seconds':round(boundary,4) if boundary is not None else None,'other_type_regions':sum(e['kind']!=g['kind'] for e in pred),'abstained':x.get('status')=='abstained','partial':x.get('status')=='partial'})
groups=defaultdict(list)
for r in rows:
 if not r['control']:groups[(r['kind'],r['severity'])].append(r)
summaries=[]
for (kind,severity),r in sorted(groups.items()):
 summaries.append({'kind':kind,'severity':severity,'cases':len(r),'matched':sum(z['matched'] for z in r),'recall':round(np.mean([z['matched'] for z in r]),3),'mean_iou':round(np.mean([z['iou'] for z in r]),3),'abstained':sum(z['abstained'] for z in r)})
controls=[r for r in rows if r['control']];positives=[r for r in rows if not r['control']]
result={'benchmark':'CadenceLab controlled acoustic perturbations v1','cases':len(cases),'reference_excerpts':5,'speakers':2,'speeches':3,'definition':'A case matches when the union of detected same-type regions has temporal IoU >= 0.30 with its injected interval. All levels, misses and abstentions remain included. Metrics are development-set diagnostics, not held-out generalization estimates.','positive_cases':len(positives),'matched_cases':sum(r['matched'] for r in positives),'case_recall':round(np.mean([r['matched'] for r in positives]),3),'mean_iou':round(np.mean([r['iou'] for r in positives]),3),'control_cases':len(controls),'control_cases_with_regions':sum(r['regions']>0 for r in controls),'control_false_positive_rate':round(np.mean([r['regions']>0 for r in controls]),3),'abstentions':sum(r['abstained'] for r in rows),'partial_reports':sum(r['partial'] for r in rows),'control_abstentions':sum(r['abstained'] for r in controls),'moderate_strong_matches':sum(r['matched'] for r in positives if r['severity']>=2),'moderate_strong_cases':sum(r['severity']>=2 for r in positives),'groups':summaries,'limitations':['Two historical English-speaking men; no real-student or demographic validation.','No training or test split: thresholds and pipeline were developed with this synthetic benchmark.','Pitch shifts can create artifacts; pitch tracking can make octave errors.','Exact injection labels are ground truth for transformations, not human performance ratings.'],'per_case':rows}
(ROOT/'web/public/evaluation.json').write_text(json.dumps(result,indent=2))
(ROOT/'docs/evaluation.json').write_text(json.dumps(result,indent=2))
print(json.dumps({k:v for k,v in result.items() if k not in ['per_case','limitations','definition']},indent=2))
