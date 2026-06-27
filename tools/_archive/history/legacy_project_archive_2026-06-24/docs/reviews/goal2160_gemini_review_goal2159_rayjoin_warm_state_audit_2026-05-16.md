# Goal2160 Gemini Review of Goal2159 RayJoin Warm-State Audit

Date: 2026-05-16

This is an independent Gemini review, distinct from Codex. This review does not authorize v2.0 release by itself.

## Review Questions

### 1. Does the committed runner provide a reproducible and bounded RayJoin public-CDB benchmark protocol?

**Answer:** Yes. The `scripts/goal2159_rayjoin_public_cdb_runner.py` script, along with its defined `CASES`, provides a structured, reproducible, and bounded benchmark protocol. It handles data sample downloading, deterministic slice materialization, and execution across specified backends with controlled warmups and repeats. The generation of detailed JSON artifacts further enhances reproducibility. The `tests/goal2159_rayjoin_public_cdb_runner_test.py` validates these aspects, confirming the runner's intent and functionality.

### 2. Does the Goal2159 report correctly narrow the public performance interpretation and avoid overclaiming the 5x warm-state number?

**Answer:** Yes. The `docs/reports/goal2159_rayjoin_public_cdb_runner_and_warm_state_audit_2026-05-16.md` explicitly addresses the warm-state sensitivity. It clearly differentiates between the conservative single-case result (OptiX 1.05x vs CPU) and the multi-case warm-state result (OptiX 5.28x vs CPU). The report unequivocally states that "public wording should use the conservative single-case result" until an explicit warm-state protocol is defined, effectively narrowing public performance claims and preventing overstatements. This correction is also reflected in `docs/reports/goal2157_rayjoin_public_cdb_nonzero_lsi_slice_evidence_2026-05-16.md` via a dedicated "Goal2159 Follow-Up Correction" section.

### 3. Are the claim-boundary flags and text conservative enough for v2.0 release preparation?

**Answer:** Yes. Both the `scripts/goal2159_rayjoin_public_cdb_runner.py` and the `docs/reports/goal2159_rayjoin_public_cdb_runner_and_warm_state_audit_2026-05-16.md` demonstrate a strong commitment to conservatism. The runner's generated artifacts include `claim_boundary` flags that are explicitly set to `false` for broad claims and `v2_0_release_authorized`. The report's "Claim Boundary" section meticulously lists what the goal does *not* authorize, including "v2.0 release authorization" and broad performance claims, thereby maintaining a highly conservative stance suitable for release preparation. The tests ensure these flags and phrases are consistently present.

### 4. Do the tests guard the correction and artifact assumptions adequately?

**Answer:** Yes. The test suite (`tests/goal2159_rayjoin_public_cdb_runner_test.py` and `tests/goal2159_rayjoin_public_cdb_runner_and_warm_state_audit_test.py`) adequately guards the correction and artifact assumptions. Tests confirm that slices are materialized correctly, claim boundary flags are present and correctly set (e.g., `v2_0_release_authorized` is `false`), and key textual assertions from the reports are maintained. Crucially, the tests load and examine the actual JSON artifacts to verify the observed warm-state sensitivity, ensuring that the numerical evidence supports the report's interpretations.

### 5. Does this remain consistent with the RTDL v2.0 rule that public performance claims require exact scope, same-contract comparison, and reviewed evidence?

**Answer:** Yes. This work strongly aligns with the RTDL v2.0 rule. The explicit definition of `CaseSpec` and `SliceSpec` within the runner script, along with the detailed discussion of single-case versus multi-case execution, ensures an exact scope for any performance claims. The consistent application of CPU, Embree, and OptiX backends under identical workload conditions (`run_rayjoin_workload`) constitutes a same-contract comparison. Finally, the generation of verifiable artifacts, the explicit "Claim Boundary" sections in the reports, and this independent review process itself exemplify the commitment to reviewed evidence.

## Verdict

**`accept-with-boundary`**

Goal2159 successfully implements a reproducible benchmark runner, clarifies the warm-state sensitivity of OptiX performance, and appropriately narrows the public interpretation of performance claims. The defined claim boundaries are conservative and well-supported by evidence and testing. This work is a solid step in preparing for v2.0 release by establishing clearer and more robust benchmarking protocols.
