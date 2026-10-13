## Inspiration
A student hears “improve your pacing” and has no idea which five seconds to rehearse. CadenceLab makes that moment visible. We chose **Track C** to build an auditable speech comparison tool: recordings, transcript, signal measurements and human-readable evidence all point to the same moment.

## What it does
Compare a reference and practice recording of the same English words. Select a delivery finding to inspect its interval, numerical reason and focused practice suggestion. Listen to either phrase, seek through transcript words and export the evidence as JSON. The interface preserves each recording’s own time axis rather than implying a uniform waveform stretch.

A working upload flow performs genuine acoustic inference and transcript-constrained forced alignment locally in a browser worker. Your recordings and transcript have no upload endpoint. First use downloads pinned model weights. No account or paid inference API is required.

## How we built it
React, Vite, Radix UI and self-hosted DM Sans power an editorial workbench. ONNX Runtime Web runs a pinned quantized Wav2Vec2 model. Its frame-level token probabilities feed a CTC Viterbi path through the supplied transcript, including blank states and repeated-character constraints. These are acoustic word timestamps, not equal spacing or ASR text timestamps.

Python/NumPy/SciPy extract FFT spectral texture, energy, autocorrelation F0, 13 MFCCs, pace and pauses. Matched-word comparisons center pitch in semitones and normalize recording energy. Each finding exposes its threshold and measured difference. The rubric is reproducible reference similarity, not a learned human grade.

When phonetic support becomes unreliable, independent frame-level noise evidence can produce a **partial report** with no word-based score. Otherwise the system abstains. Uncertainty is part of the experience.

## Dataset and evaluation
We built **90 paired cases** from five public archival excerpts, two speakers and three speeches. Each has three levels of five modifications—pace, local energy, pause, noise and pitch—plus unchanged, whole-recording gain and pitch controls. Injection labels come from exact sample boundaries independently of detector predictions. Source rights, hashes and construction scripts are documented.

At declared temporal IoU ≥ 0.30, **43/75** altered cases localized the target change; **40/50** moderate and strong cases matched. Mean temporal IoU including misses is **0.403**. **2/15** controls produced false regions; all ten unchanged/global-gain controls produced none. Four cases abstained completely and two returned partial reports. Every case remains in the results.

These are **development diagnostics on synthetic archival audio**, not held-out student accuracy. Historical English male speakers cannot validate fairness across accents, genders, devices or real rehearsal errors.

## Challenges and what we learned
Forced alignment becomes fragile under strong pitch shifts and noise. Alignment-only gain conditioning helps preserve phonetic support without erasing evidence from the original signal. Chunk context, true convolution frame centers and repeated letters matter. Comparing independently serialized audio also prevented silent differences between evaluation and deployed fixtures.

A real browser upload recovered three local energy regions. Its 94.8 similarity score matched Python, with at most 20 ms boundary differences. Five pipeline tests pass. Automated accessibility checks found no violations across four screens, no mobile overflow and no page errors. Security documentation describes the actual boundary and remaining resource-exhaustion limits; it is not a security certification.

## Impact and next steps
Students and coaches can turn broad feedback into a phrase they can replay and practice. Consent-based trials with real students, independent held-out recordings, broader accents/devices and human preference comparisons are the next validation steps. We do not diagnose speech disorders, infer emotions or judge persuasive truth.

## Team planning and AI disclosure
Proposed responsibility split for team confirmation: **Adeel Falak Sher**—product direction, interface and presentation; **Rauf Khalid**—dataset, evaluation and quality review. These are proposed roles, not a claim of completed human contributions.

AI assistance supported research, coding, documentation and review. Wav2Vec2 supplies acoustic probabilities; the original alignment, evidence, dataset and evaluation code is inspectable. Demo narration uses a disclosed stock synthetic voice. HyperFrames composes the real app recording, synchronized captions and audio into continuous 1080p video. No fabricated user study or benchmark is claimed.
