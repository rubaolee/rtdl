# Goal 158: RTDL-Plus-Python Demo Docs

## Why

RTDL v0.2.0 should not be presented only as a closed list of workload names.
The repo now has a small but concrete example of the broader user model:

- RTDL provides the geometry-query core
- Python provides surrounding application logic

That story needs to be documented clearly and consistently.

## Scope

- add the lit-ball demo to the release-facing example path
- explain the RTDL-plus-Python application model in high-level docs
- keep the honesty boundary explicit:
  - this is not a claim that RTDL v0.2.0 is a full rendering system
- get Claude review
- get Gemini audit
- write final consensus

## Acceptance

- the demo is visible from front-door docs and tutorials
- the `ray_tri_hitcount` feature home points readers to the demo
- the docs consistently say RTDL works well with Python user applications
- the docs consistently preserve the non-graphical / not-a-renderer boundary
- Claude review artifact saved
- Gemini review artifact saved
- Codex consensus saved
