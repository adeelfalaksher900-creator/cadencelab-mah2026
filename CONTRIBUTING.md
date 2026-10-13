# Contributing to CadenceLab

Thank you for helping make acoustic practice feedback easier to understand and verify.

## Choose a useful change

Good starting points include clearer documentation, keyboard and screen-reader access, browser compatibility, tests for acoustic edge cases, and independently evaluated alignment improvements. Open an issue before a large redesign or change to the scoring rubric so its purpose and evidence can be reviewed.

This hackathon version is tied to the published demo. Keep unrelated presentation changes out of fixes, and document behavior changes clearly. Never substitute precomputed results for the real upload inference path.

## Set up locally

1. Fork the repository, clone your fork and create a branch for one focused change.
2. Install Node 22.12+ or 24.x and npm.
3. Run `npm --prefix web ci`, then `npm --prefix web run dev` from the repository root.
4. Open the URL printed by Vite. The checked-in public examples work without Python or model downloads.

For Python work, use Python 3.12, create a virtual environment and install `requirements.txt`. Run `python tools/download_inputs.py` before model-dependent analysis. FFmpeg with the `atempo` and `rubberband` filters is needed to rebuild the modified audio corpus. Detailed commands and provenance are in the root README and `docs/DATASET.md`.

## Validate the change

- Frontend: run `npm --prefix web run build`. Exercise the affected flow with a real browser; check keyboard access, readable labels, mobile width and the browser console.
- Analysis or dataset: run `python -m unittest discover -s tests -p 'test_*.py'`. If thresholds, alignment or signals changed, run `python src/evaluate.py` and report all cases, including misses and abstentions.
- Documentation: check that paths, commands and stated results match the code. Do not rerun a large benchmark for a wording-only edit.

Browser verification scripts in `tests/` document the original environment and may need local Chromium paths adjusted. They are evidence and reproducible harnesses, not a promise that every machine has those binaries installed.

## Send a pull request

Explain the user problem, what changed, how you checked it and any remaining limitation. Include screenshots for UI changes and before/after case results for analysis changes. Keep the change small enough to review. Disclose AI-assisted changes and understand the submitted code. Do not commit model binaries, generated media, credentials, local environments or dependency directories.

## Respect data and licenses

Only contribute audio you have permission to distribute. Avoid private student recordings, names and consent forms in issues or commits. Synthetic transformations must remain clearly labeled. Separate detector predictions from ground-truth labels. The current corpus is a development benchmark, not a held-out real-student accuracy claim.

Application code is MIT licensed; third-party models, fonts and source recordings keep their own notices. By contributing, you agree to license your original code under the project license.
