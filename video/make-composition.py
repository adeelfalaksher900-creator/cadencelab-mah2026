import json,html,shutil
from pathlib import Path
p=Path(__file__).resolve().parent;q=p/'composition';words=json.loads((p/'edited-words.json').read_text());timing=json.loads((p/'production-timing.json').read_text());shutil.copy(p/'narration-edited.wav',q/'assets/narration.wav')
groups=[]
for w in words:
 if not groups or len(groups[-1])>=6 or w['start']-groups[-1][-1]['end']>.25:groups.append([])
 groups[-1].append(w)
clips=[];tweens=[]
for i,g in enumerate(groups):
 start=g[0]['start'];end=g[-1]['end'];text=' '.join(w['word'].lower() for w in g)
 clips.append(f'<div id="cap{i}" class="caption clip" data-start="{start:.4f}" data-duration="{end-start:.4f}" data-track-index="4"><span>{html.escape(text)}</span></div>');tweens.append(f'tl.from("#cap{i}",{{opacity:0,y:8,duration:.1,ease:"sine.out"}},{start});tl.set("#cap{i}",{{opacity:0}},{end});')
data=json.loads((p.parent/'web/public/dataset/obama-20170114-1-energy-2.json').read_text());e=data['events'][1];shutil.copy(p.parent/'web/public/dataset/obama-20170114-1-reference.flac',q/'assets/reference.flac');shutil.copy(p.parent/'web/public/dataset/obama-20170114-1-energy-2.flac',q/'assets/practice.flac')
text='''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><script src="assets/gsap.min.js"></script><style>
@font-face{font-family:"DM Sans";src:url('assets/dm-sans.woff2')}*{box-sizing:border-box}body{margin:0;width:1920px;height:1080px;overflow:hidden;background:#F8F6F1;font-family:"DM Sans",sans-serif;color:#202422}.scene,.clip{position:absolute;inset:0;width:1920px;height:1080px}.scene-content{width:100%;height:100%;padding:140px 140px;display:flex;flex-direction:column;justify-content:center;gap:34px}.kicker{color:#247D79;font-size:26px;letter-spacing:.12em}.title{font-family:Georgia,serif;font-size:112px;line-height:1.1;margin:0;max-width:1500px}.sub{font-size:37px;line-height:1.4;max-width:1400px;margin:0}.line{height:3px;width:160px;background:#B7482D}.scene{background:#F8F6F1}#intro{z-index:5}#outro{z-index:6;opacity:0}.caption{z-index:10;top:auto;bottom:86px;height:90px;display:flex;align-items:center;justify-content:center;padding:0 150px;text-align:center;font-size:44px;line-height:1.25;max-width:1920px}.caption span{max-width:1600px;padding:14px 26px;color:#F8F6F1;background:#202422;border-radius:5px}.listen{z-index:11;top:42px;left:120px;right:auto;bottom:auto;width:520px;height:72px;background:#F8F6F1;color:#247D79;padding:15px 22px;font-size:30px;border:1px solid #247D79}video{object-fit:contain} .footer{font-size:23px;color:#626760}
</style></head><body><div id="root" data-composition-id="cadence-demo" data-start="0" data-duration="303" data-width="1920" data-height="1080" data-fps="30">
<video id="app" class="clip" data-start="0" data-duration="303" data-track-index="0" src="assets/app-footage.mp4" muted playsinline></video>
<audio id="voice" data-start="0" data-duration="AUDIO_DURATION" data-track-index="2" src="assets/narration.wav" data-volume="1"></audio>
<div id="intro" class="scene"><div class="scene-content"><div class="kicker">MULTIMODAL AI HACKATHON / TRACK C</div><h1 class="title">Hear the difference.<br>See the evidence.</h1><div class="line"></div><p class="sub">CadenceLab — a local speech evidence workbench.</p></div></div>
<div id="outro" class="scene"><div class="scene-content"><div class="kicker">CADENCELAB</div><h1 class="title">Practice the moment.<br>Keep the evidence.</h1><div class="line"></div><p class="sub">Working browser inference · 90 labeled pairs · Transparent evaluation</p><p class="footer">Stock synthetic narration disclosed. Development diagnostics; broader validation remains necessary.</p></div></div>
CAPTIONS
<audio id="reference" data-start="REF_START" data-duration="REF_DUR" data-media-start="REF_OFFSET" data-track-index="3" src="assets/reference.flac" data-volume="1"></audio>
<audio id="practice" data-start="PRA_START" data-duration="PRA_DUR" data-media-start="PRA_OFFSET" data-track-index="3" src="assets/practice.flac" data-volume="1"></audio>
<div id="ref-label" class="clip listen" data-start="REF_START" data-duration="REF_DUR" data-track-index="5">Listen: reference phrase</div><div id="pra-label" class="clip listen" data-start="PRA_START" data-duration="PRA_DUR" data-track-index="5">Listen: quieter practice phrase</div>
</div><script>window.__timelines=window.__timelines||{};const tl=gsap.timeline({paused:true});
tl.from('#intro .kicker',{opacity:0,x:-25,duration:.5,ease:'sine.out'},.15);tl.from('#intro .title',{opacity:0,y:30,duration:.7,ease:'power2.out'},.3);tl.from('#intro .line',{scaleX:0,duration:.5,ease:'expo.out'},.55);tl.from('#intro .sub',{opacity:0,y:18,duration:.6,ease:'power3.out'},.7);
tl.to('#intro',{opacity:0,duration:.7,ease:'sine.inOut'},5.3);tl.from('#app',{opacity:0,duration:.7,ease:'sine.inOut'},5.3);
tl.to('#outro',{opacity:1,duration:.7,ease:'sine.inOut'},296);tl.from('#outro .kicker',{opacity:0,x:-20,duration:.5,ease:'sine.out'},296.2);tl.from('#outro .title',{opacity:0,y:25,duration:.7,ease:'power2.out'},296.4);tl.from('#outro .line',{scaleX:0,duration:.5,ease:'expo.out'},296.6);tl.from('#outro .sub',{opacity:0,y:20,duration:.6,ease:'power3.out'},296.8);tl.from('#outro .footer',{opacity:0,duration:.6,ease:'sine.out'},297);
TWEENS
window.__timelines['cadence-demo']=tl;</script></body></html>'''
replace={'AUDIO_DURATION':str(timing['audio_duration']),'CAPTIONS':'\n'.join(clips),'TWEENS':'\n'.join(tweens),'REF_START':str(timing['listen_start']),'PRA_START':str(timing['practice_start']),'REF_OFFSET':str(e['reference_start']),'PRA_OFFSET':str(e['start']),'REF_DUR':str(e['reference_end']-e['reference_start']),'PRA_DUR':str(e['end']-e['start'])}
for k,v in replace.items():text=text.replace(k,v)
(q/'index.html').write_text(text);print(len(groups),'caption groups')
# Separate captions for YouTube/manual review.
def stamp(t):return f'{int(t//3600):02}:{int(t//60%60):02}:{int(t%60):02},{round(t%1*1000):03}'
(p/'captions.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(g[0]["start"])} --> {stamp(g[-1]["end"])}\n'+ ' '.join(w['word'].lower() for w in g) for i,g in enumerate(groups)))
