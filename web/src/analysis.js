import * as ort from 'onnxruntime-web/wasm';
import FFT from 'fft.js';
ort.env.wasm.numThreads=1;
ort.env.wasm.proxy=false;
let session;
const chars="<pad> <s> </s> <unk> | E T A O N I H S R D L U M W C F G Y P B V K ' X J Q Z".split(' ');
const vocabulary=Object.fromEntries(chars.map((c,i)=>[c,i]));
const modelURL='https://huggingface.co/Xenova/wav2vec2-base-960h/resolve/40a7d3243922b1fcbf660285036ecc7ef52667ea/onnx/model_quantized.onnx';
const median=a=>{const b=a.filter(Number.isFinite).sort((x,y)=>x-y);return b.length?(b[Math.floor(b.length/2)]+b[Math.floor((b.length-1)/2)])/2:0};
async function emissions(y,notify){
 if(!session){notify('Loading the speech model. First use downloads about 95 MB.');session=await ort.InferenceSession.create(modelURL,{executionProviders:['wasm']});}
 const pieces=[],times=[];
 for(let a=0;a<y.length;a+=64000){
  const b=Math.min(a+64000,y.length),lo=Math.max(0,a-8000),hi=Math.min(y.length,b+8000),x=y.slice(lo,hi);
  // Alignment-only AGC. Raw audio remains unchanged for feature evidence.
  let peak=0;for(const z of x)peak=Math.max(peak,Math.abs(z));for(let i=0;i<x.length;i++)x[i]/=Math.max(peak,1e-9);const first=x[0],last=x.at(-1),squares=new Float64Array(x.length+1);for(let i=0;i<x.length;i++)squares[i+1]=squares[i]+x[i]*x[i];for(let i=0;i<x.length;i++){const l=Math.max(0,i-800),h=Math.min(x.length,i+800),sum=squares[h]-squares[l]+Math.max(0,800-i)*first*first+Math.max(0,i+800-x.length)*last*last,local=Math.sqrt(sum/1600+1e-8);x[i]*=Math.max(.25,Math.min(20,.1/Math.max(local,.002)));}
  let mean=0;for(const z of x)mean+=z;mean/=x.length;let variance=0;for(const z of x)variance+=(z-mean)**2;const sd=Math.sqrt(variance/x.length+1e-7);for(let i=0;i<x.length;i++)x[i]=(x[i]-mean)/sd;
  const result=await session.run({input_values:new ort.Tensor('float32',x,[1,x.length])}),z=result.logits,n=z.dims[1];
  for(let f=0;f<n;f++){const t=(f*320+200)/16000+lo/16000;if(t<a/16000||t>=b/16000)continue;const row=Array.from(z.data.slice(f*32,f*32+32));const mx=Math.max(...row),sum=row.reduce((s,v)=>s+Math.exp(v-mx),0);pieces.push(row.map(v=>v-mx-Math.log(sum)));times.push(t);}
  notify(`Acoustic inference ${Math.round(b/y.length*100)}%`);
 }
 return {logp:pieces,times};
}
function transcriptError(logp,text){
 const target=text.replace(/[’‘]/g,"'").toUpperCase().replace(/[^A-Z' ]/g,' ').trim().replace(/\s+/g,' ').split(' ');let heard='',last=-1;
 for(const row of logp){let id=0;for(let k=1;k<32;k++)if(row[k]>row[id])id=k;if(id!==last&&id>3)heard+=chars[id];last=id;}
 const tokens=heard.replaceAll('|',' ').trim().split(/\s+/);let v=tokens.map((_,i)=>i);v.push(tokens.length);
 target.forEach((w,i)=>{const n=[i+1];tokens.forEach((z,j)=>n.push(Math.min(n.at(-1)+1,v[j+1]+1,v[j]+(w!==z?1:0))));v=n;});return v.at(-1)/Math.max(target.length,1);
}
function align(logp,times,transcript){
 const text=transcript.replace(/[’‘]/g,"'").toUpperCase().replace(/[^A-Z' ]/g,' ').trim().replace(/\s+/g,' '),letters=text.replaceAll(' ','|').split(''),labels=letters.map(c=>vocabulary[c]);
 const states=new Int16Array(2*labels.length+1);labels.forEach((x,i)=>states[2*i+1]=x);const S=states.length,T=logp.length;
 if(!labels.length||T<labels.length)throw Error('The transcript is too long or empty.');
 const back=new Uint8Array(S*T);let v=new Float32Array(S).fill(-Infinity);v[0]=logp[0][0];v[1]=logp[0][states[1]];
 for(let f=1;f<T;f++){const next=new Float32Array(S);for(let s=0;s<S;s++){let best=v[s],jump=0;if(s>0&&v[s-1]>best){best=v[s-1];jump=1;}if(s>1&&states[s]!==0&&states[s]!==states[s-2]&&v[s-2]>best){best=v[s-2];jump=2;}next[s]=best+logp[f][states[s]];back[f*S+s]=jump;}v=next;}
 let s=v[S-1]>v[S-2]?S-1:S-2;if(!Number.isFinite(v[s]))throw Error('This transcript could not be aligned.');const path=new Int16Array(T);
 for(let f=T-1;f>=0;f--){path[f]=s;s-=back[f*S+s];}
 const cells=letters.map((char,i)=>({char,start:Infinity,end:0,confidence:0,n:0}));
 for(let f=0;f<T;f++){const s=path[f];if(s%2){const c=cells[(s-1)/2];c.start=Math.min(c.start,times[f]-.01);c.end=times[f]+.01;c.confidence+=Math.exp(logp[f][states[s]]);c.n++;}}
 const words=[];let chunk=[];for(const c of [...cells,{char:'|'}]){if(c.char==='|'){if(chunk.length){words.push({word:chunk.map(x=>x.char).join(''),start:Math.max(0,chunk[0].start),end:chunk.at(-1).end,confidence:chunk.reduce((n,x)=>n+x.confidence/Math.max(x.n,1),0)/chunk.length});chunk=[];}}else{if(!c.n)throw Error('Incomplete transcript alignment.');chunk.push(c);}}
 return words;
}
function acoustic(y){
 const specFFT=new FFT(1024),specInput=new Float64Array(1024),specComplex=specFFT.createComplexArray();const fft=new FFT(2048),input=new Float64Array(2048),complex=fft.createComplexArray(),ifft=fft.createComplexArray(),time=[],db=[],pitch=[],flatness=[],waveform=[];
 for(let a=0;a+640<=y.length;a+=320){
  input.fill(0);let mean=0,rms=0;for(let k=0;k<640;k++){mean+=y[a+k];rms+=y[a+k]**2;}mean/=640;
  for(let k=0;k<640;k++)input[k]=y[a+k]-mean;
  specInput.fill(0);for(let k=0;k<640;k++)specInput[k]=y[a+k]*(.5-.5*Math.cos(2*Math.PI*k/639));specFFT.realTransform(specComplex,specInput);let logPower=0,sumPower=0,n=0;
  for(let k=4;k<320;k++){const power=specComplex[k*2]**2+specComplex[k*2+1]**2+1e-12;logPower+=Math.log(power);sumPower+=power;n++;}
  flatness.push(Math.exp(logPower/n)/(sumPower/n));fft.realTransform(complex,input);fft.completeSpectrum(complex);for(let k=0;k<2048;k++){complex[2*k]=complex[2*k]**2+complex[2*k+1]**2;complex[2*k+1]=0;}
  fft.inverseTransform(ifft,complex);let best=-1,lag=0;for(let k=32;k<246;k++){const score=ifft[2*k]/Math.max(ifft[0],1e-12);if(score>best){best=score;lag=k;}}
  const level=20*Math.log10(Math.sqrt(rms/640)+1e-12);pitch.push(best>.6?16000/lag:null);db.push(level);time.push((a+320)/16000);waveform.push(Math.sqrt(rms/640));
 }
 const sortedDb=[...db].sort((a,b)=>a-b),gate=Math.max(-65,sortedDb[Math.floor(db.length*.8)]-30);pitch.forEach((_,i)=>{if(db[i]<=gate)pitch[i]=null;});const pitchCenter=median(pitch.filter(x=>x!==null)),dbCenter=[...db].sort((a,b)=>a-b)[Math.floor(db.length*.9)];return {time,db,rms:waveform,relative_db:db.map(x=>x-dbCenter),pitch_hz:pitch,pitch_semitones:pitch.map(x=>x===null?null:12*Math.log2(x/Math.max(pitchCenter,1))),flatness,duration:y.length/16000,voiced_fraction:pitch.filter(x=>x!==null).length/pitch.length,median_pitch_hz:pitchCenter};
}
function slice(f,key,start,end){return f[key].filter((_,i)=>f.time[i]>=start&&f.time[i]<=end).filter(x=>x!==null);}
export function compare(ref,practice,rwords,pwords){
 const rows=[];for(let i=0;i<rwords.length;i++){const r=rwords[i],p=pwords[i];const lo=Math.max(0,i-1),hi=Math.min(rwords.length,i+3);const rd=Math.max(.05,rwords[hi-1].end-rwords[lo].start),pd=Math.max(.05,pwords[hi-1].end-pwords[lo].start),rp=slice(ref,'pitch_semitones',r.start,r.end),pp=slice(practice,'pitch_semitones',p.start,p.end);rows.push({word:r.word,start:p.start,end:p.end,ref_start:r.start,ref_end:r.end,pace_ratio:rd/pd,energy_delta_db:median(slice(practice,'relative_db',p.start,p.end))-median(slice(ref,'relative_db',r.start,r.end)),flatness_delta:median(slice(practice,'flatness',p.start,p.end))-median(slice(ref,'flatness',r.start,r.end)),pitch_delta_semitones:rp.length&&pp.length?median(pp)-median(rp):null,confidence:Math.min(r.confidence,p.confidence)});}
 const offset=median(rows.filter(r=>r.confidence>.25&&r.pitch_delta_semitones!==null).map(r=>r.pitch_delta_semitones));rows.forEach(r=>{if(r.pitch_delta_semitones!==null)r.pitch_delta_semitones-=offset;});const events=[],checks=[['pace','Pacing changes',r=>Math.abs(Math.log2(r.pace_ratio))>.35],['energy','Energy drops',r=>r.energy_delta_db<-7],['texture','Spectral texture changes',r=>r.flatness_delta>.05],['pitch','Pitch pattern changes',r=>r.pitch_delta_semitones!==null&&Math.abs(r.pitch_delta_semitones)>4]];
 for(const[k,title,test]of checks){const groups=[];for(const r of rows){if(r.confidence<.25||!test(r))continue;if(groups.length&&r.start-groups.at(-1).at(-1).end<.5)groups.at(-1).push(r);else groups.push([r]);}for(const g of groups){if(g.length<2)continue;events.push({kind:k,title,start:g[0].start,end:g.at(-1).end,reference_start:g[0].ref_start,reference_end:g.at(-1).ref_end,words:g.map(x=>x.word).join(' '),metrics:{pace_ratio:median(g.map(x=>x.pace_ratio)),energy_delta_db:median(g.map(x=>x.energy_delta_db)),flatness_delta:median(g.map(x=>x.flatness_delta)),pitch_delta_semitones:median(g.map(x=>x.pitch_delta_semitones).filter(x=>x!==null))},confidence:median(g.map(x=>x.confidence))});}}
 for(let i=1;i<pwords.length;i++){const pg=pwords[i].start-pwords[i-1].end,rg=rwords[i].start-rwords[i-1].end;if(pg-rg>.9&&Math.min(pwords[i].confidence,pwords[i-1].confidence,rwords[i].confidence,rwords[i-1].confidence)>.25)events.push({kind:'pause',title:'An extended pause',start:pwords[i-1].end,end:pwords[i].start,reference_start:rwords[i-1].end,reference_end:rwords[i].start,words:pwords[i].word,metrics:{pause_seconds:pg,reference_pause_seconds:rg},confidence:Math.min(pwords[i].confidence,pwords[i-1].confidence)});}
 const values=ref.flatness.filter((_,i)=>ref.relative_db[i]>-25).sort((a,b)=>a-b),ceiling=(values.length?values[Math.floor((values.length-1)*.95)]:1)+.05,groups=[];
 practice.time.forEach((t,i)=>{if(practice.flatness[i]<=ceiling||practice.relative_db[i]<=-25)return;if(groups.length&&t-practice.time[groups.at(-1).at(-1)]<=.20)groups.at(-1).push(i);else groups.push([i]);});
 const acousticEvents=groups.map(g=>{const start=Math.max(0,practice.time[g[0]]-.02),end=Math.min(practice.duration,practice.time[g.at(-1)]+.02),value=median(g.map(i=>practice.flatness[i]));return {kind:'texture',title:'Spectral texture changes',start,end,reference_start:0,reference_end:ref.duration,words:'Acoustic evidence against the whole reference baseline.',metrics:{flatness_delta:value-(ceiling-.05),practice_flatness:value,reference_flatness_p95:ceiling-.05,threshold:ceiling,basis:'recording-texture'},confidence:0,alignment_required:false};}).filter(e=>e.end-e.start>=.30);
 if(acousticEvents.length){for(let i=events.length-1;i>=0;i--)if(events[i].kind==='texture')events.splice(i,1);events.push(...acousticEvents);}
 const weights={pace:.3,energy:.25,texture:.15,pitch:.15,pause:.15},penalties=Object.fromEntries(Object.keys(weights).map(k=>[k,Math.min(100,events.filter(e=>e.kind===k).reduce((s,e)=>s+e.end-e.start,0)/practice.duration*100)]));const score=100-Object.keys(weights).reduce((s,k)=>s+weights[k]*penalties[k],0);
 return {events:events.sort((a,b)=>a.start-b.start),word_evidence:rows,rubric:{comparison_score:Math.round(score*10)/10,weights,penalties},words:pwords,features:practice,duration:practice.duration,alignment_confidence:median(rows.map(x=>x.confidence))};
}
self.onmessage=async({data})=>{try{const {reference,practice,transcript}=data;const notify=text=>self.postMessage({progress:text});notify('Analyzing reference recording');const r=await emissions(reference,notify);if(transcriptError(r.logp,transcript)>.55)throw Error('Reference audio has insufficient support for this transcript. Check the words or try a cleaner recording.');const rw=align(r.logp,r.times,transcript);notify('Analyzing practice recording');const p=await emissions(practice,notify);const practiceError=transcriptError(p.logp,transcript);const pw=align(p.logp,p.times,transcript);const rf=acoustic(reference),pf=acoustic(practice),result=compare(rf,pf,rw,pw);if(practiceError>.55||result.alignment_confidence<.35){result.events=result.events.filter(e=>e.metrics.basis==='recording-texture');if(!result.events.length)throw Error('Low-confidence transcript alignment. Check the transcript or try a cleaner recording.');result.status='partial';result.rubric.comparison_score=null;result.reason='Only acoustic texture can be reported; word alignment and scoring have insufficient support.';}self.postMessage({result,reference:{words:rw,features:rf,duration:reference.length/16000,transcript}});}catch(e){self.postMessage({error:e.message||String(e)});}};
