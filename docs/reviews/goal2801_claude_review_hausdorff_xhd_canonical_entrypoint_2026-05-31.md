# Claude External Review: Goal2801 Hausdorff/X-HD v2.5 Canonical Entrypoint

Reviewer: Claude (external, read-only)
Date: 2026-05-31
Verdict: **accept-with-boundary**

---

## Scope

Independent review of the Goal2801 canonical Hausdorff/X-HD entrypoint against the six questions in the handoff. Files reviewed:

- `scripts/goal2801_hausdorff_xhd_v25_canonical_entrypoint.py`
- `tests/goal2801_hausdorff_xhd_v25_canonical_entrypoint_test.py`
- `src/rtdsl/v2_5_triton_app_migration.py`
- `docs/reports/goal2801_hausdorff_xhd_v2_5_canonical_entrypoint_2026-05-31.md`
- `docs/reports/goal2801_pod_artifacts/hausdorff_xhd_v25_canonical_entrypoint_4096.json`
- `docs/reports/goal2801_pod_artifacts/hausdorff_xhd_v25_canonical_entrypoint_4096.stdout`

No source files were modified.

---

## JSON Artifact vs. Report Cross-Check

| Metric | Report | JSON artifact |
| --- | ---: | ---: |
| Status | pass | `"status": "pass"` |
| Distance error | 0.0 | `"distance_error": 0.0` |
| CuPy grid elapsed | 0.004478 s | `0.004478201037272811` s |
| RTDL/OptiX elapsed | 0.649487 s | `0.6494873950723559` s |
| RTDL/CuPy ratio | 145.03× slower | `145.03310362053074` |
| RTDL uses RT cores | true | `"uses_rt_cores": true` |
| Exact match | true | `"matches_exact_baseline": true` |

All report values match the JSON artifact to the precision shown. The `.stdout` file is byte-identical to the `.json` artifact, confirming the script's `print(json.dumps(...))` and `write_text(json.dumps(...))` produced the same payload in the recorded pod run.

Both baseline and RTDL results return `direction: "b_to_a"`, `source_index: 472`, `target_index: 1183`, and `distance: 0.13528455701336056`, confirming the witness point pairs agree, not just the scalar distance.

---

## Review Questions

### Q1 — Does Goal2801 provide a real canonical exact Hausdorff entrypoint rather than another scattered method note?

**Yes.**

The script is a proper standalone entrypoint: it carries an explicit `GOAL2801_ENTRYPOINT_VERSION` string, a typed `run_goal2801_hausdorff_entrypoint()` function, a `main()` with argument parsing, and a `--output` flag that writes a structured JSON artifact. The manifest row in `v2_5_triton_app_migration.py` (line 322-328) records `canonical_harness_status: "ready_with_goal2801_canonical_exact_entrypoint"` for `hausdorff_xhd`. This is a single designated entrypoint, not a scattered method note.

### Q2 — Does the entrypoint compare the RTDL/OptiX exact witness path with the same-contract CuPy grid exact baseline?

**Yes.**

The script invokes exactly two paths with the same 4096×4096 point fixture and the same scenario parameters:

- Baseline: `hd.hausdorff_distance_2d(..., method="cupy_grouped_grid_rawkernel", warmup=1)` — CUDA-core CuPy grid, no RT cores, exact value.
- RTDL path: `hd.hausdorff_distance_2d_rt_grouped_adaptive_nearest_witness(a_points, b_points)` — OptiX backend, RT-core-accelerated, exact value.

The JSON confirms `"exact_value": true` for both paths. The witness pair and scalar distance are identical across paths. Same fixture, same contract, same exactness guarantee — this is a properly paired same-contract comparison.

### Q3 — Is the report honest that RTDL/OptiX is correct and uses RT cores but is much slower than CuPy grid on this 4K fixture?

**Yes, completely.**

The report states directly: "The first artifact shows the RTDL/OptiX path is correct and uses RT cores, but it is much slower than the CuPy grid baseline on the 4K fixture." The JSON records `rt_core_accelerated: true` inside the RTDL result block, and `rtdl_over_cupy_grid_elapsed_ratio: 145.03`, confirming 145× slowdown relative to the CuPy grid opponent. No speedup is implied or obscured. The report table shows the raw timing without normalization tricks. This is exemplary honesty.

