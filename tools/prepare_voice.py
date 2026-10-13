import sys,re,json,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import soundfile as sf
from src.alignment import Aligner
p=Path('video');subprocess.run(['ffmpeg','-y','-v','error','-i',str(p/'narration.mp3'),'-ar','16000','-ac','1',str(p/'narration.wav')],check=True)
y,sr=sf.read(p/'narration.wav');a=Aligner();paragraphs=(p/'narration.txt').read_text().strip().split('\n\n');text=' '.join(paragraphs).upper();text=re.sub(r'[^A-Z\x27 ]',' ',text);text=' '.join(text.split());logp,t=a.emissions(y);words=a.align(logp,t,text)
(p/'narration-words.json').write_text(json.dumps(words));n=0;times=[]
for s in paragraphs:
 k=len(re.sub(r'[^A-Z\x27 ]',' ',s.upper()).split()); times.append({'start':words[n]['start'],'end':words[n+k-1]['end'],'text':s});n+=k
cut=times[3]['end']+.12;gap=6.4;edited=__import__('numpy').concatenate([y[:round(cut*sr)],__import__('numpy').zeros(round(gap*sr)),y[round(cut*sr):]]);sf.write(p/'narration-edited.wav',edited,sr,subtype='PCM_16')
for w in words:
 if w['start']>=cut:w['start']+=gap;w['end']+=gap
(p/'edited-words.json').write_text(json.dumps(words));(p/'paragraph-timing.json').write_text(json.dumps(times,indent=2));(p/'production-timing.json').write_text(json.dumps({'duration':303,'audio_duration':len(edited)/sr,'listen_start':cut+.35,'practice_start':cut+3.1},indent=2));print(times);print('Voice aligned')
