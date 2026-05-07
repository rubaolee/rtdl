# COLLECT_K_BOUNDED Candidate Surface

`COLLECT_K_BOUNDED` is proposed for v1.5.1 as a documented experimental public-candidate in the Python+RTDL track.

Goal1421 accepted public documentation discoverability for this candidate package after 3-AI review. That acceptance is discoverability only: it is not stable primitive promotion, not public speedup wording, not zero-copy wording, not a whole-app claim, and not a release-tag action.

The primitive materializes bounded candidate-id rows with:

- explicit capacity `k`
- row layout `dense_candidate_id_rows_with_valid_count`
- canonical candidate-id rows
- fail-closed overflow behavior before partial result materialization
- active measured backend scope: Embree and OptiX

This candidate surface is for bounded candidate-id rows. It does not claim that row-returning applications are broadly accelerated, and it does not claim that the native engine is fully app-agnostic internally.

Evidence basis:

- contract and bounds tests
- native Embree and OptiX parity
- same-contract benchmarks
- Claude and Gemini external review

Forbidden claims:

- not stable primitive promotion
- no public speedup wording
- no zero-copy wording
- no whole-app claims
- no release tag action

Source-tree usage remains the supported usage style, for example:

```bash
PYTHONPATH=src:. python -m unittest tests.goal1418_v1_5_1_collect_k_readiness_gate_test
```