One observation: `baseline.wrapper_elapsed_sec` (0.548 s) is approximately 120× the `baseline.elapsed_sec` (0.00448 s), reflecting the `warmup=1` JIT-compile pass dominating wall time. The entrypoint correctly uses the inner `elapsed_sec` field (from the returned result dataclass) for the ratio, not the wrapper time, which is the right choice for a same-contract hot-path comparison.

### Q4 — Does the manifest avoid overclaiming Triton, public speedup, X-HD paper reproduction, or native app customization?

**Yes, comprehensively.**

The `CLAIM_BOUNDARY` dict in the script has eight explicit `false` flags:

```
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
rtdl_beats_xhd_claim_authorized: false
rtdl_beats_cupy_grid_claim_authorized: false
broad_rt_core_speedup_claim_authorized: false
triton_speedup_claim_authorized: false
paper_reproduction_claim_authorized: false
native_engine_customization: false
```

All eight appear verbatim in the JSON artifact, confirming the runtime payload is not mutated. The manifest `next_action` field (line 327) additionally states: "keep Triton witness auto-selection blocked until it beats the same-contract CuPy grid opponent." The tiered manifest validation in `validate_v2_5_tiered_benchmark_manifest()` enforces `public_speedup_claim_authorized: False` as a hard error. No overclaiming on any axis.

### Q5 — Are app-specific Hausdorff/X-HD policies kept outside the native engine contract?

**Yes.**

The `hausdorff_xhd` app plan in `v2_5_triton_app_migration.py` (lines 131-156) carries an explicit `notes` field: "Do not add Hausdorff-specific native code; nearest-witness scoring remains generic point-nearest plus grouped reduction." The `native_engine_customization: false` boundary flag reinforces this. The entrypoint imports from `examples.v2_0.research_benchmarks.hausdorff_xhd`, keeping Hausdorff logic in examples/research space rather than embedded in the native engine or Triton continuation primitives. App-specific X-HD geometry policy is not present anywhere in the engine-side manifest row or validation logic.

### Q6 — Is clean-from-Git rerun correctly identified as pending before final evidence closure?

**Yes.**

The report states explicitly: "Focused tests, external review, consensus, and clean-from-Git pod validation are still pending at the time this report was first written." The report verdict is "accept-with-boundary pending external review and clean-from-Git rerun." The test file references a consensus document (`docs/reports/goal2801_hausdorff_xhd_v2_5_canonical_entrypoint_consensus_2026-05-31.md`) that does not yet exist in the repository at the time of this review, confirming the test suite is intentionally aspirational and designed to gate final closure once consensus is written and a clean-from-Git pod run is recorded.

---

## Additional Observations

1. **Witness pair agreement is stronger evidence than scalar distance alone.** The RTDL and CuPy paths return the same `source_index: 472`, `target_index: 1183`, and identical distance to full float64 precision. This rules out any numerical coincidence.

2. **Consensus document is the only open gate.** The `test_report_and_consensus_keep_boundary` test will fail until the consensus document is written. This is by design — the test enforces that final closure requires both external review and an explicit consensus artifact. This review document satisfies the external-review precondition; the consensus document should be written next.

3. **The 145× slowdown is expected for this fixture size.** At 4096×4096, the OptiX BVH build and adaptive-radius iteration overhead dominates against a single-pass CuPy grid kernel. The entrypoint does not attempt to hide this; it records and reports it directly. This is an appropriate baseline for the canonical record.

4. **`hausdorff_xhd` required operations include `grouped_argmax_witness`** (line 325 in `v2_5_triton_app_migration.py`), which is not in the Triton front-door or dispatcher-preview set. This is consistent with Triton auto-selection remaining blocked — the operation set for parity is not yet covered.

---

## Verdict

**accept-with-boundary**

All six review questions pass. The entrypoint is a genuine canonical record: it is honest about correctness, honest about the RT-core path being slower, names the same-contract CuPy grid opponent without elision, and carries a complete boundary dict that is preserved verbatim in the pod artifact. The manifest update is minimal and accurate. The JSON artifact is consistent with the report to full numeric precision.

Open items before final evidence closure:
1. Clean-from-Git pod rerun to replace the current locally-run artifact.
2. Consensus document (`goal2801_hausdorff_xhd_v2_5_canonical_entrypoint_consensus_2026-05-31.md`) incorporating this review.
3. Focused test suite pass against the completed consensus document.

None of these invalidate the current implementation. The entrypoint and boundary are correctly structured; only the evidence record needs a clean reproducibility stamp.
