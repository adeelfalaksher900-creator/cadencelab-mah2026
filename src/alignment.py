"""Quantized Wav2Vec2 emissions and transcript-constrained CTC Viterbi alignment."""
from pathlib import Path
import json,re
import numpy as np
import onnxruntime as ort
from scipy.ndimage import uniform_filter1d
ROOT=Path(__file__).resolve().parent.parent
VOCAB=json.loads((ROOT/'models/vocab.json').read_text())
class Aligner:
 def __init__(self):
  options=ort.SessionOptions();options.intra_op_num_threads=4;options.inter_op_num_threads=1
  self.session=ort.InferenceSession(str(ROOT/'models/wav2vec2-q8.onnx'),options,providers=['CPUExecutionProvider'])
 def emissions(self,y,sr=16000):
  """Use 4-second windows with 0.5s context; discard overlap emissions."""
  pieces=[];times=[];step=4*sr;context=sr//2
  for a in range(0,len(y),step):
   b=min(a+step,len(y));lo=max(0,a-context);hi=min(len(y),b+context)
   x=np.asarray(y[lo:hi],np.float32).copy()
   x/=max(float(np.max(np.abs(x))),1e-9)
   # Alignment-only AGC; original waveform stays untouched for acoustic evidence.
   local=np.sqrt(uniform_filter1d(x*x,size=1600,mode='nearest')+1e-8)
   x*=np.clip(.1/np.maximum(local,.002),.25,20)
   x=(x-x.mean())/np.sqrt(x.var()+1e-7)
   logits=self.session.run(None,{'input_values':x[None]})[0][0]
   tt=(np.arange(len(logits))*320+200)/sr+lo/sr
   keep=(tt>=a/sr)&(tt<b/sr);pieces.append(logits[keep]);times.extend(tt[keep])
  x=np.concatenate(pieces);x=x-x.max(axis=1,keepdims=True)
  return x-np.log(np.exp(x).sum(axis=1,keepdims=True)),np.asarray(times)
 def recognize(self,y):
  logp,t=self.emissions(y);return self.greedy(logp),logp,t
 def greedy(self,logp):
  ids=logp.argmax(axis=1);out=[];last=-1
  inv={i:c for c,i in VOCAB.items()}
  for i in ids:
   if i!=last and i>3:out.append(inv[int(i)])
   last=i
  return ''.join(out).replace('|',' ').strip()
 def align(self,logp,t,transcript):
  text=re.sub(r"[^A-Z' ]",' ',transcript.upper());text=' '.join(text.split())
  if not text:raise ValueError('Transcript has no supported English characters')
  labels=[VOCAB[c] for c in text.replace(' ','|')];states=np.zeros(2*len(labels)+1,dtype=np.int32);states[1::2]=labels
  T=len(logp);S=len(states)
  if T<len(labels)+sum(a==b for a,b in zip(labels,labels[1:])):raise ValueError('Transcript is too long for this recording')
  back=np.zeros((T,S),np.uint8);v=np.full(S,-np.inf);v[0]=logp[0,0];v[1]=logp[0,states[1]]
  skip=(states!=0)&(states!=np.roll(states,2));skip[:2]=False
  for frame in range(1,T):
   candidates=np.stack((v,np.r_[-np.inf,v[:-1]],np.r_[-np.inf,-np.inf,v[:-2]]))
   candidates[2,~skip]=-np.inf;back[frame]=candidates.argmax(axis=0);v=candidates.max(axis=0)+logp[frame,states]
  s=S-1 if v[-1]>v[-2] else S-2
  if not np.isfinite(v[s]):raise ValueError('Unable to align supplied transcript')
  path=np.zeros(T,np.int32)
  for frame in range(T-1,-1,-1):path[frame]=s;s-=int(back[frame,s])
  chars=[];dt=float(np.median(np.diff(t)))
  for i,c in enumerate(text.replace(' ','|')):
   ids=np.where(path==2*i+1)[0]
   if not len(ids):raise ValueError('Incomplete transcript alignment')
   chars.append({'char':c,'start':max(0,float(t[ids[0]]-dt/2)),'end':float(t[ids[-1]]+dt/2),'confidence':float(np.exp(logp[ids,labels[i]]).mean())})
  words=[];chunk=[]
  for c in chars+[{'char':'|'}]:
   if c['char']=='|':
    if chunk:words.append({'word':''.join(z['char'] for z in chunk),'start':chunk[0]['start'],'end':chunk[-1]['end'],'confidence':float(np.mean([z['confidence'] for z in chunk]))});chunk=[]
   else:chunk.append(c)
  return words

 def transcript_error(self,logp,transcript):
  target=transcript.split();heard=self.greedy(logp).split();v=list(range(len(heard)+1))
  for i,w in enumerate(target,1):
   n=[i]
   for j,z in enumerate(heard,1):n.append(min(n[-1]+1,v[j]+1,v[j-1]+(w!=z)))
   v=n
  return v[-1]/max(1,len(target))
