# Using CadenceLab

CadenceLab helps a speaker or coach locate measurable differences between two recordings of the **same English words**. It is a practice aid, not a talent grade or clinical assessment.

## Explore a public example

Open **Compare**, choose **Try a labeled example**, then pick a reference and a controlled example. Examples load when a selection changes. They are synthetic modifications of public archival recordings, not recordings of student mistakes.

The finding list describes changes in pacing, relative energy, pauses, pitch patterns or spectral texture. Select a finding to see its interval and numerical reason. Listen to each corresponding phrase before deciding what to practice. Each recording retains its own time axis; an interval at five seconds in one file need not start at five seconds in the other.

Use the relative-energy, normalized-pitch and waveform-envelope tabs to inspect different measurements. Transcript words seek within the relevant recording. Exported JSON contains the analysis and its limitations; it does not include an uploaded audio file.

## Compare your own recordings

1. Record a reference and a practice version of the same passage. Use recordings you have permission to analyze.
2. Choose **Compare recordings** and select both files. Each must be **3–60 seconds** and **below 20 MB**. A modern browser must support their audio codec; WAV is a useful fallback if decoding fails.
3. Paste one shared English transcript, up to **3,000 characters**, using Latin characters. Spell out numbers. A materially different or inaccurate transcript weakens alignment.
4. Select **Run local comparison**. First use downloads about **95 MB** of pinned model weights. Analysis runs in a browser worker and can take time on slower devices.
5. Inspect and listen to the resulting findings. To return to the corpus, load a labeled example.

## Understand the result

The score is similarity to the reference under explicit acoustic weights, not a learned human judgment. A high score does not prove an effective speech; a lower score can reflect a deliberate stylistic difference. Whole-recording volume and pitch are normalized, but those controls can still expose limitations, especially in pitch tracking and alignment.

A partial report may show independent noise evidence while withholding a word-based score. Insufficient evidence means the app declines to invent word correspondence. Try a shorter, clearer passage with an exact transcript. Do not interpret either state as a judgment about the speaker.

## Troubleshooting

| Situation | What to try |
|---|---|
| Model download fails | Check connectivity and whether the model host is reachable. No API key is required. |
| Unsupported audio file | Export a short WAV file and try again. |
| Transcript rejected | Use English Latin characters, spell out digits and stay within 3,000 characters. |
| Low alignment support | Check that both recordings actually contain the shared transcript; reduce noise and shorten the passage. |
| Analysis takes a long time | Allow the first model download to finish, close resource-heavy tabs or use **Cancel analysis**. |
| No finding appears | The measured differences may stay below the stated thresholds. Listen to the pair; absence of findings is not proof of identical delivery. |

## Privacy and scope

Audio and transcript are decoded and analyzed locally; there is no audio-upload endpoint, account, database or telemetry. Hosting and model providers receive ordinary asset requests. Browser extensions and compromised devices are outside this boundary. Use **Method** and `docs/SECURITY.md` for details.

The 90-case evaluation uses synthetic changes to historical English recordings from two male speakers. It does not establish fairness or accuracy for real students, other languages, accents, genders or devices. Consent-based, independent validation is future work.
