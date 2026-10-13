import unittest,sys,json
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'src'))
from acoustics import features,compare
from alignment import Aligner,VOCAB
class Contracts(unittest.TestCase):
 def test_ctc_repeated_letters_have_separate_states(self):
  # A hand-constructed emission lattice with blanks between repeated letters.
  ids=[0,VOCAB['A'],0,VOCAB['L'],0,VOCAB['L'],0,VOCAB['|'],0,VOCAB['A'],0]
  logits=np.full((len(ids),32),-12.0)
  for i,k in enumerate(ids):logits[i,k]=0
  words=Aligner.align(None,logits,np.arange(len(ids))*.02+.0125,'ALL A')
  self.assertEqual([w['word'] for w in words],['ALL','A'])
  self.assertLess(words[0]['end'],words[1]['start'])
  self.assertAlmostEqual(words[0]['start'],.0225,places=4)
 def test_gain_normalization_preserves_energy_contour(self):
  t=np.arange(16000*3)/16000;y=(.12+.04*np.sin(2*np.pi*t))*np.sin(2*np.pi*160*t)
  a,b=features(y),features(y*.5)
  np.testing.assert_allclose(a['relative_db'],b['relative_db'],atol=.001)
  self.assertAlmostEqual(a['median_pitch_hz'],b['median_pitch_hz'],places=2)
  self.assertEqual(a['mfcc'].shape[1],13)
 def test_identical_evidence_has_no_findings(self):
  t=np.arange(16000*3)/16000;y=.15*np.sin(2*np.pi*160*t);f=features(y)
  w=[{'word':str(i),'start':i*.5,'end':i*.5+.4,'confidence':.95} for i in range(5)]
  r=compare(f,f,w,w);self.assertEqual(r['events'],[]);self.assertEqual(r['rubric']['comparison_score'],100)
 def test_same_text_is_required(self):
  f=features(np.ones(16000,dtype=np.float32)*.1)
  with self.assertRaises(ValueError):compare(f,f,[{'word':'A'}],[{'word':'B'}])
 def test_corpus_integrity_and_truth_boundaries(self):
  import hashlib,soundfile as sf
  d=Path(__file__).resolve().parent.parent/'web/public/dataset'
  cases=json.loads((d/'manifest.json').read_text());self.assertEqual(len(cases),90)
  for c in cases:
   x=json.loads((d/(c['id']+'.json')).read_text());wav=d/x['audio']
   self.assertEqual(hashlib.sha256(wav.read_bytes()).hexdigest(),x['sha256'])
   info=sf.info(wav);self.assertEqual(info.samplerate,16000);self.assertEqual(info.channels,1)
   for g in x['ground_truth']:self.assertTrue(0<=g['start']<g['end']<=info.duration+.03)
   for w in x['words']:self.assertTrue(0<=w['start']<=w['end']<=info.duration+.03)
   if x['status']=='abstained':self.assertIsNone(x['rubric']['comparison_score'])
if __name__=='__main__':unittest.main()
