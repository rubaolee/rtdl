# Goal1035 Claude Review

Date: 2026-04-26  
Reviewer: Claude Sonnet 4.6  
Verdict: **ACCEPT**

---

## Criteria

### 1. Incremental runner is safer than the failed monolithic run

PASS.

The prior Goal1031 runner emitted no output until the full batch completed. At manifest scale (`--copies 20000`) it stalled on `outlier_detection` Embree after an expensive CPU command and had to be killed, losing all timing evidence.

Goal1035 corrects this structurally:

- Each command is run in isolation via `subprocess.run` with a hard `timeout_sec` (default 180 s).
- `TimeoutExpired` is caught and recorded as `status: timeout` with partial stdout/stderr — evidence survives.
- `write_outputs()` is called inside the per-command loop (script lines 192–198), so a checkpoint JSON and Markdown exist after every row.
- The `_status()` classifier surfaces any timeout or non-ok row as `needs_attention`, preventing a partial run from reporting green.

These properties together mean that a repeat of the original failure would produce: (a) a result file with all rows up to the stall, (b) a `timeout` row for the offending command, and (c) a `needs_attention` top-level status. No silent data loss.

### 2. Summary accurately reports completed rows and boundaries

PASS.

The summary table claims 24 rows at 50/500 copies and 12 rows at 2000 copies, both `ok`. This matches the result files exactly:

- `goal1035_local_baseline_scale_ramp_2026-04-26.md`: `rows: 24`, `status: ok` (4 apps × 3 backends × 2 scales).
- `goal1035_local_baseline_scale_ramp_2000_2026-04-26.md`: `rows: 12`, `status: ok` (4 apps × 3 backends × 1 scale).

All 36 individual rows carry `status: ok`. No rows are missing from either file. Boundary language is stated correctly and consistently across the summary, both result files, and the `build_payload` hardcoded field.

### 3. No public speedup or RTX claim is authorized

PASS.

The boundary text ("does not authorize speedup claims, and same-scale public comparisons still require review") is:

- Hardcoded in `build_payload()` and written into every JSON output.
- Embedded twice in every generated Markdown (header paragraph and `## Boundary` footer).
- Asserted by the test suite (`test_write_outputs_updates_json_and_markdown`, line 61).

The summary goes further, explicitly excluding release authorization and NVIDIA RT-core superiority claims, and stating that cloud RTX timing with repeated runs and same-semantics review gates are still required. No Embree/CPU ratio or speedup multiplier appears anywhere in the artifacts.

### 4. Outlier detection performance concern is fairly stated

PASS.

The raw data at 2000 copies:

| Backend | Elapsed (s) |
|---|---:|
| cpu | 15.258 |
| embree | 15.268 |
| scipy | 16.228 |

CPU and Embree are within 10 ms — no RT-phase signal is visible at app level. The summary correctly attributes this to "shared overhead or semantics outside the prepared RT phase" and states that `outlier_detection` "needs phase-level instrumentation or implementation review before it is useful as a public comparison target." This language is accurate, honest, and does not suppress the anomaly or offer unsupported explanations. A concrete engineering action (phase-level instrumentation) is recommended rather than a workaround.

For comparison, the three other apps show consistent Embree < CPU at 2000 copies with sub-500 ms elapsed, confirming the problem is specific to `outlier_detection`.

---

## Minor Observations (non-blocking)

- `event_hotspot_screening` does not emit `hotspot_event_count` in its JSON summary (the field is listed in `to_markdown`'s compact key list but absent from actual output). All rows pass `status: ok`, so this is a summary-completeness gap, not a correctness issue. Worth tracking separately.
- The boundary text is written twice per Markdown file (once in the preamble, once in `## Boundary`). Redundant but consistent and not incorrect.

---

## Verdict

**ACCEPT.** All four criteria are met. Goal1035 is a materially safer execution method than the failed monolithic runner, its reported results are verifiable against the artifact files, no public speedup or RTX claim is made or implied, and the `outlier_detection` anomaly is disclosed accurately with a clear engineering path forward.
