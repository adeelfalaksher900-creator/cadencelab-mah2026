"""Download public input assets. No credentials or paid API required."""
from pathlib import Path
import urllib.request,hashlib,json
ROOT=Path(__file__).resolve().parent.parent
PIN='40a7d3243922b1fcbf660285036ecc7ef52667ea'
assets={
 'models/wav2vec2-q8.onnx':f'https://huggingface.co/Xenova/wav2vec2-base-960h/resolve/{PIN}/onnx/model_quantized.onnx',
 'models/vocab.json':f'https://huggingface.co/Xenova/wav2vec2-base-960h/resolve/{PIN}/vocab.json',
 'models/config.json':f'https://huggingface.co/Xenova/wav2vec2-base-960h/resolve/{PIN}/config.json',
 'data/jfk.wav':'https://huggingface.co/datasets/Xenova/transformers.js-docs/resolve/159e0fd398b57d12a34e6a01e426e9e416ffce30/jfk.wav',
 'data/obama-20170114.mp3':'https://obamawhitehouse.archives.gov/videos/2017/January/20170114_Weekly_Address.mp3',
 'data/obama-20170107.mp3':'https://obamawhitehouse.archives.gov/videos/2017/January/20170107_Weekly_Address.mp3',
}
receipts=[]
for name,url in assets.items():
 path=ROOT/name;path.parent.mkdir(parents=True,exist_ok=True)
 if not path.exists():
  with urllib.request.urlopen(url,timeout=90) as src,path.open('wb') as dst:
   while block:=src.read(1024*1024):dst.write(block)
 receipts.append({'file':name,'source':url,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
 print(name,path.stat().st_size)
(ROOT/'docs/input-provenance.json').write_text(json.dumps(receipts,indent=2))
