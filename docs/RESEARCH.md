# Track choice and verified requirements

Reviewed 13 October 2026. Event: https://multimodal-ai-hackathon-2026-7.devpost.com/
Rules: https://multimodal-ai-hackathon-2026-7.devpost.com/rules
Deadline: 14 October 2026 23:45 Asia/Karachi (15 October 00:15 IST).
One team, one track; 1–4 real-name members. Public GitHub and 3–10 minute YouTube video; unlisted accepted. English audio or subtitles. AI-assistance disclosure required.

| Track | Core work | Main execution risk | Assessment |
|---|---|---|---|
| A | Four clinical classifiers, anatomical 3D, SHAP/LIME | 303-record dataset; leakage, calibration and licensed anatomy | Feasible but medical validity and anatomy dominate |
| B | Raw Sentinel ingestion, historical OSM, road connectivity, EMSR927 comparison | Live arbitrary-area/date judging; credentials, satellite availability, geospatial preprocessing | Highest external-data and infrastructure risk |
| C | Contrastive speech dataset, forced alignment, acoustic features, temporal explanations | Recording rights, alignment confidence, synthetic-to-real generalization | Selected: repeatable perturbations and observable explanations suit rigorous prototype |
| D | Video/PDF/slide ingestion, multimodal RAG, quizzes, learner model, framework evaluation | Broad mandatory surface; model APIs and validated assessment generation | High integration burden and overlaps with user's separate education projects |

Track C weights: dataset engineering/stress testing 30%; temporal grounding/explanation 25%; acoustic features 20%; dashboard 15%; reproducibility 10%.
No track participation counts or probabilities of winning are known. Selection reflects execution fit, not a guaranteed award.
The overview lists first ₹15,000 and second ₹10,000 per track; Rules says one winner per track. Preserve this contradiction; do not promise a payout structure beyond the published information.

## Technical research
CTC forced alignment maps a supplied transcript to acoustic model emissions, rather than allocating word timestamps uniformly or treating ASR timestamps as exact alignment.
https://docs.pytorch.org/audio/2.1/tutorials/ctc_forced_alignment_api_tutorial.html
The quantized ONNX Wav2Vec2 model has one float input (`input_values`) and a 32-token logits output. Commit pinned: 40a7d3243922b1fcbf660285036ecc7ef52667ea.
https://huggingface.co/Xenova/wav2vec2-base-960h

Archive source candidates are historical public speeches. Public-domain status must be checked per recording, not inferred from being hosted by an archive. Modified versions will be labeled synthetic perturbations and not genuine performances.
https://commons.wikimedia.org/wiki/File:JFK_inaugural_address.ogg
https://www.fdrlibrary.org/utterancesfdr

## Product brief
CadenceLab: an evidence workbench for coaches and student speakers. Compare recordings of the same words, inspect precisely timed acoustic differences, listen to the evidence, and try a focused revision. Scores are transparent rubric measurements, not objective judgments of talent, accent, identity, health or rhetorical truth.
Design: warm paper, near-black ink, vermilion highlights, precise editorial typography. Transcript anchors and timelines take priority over decorative 3D.
