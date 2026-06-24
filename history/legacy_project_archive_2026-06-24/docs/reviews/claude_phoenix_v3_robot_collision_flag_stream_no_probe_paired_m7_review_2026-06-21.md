---

# Critical Review — Phoenix V3 Robot Collision Flag-Stream No-Probe Paired RTX Evidence
**Date of review:** 2026-06-21  
**Packet files reviewed:**
- `phoenix_v3_robot_collision_flag_stream_no_probe_paired_rtx_evidence_2026-06-21.md`
- `phoenix_v3_robot_collision_flag_stream_no_probe_paired_rtx_evidence_2026-06-21.json`
- `evidence/phoenix_v3_robot_collision_flag_stream_no_probe_paired_20260621/summary.json`

---

## 1. Verdict

**Approve with amendments.**

The candidate wording is conditionally approved. Two P1 items must be resolved before M7 promotion: a triangle-count documentation error in the packet (does not affect public wording), and a required disclosure addition to the public wording regarding the scope of "prepared invocation" timing. No P0 blockers are present in the numeric claims or the structural separation of validation from performance timing.

---

## 2. Probe-Reference Separation — Acceptability for Row-Scoped M7

**Acceptable.** The protocol cleanly separates the two jobs:

- Validation rows use `no_probe_reference: false`. Both backends produce `probe_reference_validated: true`, identical signature hashes (`e68197e1...093`), and matching flagged-group counts (`5268 / 16384`) against the CPU oracle. The validation confirms the same collision result is produced regardless of backend.
- Timed rows use `--no-probe-reference` (`no_probe_reference: true`). Every timed payload shows `probe_reference_seconds: null` and `probe_reference_validated: false`, confirming the oracle is genuinely excluded.
- `validation_and_timed_signatures_overlap: true` and identical `validation_signature_hashes` and `timed_signature_hashes` in summary.json confirm both protocol arms test the same shape and produce the same flags.

The prior blocker (`probe_reference_dominates_wall_time`) is directly addressed. Validation probe-reference times (~373–374 s per backend) confirm why the prior end-to-end wall metric was uninformative for performance. The separation is methodologically sound for a row-scoped M7 claim.

---

## 3. Timing Definition Clarity

### Numeric verification

All five sample ratios were independently recomputed from raw payload values in summary.json:

| Metric | Claimed mean | Computed mean | Match |
|---|---:|---:|---|
| Tail prepared invocation speedup | 5.086x | 5.086008x | ✓ |
| Total-run window speedup | 5.075x | 5.074757x | ✓ |
| Wrapper no-probe speedup | 1.171x | 1.170747x | ✓ |
| Weakest wrapper speedup | 1.083x | 1.082787x (sample 2) | ✓ |

All five wrapper speedups are above 1x. All five tail and window speedups exceed 5x. Stddev is low for tail (0.037) and moderate for wrapper (0.050); the min-disclosing language in the candidate wording handles the wrapper variance correctly.

### Definition clarity — accepted with one required addition

The three metrics are defined:

- **Wrapper no-probe speedup**: runner-measured subprocess wall time with `--no-probe-reference`. Includes Python/app process overhead, app lowering (~0.81 s per backend), backend setup, all 101 repeat invocations, and JSON output. This is the most conservative, most comprehensive metric and directly verifiable from subprocess timing.
- **Total-run window**: `run_summary.total_run_seconds.total_sec` across 96 measured invocations.
- **Tail prepared invocation**: `tail_medians.total_run_seconds` after dropping 5 warmup rows.

These definitions are sufficiently clear for a row-scoped claim. However, there is a structural opacity that creates a **P1 concern** requiring a disclosure addition to the public wording:

**Phase-timing asymmetry (P1):** In the raw payload, `phase_window_sec.prepare_build` accumulates across repeats at very different magnitudes by backend:

| Backend | `prepare_build_window` | Inferred per-run | `total_run_window` / 96 |
|---|---:|---:|---:|
| Embree | 0.395 s | ~4.1 ms | ~11.3 ms |
| OptiX | 9.917 s | ~103 ms | ~2.24 ms |

The OptiX `prepare_build_window` of 9.9 s is physically impossible to fit inside the OptiX subprocess wrapper of 2.785 s on a wall-clock basis. The only consistent interpretation is that `prepare_build` for OptiX is measured in **GPU device time** (CUDA event timing), not wall time. GPU prepare_build runs asynchronously, overlapping with other CPU and GPU operations, and is therefore not counted linearly in wall-clock `total_run_window`.

For Embree, `prepare_build` is CPU-only and sequential. Its 0.395 s accumulation is consistent with wall-clock operation and is plausibly included in `total_run_window` (1.084 s = ~4.1 ms prepare + ~5.9 ms traversal + ~1.4 ms output_clear + ~2.1 ms postprocess per run, plus measurement overhead).

The wall-clock wrapper correctly captures this asymmetry — the wrapper includes the wall-clock cost of all GPU prepare work (since the process cannot exit before async GPU work synchronizes). The wrapper comparison (1.17x OptiX win) is therefore the most trustworthy end-to-end comparison excluding only the CPU oracle.

The ~5x tail and window speedups measure the `total_run_seconds` execution window, which is a narrower slice of the invocation that excludes device-side `prepare_build` work for OptiX. This is not inherently wrong for a "prepared invocation" claim, but a reader must understand that "prepared invocation" here means "the query execution window after the prepared structure has been engaged, measured in wall time, which may exclude asynchronous GPU preparation work measured separately in device time."

