Verdict: accept-with-boundary

This is an independent Gemini review, distinct from Codex.

Goal3593 provides clear and consistent evidence for the performance characteristics of RayJoin-style workloads on public CDB slices using both CuPy CUDA-core baselines and RTDL/OptiX prepared routes. The documentation, tests, and artifacts consistently reinforce strong claim boundaries, making the results suitable for internal guidance.

### Findings

1.  **Consistent Same-Contract Comparison Boundary (Severity: Low)**
    Goal3593 successfully preserves the same-contract comparison boundary between the CuPy CUDA-core baseline and RTDL/OptiX prepared routes. The `scripts/goal3593_rayjoin_public_cdb_cupy_same_contract_probe.py` script explicitly checks for count parity between the two implementations and raises a `RuntimeError` on mismatch, ensuring that performance is compared for identical results. The `docs/reports/goal3593_rayjoin_public_cdb_cupy_same_contract_a5000/summary.json` artifact and `docs/reports/goal3593_rayjoin_public_cdb_cupy_same_contract_probe_2026-06-06.md` report confirm that "All counts matched" across all tested cases. This is further validated by `tests/goal3593_rayjoin_public_cdb_cupy_same_contract_probe_test.py::test_a5000_artifact_is_checked_when_present`.

2.  **Generic and Safe `SegmentColumns2D` Support (Severity: Low)**
    The `SegmentColumns2D` support added to Goal3589, and utilized by Goal3593, is demonstrably safe and generic. The `scripts/goal3589_rayjoin_cupy_same_contract_baseline.py` includes a general-purpose `_segment_array` helper function capable of handling `SegmentColumns2D` objects. The `docs/reports/goal3593_rayjoin_public_cdb_cupy_same_contract_probe_2026-06-06.md` explicitly describes this as "hardened... to accept RTDL's generic `SegmentColumns2D` input layout." Critical validation is provided by `tests/goal3593_rayjoin_public_cdb_cupy_same_contract_probe_test.py::test_goal3589_cupy_segment_baseline_accepts_segment_columns`, which unit tests the successful conversion of `SegmentColumns2D` to a NumPy array.

3.  **Accurate Artifacts and Reports (Severity: Low)**
    Both the `docs/reports/goal3593_rayjoin_public_cdb_cupy_same_contract_a5000/summary.json` artifact and the `docs/reports/goal3593_rayjoin_public_cdb_cupy_same_contract_probe_2026-06-06.md` report accurately state the measured numbers and count-parity status. The numerical results in the markdown report align with the more precise data in the JSON artifact. Both documents consistently report "All counts matched" and the interpretations (e.g., PIP favoring CuPy, LSI/Overlay favoring RTDL/OptiX) are consistent with the quantitative data.

4.  **Clear README Route Guidance (Severity: Low)**
    The `examples/v2_0/research_benchmarks/spatial_rayjoin/README.md` provides clear and correct guidance by distinguishing between authored fixtures and bounded public CDB slices. It includes separate tables and justifications for recommended routes for each data type within the "Recommended Explicit Route Choice" section. This distinction is crucial for understanding the context and applicability of performance findings. This is further verified by `tests/goal3593_rayjoin_public_cdb_cupy_same_contract_probe_test.py::test_readme_documents_public_cdb_route_choice`.

5.  **Strong Claim Boundaries (Severity: Low)**
    The claim boundaries are robust and consistently articulated across all provided files. The `scripts/goal3593_rayjoin_public_cdb_cupy_same_contract_probe.py` output, `docs/reports/goal3593_rayjoin_public_cdb_cupy_same_contract_a5000/summary.json`'s `claim_boundary` object (with all relevant authorization flags set to `false`), the "Purpose" and "Boundary" sections of `docs/reports/goal3593_rayjoin_public_cdb_cupy_same_contract_probe_2026-06-06.md`, and the `README.md` all explicitly disclaim "RayJoin paper reproduction," "public RT-core speedup," "release," "automatic-dispatch," and "zero-copy" claims. This strong stance on boundaries effectively scopes the utility of the evidence to internal research and development.

6.  **Fixes Before Larger Performance Packet Inclusion (Severity: Medium)**
    Before this evidence is incorporated into a larger v2.8/v2.9 performance packet, the following should be addressed:
    *   **PIP Performance Disparity:** The `docs/reports/goal3593_rayjoin_public_cdb_cupy_same_contract_probe_2026-06-06.md` "Interpretation" notes that "PIP remains a case where a simple dense CuPy count baseline is faster than the current prepared RTDL/OptiX path at this bounded size." For a comprehensive performance packet, this gap should be further investigated and optimized for RTDL/OptiX, or a clear strategy for using the CuPy path in these specific scenarios must be firmly established and justified.
    *   **"Internal Evidence Only" Status:** The current report explicitly states its status as "internal evidence only" and "not release evidence." To be included in a release-facing performance packet, the underlying work needs to satisfy the broader criteria for release authorization.
    *   **Git Cleanliness for Artifact Generation:** The `git_status_short` field in the `summary.json` indicates the presence of untracked files during the artifact generation. While not impacting the reported numbers themselves, best practice for reproducible performance reporting dictates that artifacts should ideally be generated from a clean git working directory. This ensures maximum confidence in the reported data's context.

File references:
- `scripts/goal3593_rayjoin_public_cdb_cupy_same_contract_probe.py`
- `scripts/goal3589_rayjoin_cupy_same_contract_baseline.py`
- `tests/goal3593_rayjoin_public_cdb_cupy_same_contract_probe_test.py`
- `docs/reports/goal3593_rayjoin_public_cdb_cupy_same_contract_a5000/summary.json`
- `docs/reports/goal3593_rayjoin_public_cdb_cupy_same_contract_probe_2026-06-06.md`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/README.md`
