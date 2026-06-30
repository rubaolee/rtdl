# Goal 255 Report: Front Page Rewrite (2026-04-11)

Date: 2026-04-11
Status: implemented

## Proposal Basis

This rewrite was based on a 3-AI proposal round:

- Codex proposal:
  - `docs/reports/goal255_front_page_rewrite_codex_proposal_2026-04-11.md`
- Gemini proposal:
  - `docs/reports/gemini_goal255_front_page_proposal_2026-04-11.md`
- Claude proposal:
  - `docs/reports/claude_goal255_front_page_proposal_2026-04-11.md`

The converged direction is recorded in:

- `docs/reports/goal255_front_page_proposal_consensus_2026-04-11.md`

## What Changed

`README.md` was rewritten to:

- lead with a one-screen RTDL identity
- surface the fastest safe first-run path near the top
- present the visual demo as a proof-of-capability application rather than as a
  defensive disclaimer
- make `v0.4.0` the explicit current release
- list the live released workload surface accurately, including the
  nearest-neighbor additions
- compress historical/research detail so it no longer dominates the front door

## Verification

Repository-root commands still work as written:

- `PYTHONPATH=src:. python3 examples/rtdl_hello_world.py`
- `PYTHONPATH=src:. python3 examples/rtdl_segment_polygon_hitcount.py --backend cpu_python_reference --copies 2`

Both passed.

Link sanity:

- internal `docs/...` and `examples/...` links referenced by the new README were
  checked against the live repo filesystem

## Intended Result

The front page should now feel:

- more correct
- more consistent
- more professional
- easier for a new user to scan

while preserving RTDL's honesty boundary and current `v0.4.0` release state.
