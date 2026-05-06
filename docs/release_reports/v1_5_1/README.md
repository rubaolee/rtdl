# RTDL v1.5.1 Candidate Docs

This directory is a candidate documentation package for the v1.5.1 Python+RTDL track. It is not a release action and does not change the current public release boundary by itself.

The proposed v1.5.1 surface documents `COLLECT_K_BOUNDED` as a documented experimental public-candidate for bounded candidate-id rows over Embree and OptiX. The current usage mode remains source-tree execution, for example `PYTHONPATH=src:. python -m unittest ...`.

Boundaries:

- not stable primitive promotion
- no public speedup wording
- no zero-copy wording
- no release tag action
- no whole-app speedup claim

Read:

- `collect_k_bounded.md` for the proposed primitive surface.
- `release_surface_gate.md` for the gate status and blocked actions.
