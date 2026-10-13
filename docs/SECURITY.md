# Security and privacy boundary

CadenceLab is a static client application. The browser decodes audio, runs quantized inference and computes evidence in a worker. There is no application audio-upload API, account, secret-bearing backend, database or telemetry. User audio/transcripts are not sent to an inference server. Model and runtime asset downloads are external network requests; their hosts receive ordinary request metadata.

## Implemented controls

- Audio file byte limit: 20 MB each. Decoded duration: 3-60 seconds. Transcript: at most 3,000 characters; English Latin text with spelled-out numbers.
- Malformed audio, unsupported text, incomplete alignment and insufficient acoustic support produce visible errors or partial acoustic-only reports. Partial reports withhold the word-based score and transcript interactions.
- React text rendering escapes supplied text. No `dangerouslySetInnerHTML`, shell execution, remote user URL, dynamic executable transcription or server-side file path is derived from inputs.
- A worker keeps expensive inference off the interface. Cancel terminates it; generated Blob URLs are revoked on replacement/unmount.
- Pinned model revision, committed dependency lockfile, locally hosted fonts, Content Security Policy, `nosniff`, no-referrer policy, denied framing and disabled camera/microphone/geolocation permissions.
- CSP permits WebAssembly compilation via `wasm-unsafe-eval`, not general JavaScript `unsafe-eval`. Inline styling is allowed for accessible Radix controls. Model download hosts are restricted in `connect-src`.

## Verification and limits

`docs/browser-qa.json` records automated WCAG checks on Compare, Dataset, Method and Upload, mobile overflow checks, script-injection handling and observed GET-only requests in the tested local UI flows. `docs/upload-evidence.json` is a real upload-analysis export using public archival test files. It is not user-private audio. Dependency audit is recorded separately. These checks are not a penetration-test certification or a human accessibility study.

Browser decoders are trusted platform components; unknown codec vulnerabilities and compromised browsers/devices/extensions remain outside this boundary. File-size and post-decode duration bounds are not a hard guarantee against every compressed-media resource attack. Model downloads require memory and bandwidth, especially on low-end phones. No sensitive audio should be committed to a public repository.

Cloudflare RLS, D1 tenant isolation, authentication hardening and backend API scans were assessed for relevance and are not applicable to this architecture. No live Cloudflare resource or unrelated user project was changed. Adding a backend later requires a new threat model, request limits, tenant isolation and independent security review.
