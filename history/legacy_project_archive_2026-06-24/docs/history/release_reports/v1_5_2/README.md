# RTDL v1.5.2 Candidate Docs

This directory is a candidate documentation package for the v1.5.2 Python+RTDL
track. It is publicly discoverable after Goal1458 public-doc-link review, but
it is not a release action and does not change the current public release
boundary by itself.

The proposed v1.5.2 surface documents prepared host-output evidence for
`COLLECT_K_BOUNDED` as a documented experimental evidence candidate. The
evidence gate is `evidence_complete_claims_blocked`: prepared host-output
contract evidence is complete, but claim-specific gates remain closed.

Boundaries:

- prepared_buffer_reuse_proven remains False
- not stable primitive promotion
- no public speedup wording
- no zero-copy wording
- no whole-app claims
- no release tag action
- external release-surface review accepted
- public docs link accepted
- publicly discoverable

Read:

- `prepared_host_output_buffers.md` for the candidate evidence surface.
- `release_surface_gate.md` for the gate status and blocked actions.

Source-tree usage remains the supported usage style, for example:

```bash
PYTHONPATH=src:. python -m unittest tests.goal1455_v1_5_2_prepared_host_output_external_review_gate_test
```