**Required disclosure addition (P1):** The public wording must clarify that the tail and window metrics measure the query execution phase within the prepared invocation, and that the wrapper metric provides the conservative process-level bound. The wrapper result should be explicitly positioned as the bound that captures all costs excluding the CPU oracle.

---

## 4. Generic V3 Engine Capability vs. App-Specific Work

**Genuine V3 generic engine capability row.** The evidence confirms:

- The measured primitive is `PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1`, a named engine contract.
- The runner (`scripts/v3_phoenix_robot_collision_flag_stream_no_probe_paired.py`) drives a research benchmark app, but the capability under test (`collision_flag_stream`) is the reusable engine route, not a native-engine or app-specific implementation.
- Both `embree_prepared_buffers` and `optix_prepared_device_buffers` invoke the same contract with the same shape and produce identical output (same hash). This is backend-comparative evidence for an engine API.
- The packet correctly does not claim this is full robot planning or that it exercises any app-level planning layer.

This row is appropriately scoped as V3 generic engine capability evidence.

---

## 5. P0/P1 Findings

### P0 findings: None

No P0 blockers affect the candidate wording. The numeric claims are arithmetically correct. The probe-reference separation is genuine. No forbidden categories (V3-over-V2, exact collision, continuous collision, zero-copy, full robot planning, whole-app end-to-end) appear in the candidate wording.

### P1 findings

**P1-A — Triangle count documentation error (packet docs, not public wording):**

The shape table in the `.md` states `static obstacle triangles: 2,048`. The top-level `.json` `shape` object states `"static_obstacle_triangle_count": 2048`. Every payload record — all 10 timed rows and both validation rows — reports `"static_obstacle_triangle_count": 4096`. The command uses `--obstacle-count 2048`, which produces 4,096 triangles (consistent with 2 triangles per obstacle, a standard convex-hull tessellation).

The candidate public wording does not cite triangle count and is therefore **not affected**. However, the packet shape table and machine-readable `.json` shape field must be corrected to `4096` (or `"2,048 obstacles, 4,096 triangles"`) before M7 promotion. A reviewer auditing the packet against the raw data would find this discrepancy immediately.

**P1-B — "Prepared invocation" scope disclosure (public wording, required addition):**

As described in section 3, the 5x tail and window speedups measure the `total_run_seconds` execution window, which for OptiX excludes GPU device-time `prepare_build` work that is counted asynchronously. The wrapper (1.17x) captures all wall-clock costs. The public wording must make explicit that the 5x metrics are for the prepared query execution phase, and that the wrapper result is the conservative process-level bound. Without this, a reader could interpret "tail prepared invocation speedup 5.086x" as the full per-call speedup including setup.

---

## 6. Exact Final Allowed Wording (if P1 items resolved)

The candidate wording requires one amendment (addition of the final sentence on metric scope). The triangle count error requires a packet correction but does not change the public wording.

```text
RTDL V3 includes a generic collision_flag_stream route where, on the 8,192-pose
/ 147,456-segment discrete sampled probe contract on a single RTX 4000 Ada pod,
prepared OptiX grouped segment any-hit flags beat the same-contract Embree route
across five no-probe paired process samples: tail prepared invocation speedup mean
5.086x, total-run window speedup mean 5.075x, and no-probe wrapper speedup mean
1.171x with weakest no-probe wrapper speedup 1.083x. CPU probe-reference
validation was run separately and matched both backends. This is sampled
flag-stream evidence, not full robot planning, exact solid collision, or
continuous collision. The tail and window speedups measure the prepared query
execution phase; the wrapper speedup is the conservative process-level bound that
includes all costs except the CPU probe-reference oracle.
```

Conditions on this wording:
- P1-A resolved: correct `static_obstacle_triangle_count` from 2048 to 4096 in the `.md` shape table and top-level `.json` shape field.
- P1-B resolved: the final sentence above (added relative to the candidate) or equivalent disclosure is included.
- Row scope: this wording must not be used to imply anything broader than this contract, this shape, and this single pod.
- No further speedup figures from this packet (traversal, validation-phase hot tail) may appear in public wording without separate review of those metrics.

---

## 7. Exact Forbidden Wording

The following are explicitly forbidden regardless of this approval:

```text
Robot collision V3 is 5x faster end to end.
RTDL accelerates full robot planning.
RTDL supports exact solid collision for this row.
RTDL supports continuous collision for this row.
V3 is broadly faster than V2 for robot collision.
This row proves zero-copy.
collision_flag_stream is M7-qualified before external review.
OptiX is 5x faster than Embree for robot collision queries.
OptiX prepared invocation is 5x faster end to end.
```

Additionally forbidden given the phase-timing finding:

```text
The prepared invocation speedup of 5x is the per-call wall-clock cost including backend setup.
OptiX handles the full prepare-and-query cycle 5x faster than Embree.
```

---

## Summary Table

| Review item | Finding |
|---|---|
| Verdict | Approve with amendments (P1-A, P1-B) |
| Probe-reference separation acceptable | Yes — clearly separated, signatures match |
| Timing definitions clear enough | Yes for wrapper; P1-B disclosure required for tail/window |
| Generic V3 engine capability (not app-specific) | Confirmed |
| P0 blockers | None |
| P1 blockers | Two: triangle count doc error (P1-A), prepared-invocation scope disclosure (P1-B) |
| Candidate wording approved as-is | No — add final sentence per section 6 |
| Candidate wording approved with amendment | Yes, per exact text in section 6 |
