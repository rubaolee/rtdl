# Goal982 Claude Review

Date: 2026-04-26

Verdict: **ACCEPT**

## Scope

This review covers:

1. Whether the same-scale Embree graph timing baseline (`goal835_baseline_graph_analytics_graph_visibility_edges_gate_embree_graph_ray_bfs_and_triangle_when_available_2026-04-23.json`) is valid.
2. Whether moving `graph_analytics / graph_visibility_edges_gate` to `reject_current_public_speedup_claim` is conservative and arithmetically correct.
3. Whether public RTX speedup claims remain unauthorized.

---

## 1. Same-Scale Embree Graph Timing Baseline Validity

**VALID.**

### Scale parity

The artifact uses `copies=20000` for both the Embree baseline and the RTX phase comparison. The Goal978 audit table confirms the RTX phase for `graph_analytics / graph_visibility_edges_gate` was also measured at `copies=20000`. Both sides of the comparison are at the same scale.

### Correctness parity

The `_expected_summary` function derives counts analytically from `copies`:

| Field | Formula | copies=20000 | Actual |
|---|---|---:|---:|
| `bfs.discovered_edge_count` | 2 × copies | 40000 | 40000 ✓ |
| `bfs.discovered_vertex_count` | 2 × copies | 40000 | 40000 ✓ |
| `bfs.max_level` | 1 | 1 | 1 ✓ |
| `triangle_count.touched_vertex_count` | 3 × copies | 60000 | 60000 ✓ |
| `triangle_count.triangle_count` | copies | 20000 | 20000 ✓ |
| `visibility_edges.blocked_edge_count` | 3 × copies | 60000 | 60000 ✓ |
| `visibility_edges.visible_edge_count` | copies | 20000 | 20000 ✓ |

`correctness_parity: true` and `matches_analytic_expected: true` are set in the artifact.

### Timing

Three wall-clock samples collected: `[0.8391, 0.5529, 0.5672]`. Sorted: `[0.5529, 0.5672, 0.8391]`. Median (middle of 3) = `0.5672194170765579`. The artifact's `phase_seconds.native_query` equals this value exactly. The median computation is correct.

The first sample is ~48% higher than the subsequent two, consistent with a cold-start warm-up on the first run. Taking the median over three runs is the correct conservative approach (it is neither the fastest nor the slowest sample).

### Backend scope

The baseline is explicitly labeled as a non-OptiX Embree path (`source_backend: "embree"`). It measures the full unified graph RT summary path (BFS + triangle + visibility edges) in a single `run_app("embree", "all", ...)` call. This matches the same code path exercised by the RTX phase comparison, making it a valid same-semantics baseline.

---

## 2. reject_current_public_speedup_claim: Conservative and Arithmetically Correct

**CONSERVATIVE AND ARITHMETICALLY CORRECT.**

The Goal978 audit reports:

- RTX native phase: `1.583060 s`
- Fastest non-OptiX same-semantics baseline: `embree_graph_ray_bfs_and_triangle_when_available` = `0.567219 s`
- Reported ratio: `0.358306`

Arithmetic check: `0.567219 / 1.583060 = 0.35831` (the audit uses ratio = baseline_time / RTX_time). Reported value `0.358306` matches to 4 significant figures. ✓

The ratio is `0.358`, meaning RTX takes approximately **2.79× longer** than the Embree non-OptiX path at the same scale. Classifying this row as `reject_current_public_speedup_claim` is the correct and conservative outcome: RTX is materially slower, not faster.

There are three additional CPU-reference baselines (`cpu_python_reference_visibility_edges`, `cpu_python_reference_bfs`, `cpu_python_reference_triangle_count`) that lack comparable timing. The audit correctly flags these as warnings rather than treating the missing timing as evidence of RTX advantage. Rejecting on the available Embree comparison alone is conservative; if any of the missing CPU baselines were also timed, the rejection decision could only be confirmed or strengthened (CPU Python reference paths are unlikely to be slower than Embree).

---

## 3. Public RTX Speedup Claims Remain Unauthorized

**UNAUTHORIZED throughout.**

Every layer of the Goal982 artifact chain explicitly sets authorization to `False`:

| Location | Field | Value |
|---|---|---|
| `goal982_graph_same_scale_timing_repair.py` script output | `public_speedup_claim_authorized` | `False` |
| `goal835_baseline_…2026-04-23.json` artifact | `authorizes_public_speedup_claim` | `false` |
| Artifact notes (3 lines) | explicit disclaimer | "It does not authorize public RTX speedup claims." |
| `goal978_rtx_speedup_claim_candidate_audit_2026-04-26.md` | `public speedup authorized` (graph row) | `False` |
| `goal978_two_ai_consensus_2026-04-26.md` | `public RTX speedup claims authorized` | `0` |

The test suite also asserts `self.assertFalse(report["public_speedup_claim_authorized"])`, so any regression that accidentally sets the flag would cause a test failure.

---

## Additional Notes

- The test `test_cli_writes_report_without_mutating_baseline_by_default` verifies that the default (no `--write` flag) does not mutate the baseline artifact on disk. This correctly prevents accidental overwrites from a dry-run or CI execution.
- The artifact filename retains the `2026-04-23` date (original Goal835 artifact date). This is intentional: Goal982 updates the same artifact in place rather than creating a new one. The in-place update is gated by `--write` and the correctness parity check, so it is safe.
- The claim effect string in the report — "Graph now has a positive same-scale non-OptiX timing baseline; Goal978 can classify it by timing." — is accurate: prior to this goal, the graph row could not be classified by timing because no comparable Embree baseline existed.

---

## Summary

All three questions resolve cleanly:

1. **Baseline validity**: the Embree timing is same-scale, correctness-verified, and computed from a correctly taken median of three runs.
2. **reject_current_public_speedup_claim**: arithmetic is correct (ratio = 0.3583, RTX is 2.79× slower) and the conservative direction (rejection rather than claim).
3. **Public RTX speedup claims**: remain unauthorized at every layer of the artifact chain.

**ACCEPT.**
