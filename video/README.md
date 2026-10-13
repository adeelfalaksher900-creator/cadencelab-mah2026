# CadenceLab video production

The demo is a 303-second, 1920×1080 continuous capture of the actual app, composed at 30 fps with HyperFrames 0.8.151. It includes a genuine upload analyzed by the pinned Wav2Vec2 model, synchronized forced-aligned captions, and a two-phrase listening comparison at equal output volume.

Narration is a disclosed ElevenLabs stock synthetic voice, Liam, obtained through the free vidIQ allowance. It does not imitate a team member. No paid video generator was used.

## Reproduce

1. Install Python requirements and web dependencies, download the pinned inputs and build the web app as described in the root README.
2. Obtain or record narration matching `narration.txt`, and save it as `video/narration.mp3`.
3. Run `python tools/prepare_voice.py` to create word timings and insert the listening gap.
4. Install Playwright and its FFmpeg recorder. Supply your Chromium path in `record-app.cjs`. Run the local test server and recorder together. The recorder uses a local HTTP mirror of the exact pinned model for network-independent testing; inference is genuine.
5. Use the measured `preRoll` in the recording receipt to trim browser startup. Never infer startup from total duration, because recorder closure adds trailing frames. Use the receipt and transcode silent 1080p footage to `composition/assets/app-footage.mp4`.
6. Copy GSAP 3.14.2 and the self-hosted DM Sans font to the asset paths declared in the composition. Run `python video/make-composition.py`.
7. In `video/composition`, run `npm run check`, then `npm run render -- --fps 30 --quality high`.

Media binaries are delivery assets, excluded from source history. Caption timings and composition code are included. The generated caption groups account for the composition's length warning; runtime, layout, motion and contrast checks pass.

The reviewed production edit replaces 92–111 seconds with a second real capture of the same pause example, selecting the extended-pause finding. `record-pause.cjs` records this insert. Its audio remains the main edited narration; the listening comparison uses separate original phrase tracks.
