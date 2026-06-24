# Phoenix V3 M47 LibRTS Stability / Cold-Start Protocol

Date: 2026-06-23

Status: `protocol_draft_pending_external_review_no_run`

This protocol prepares a focused LibRTS Set-B/control watch-row run. It does not
authorize executing the run, paid POD spend, all-app benchmarking, V3 release,
public speedup wording, broad V3-over-V2 claims, V4 work, embedding, C ABI, or
true-zero-copy claims.

## Local Harness Status

The protocol now has a local dry-run/intake harness:

```text
scripts/v3_phoenix_m47_librts_stability_protocol.py
```

Safety behavior:

- default mode is dry-run;
- real execution requires `--execute`;
- real execution also requires the explicit authorization token
  `M47_FOCUSED_LIBRTS_STABILITY_AUTHORIZED`;
- dry-run emits the full command schedule but does not run LibRTS benchmarks;
- all release/all-app/POD/public/V4/embedding/C-ABI/true-zero-copy authorization
  fields remain false.

Focused local validation:

```text
PYTHONPATH=src;. py -3 -m py_compile scripts/v3_phoenix_m47_librts_stability_protocol.py
PYTHONPATH=src;. py -3 -m unittest tests.v3_phoenix_m47_librts_stability_protocol_test
Ran 5 tests OK
```

Dry-run evidence:

```text
docs/rebuild/v3/evidence/phoenix_v3_m47_librts_stability_protocol_dry_run_20260623/
```

Dry-run summary:

```text
status: m47_librts_stability_protocol_dry_run_no_pod_not_release
execute: false
scenario_count: 2
sample_count_per_scenario: 8
schedule_row_count: 32
failed_check_count: 0
paid_pod_authorized_by_this_packet: false
```

M48 hardening note:

- `docs/reports/phoenix_v3_m48_librts_stability_harness_execution_safety_2026-06-23.md`
  hardens this harness with execution preflight, tree-specific working
  directories, fixture/contract mismatch checks, and current metadata failure
  red-classification.
- That hardening still runs no benchmark and authorizes no POD, all-app, or
  release action.

## Purpose

M46 leaves two LibRTS watch surfaces open:

- OptiX strict cold single-shot: `improved_not_closed`
- Embree 32768 stress: `stability_watch_blocker`

M47 defines the smallest focused protocol that can separate first-sample /
cold-start variance from steady behavior without hiding outliers or converting
Set-B/control rows into Set-A runtime-trunk proof.

## Inputs

- Current report:
  `docs/reports/phoenix_v3_m46_librts_set_b_watch_rows_status_and_next_protocol_2026-06-23.md`
- M27 accepted fix and consensus:
  `docs/reviews/codex_claude_phoenix_v3_m27_librts_aabb_set_b_triage_and_cold_optix_retain_fix_2ai_consensus_2026-06-23.md`
- Benchmark front door:
  `examples/current/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py`

## Scenarios

### Scenario A: OptiX Strict Cold Single-Shot

Command shape:

```bash
python examples/current/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py \
  --mode optix_aabb_index \
  --dataset uniform \
  --operation all \
  --box-count 2048 \
  --query-count 1024 \
  --seed 2025 \
  --repeat 1 \
  --warmup 0
```

This keeps CPU reference validation enabled. It targets the M25/M27 strict
cold single-shot watch row.

### Scenario B: Embree 32768 Stress

Command shape:

```bash
python examples/current/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py \
  --mode embree_aabb_index \
  --dataset uniform \
  --operation all \
  --box-count 32768 \
  --query-count 1024 \
  --seed 2025 \
  --repeat 20 \
  --warmup 5 \
  --skip-counts
```

This targets the M25/M27 Embree stress instability surface. CPU counts are
skipped to avoid turning the timing run into an oracle run; contract is carried
by the fixed fixture, mode, operation, and prior correctness coverage.

## Execution Order

No run is authorized by this protocol draft. If a later review authorizes one
focused POD run, execute:

1. environment capture:
   - `nvidia-smi`
   - Python version
   - `git rev-parse HEAD` or explicit non-git-tree provenance
   - package/import checks for current and v2.14 trees
2. local/POD tests before timing:
   - `tests.v3_phoenix_librts_aabb_count_runner_test`
   - `tests.v3_phoenix_prepared_execution_session_runner_test`
   - `tests.v3_phoenix_aabb_prepared_query_cache_test`
3. measured samples:
   - 8 samples for Scenario A, current and v2.14
   - 8 samples for Scenario B, current and v2.14
   - each sample is a fresh process
   - order alternates to reduce drift:

```text
sample 1: v2.14 then current
sample 2: current then v2.14
sample 3: v2.14 then current
sample 4: current then v2.14
...
sample 8: current then v2.14
```

The first measured sample must remain visible. It may be separately classified
as first-sample/cold-start, but it must not be deleted.

## Required Output Fields

For each scenario:

- current seconds per sample
- v2.14 seconds per sample
- paired speedup per sample, computed as `v2_sec / current_sec`
- geomean over all 8 samples
- median over all 8 samples
- min and max
- pass count for `>=0.950x`
- first-sample-stripped geomean
- first-sample-stripped median
- stderr presence/absence per run
- runner metadata presence for current OptiX:
  - `prepared_execution_session_runner_used`
  - `productized_execution_path`
  - `primitive_contract`
  - `prepared_query_mode`
- claim-boundary booleans all false for release/public/all-app/V4/etc.

## Status Labels

### Green Closure Candidate

Allowed only if all are true:

- all-sample geomean `>=0.950x`
- all-sample median `>=0.950x`
- pass count at least `7 / 8`
- no sample below `0.900x`
- first-sample-stripped geomean `>=0.980x`
- stderr empty
- fixture and contract fields match
- current runner metadata present where applicable

Even green is only a closure candidate. It still needs external review before
the watch row is called closed.

### Yellow Stability Boundary

Use if:

- all-sample geomean is `>=0.950x`, but any closure-candidate condition above
  fails.

This means the row remains open with a documented stability/cold-start boundary.

### Red Failure

Use if:

- all-sample geomean `<0.950x`; or
- all-sample median `<0.950x`; or
- stderr / fixture / contract / runner metadata failures appear.

This means the row remains an active Set-B blocker.

## Stop Conditions

Stop and record failure instead of interpreting performance if:

- current or v2.14 command exits nonzero;
- stderr contains runtime/toolchain errors;
- fixture counts, seed, operation, mode, box count, query count, repeat, or
  warmup differ between paired runs;
- current OptiX payload lacks productized runner metadata;
- result files are missing;
- output claim-boundary fields authorize release/public/all-app/V4/etc.;
- a run accidentally becomes all-app or includes unrelated benchmark apps.

## Resource Estimate

Expected focused POD time if later authorized:

```text
0.5 - 1.5 hours
estimated cost at $1 / 4 hours: $0.13 - $0.38
```

This is not an authorization. It is a budget estimate for review.

## Non-Authorization

This protocol does not authorize:

- V3 release
- all-app benchmark run
- paid POD spend
- public speedup wording
- broad V3-over-V2 claim
- V4 work
- embedding
- C ABI
- true zero-copy claim

## Goal-Level Decision Audit

Decision: prepare a focused LibRTS stability/cold-start protocol draft without
running it.

1. Was I foolish? No.
2. If yes, what actions made the decision foolish? The foolish action would be
   to run another focused POD without an order-controlled protocol, or to hide
   first-sample outliers.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Change code first or run all-app. Both are rejected because M31 showed
   the immediate gap is stability interpretation, not a proven algorithmic
   rewrite need.
4. Can I now try a different path that actually solves the problem? Yes. Submit
   this protocol for external review; if accepted, request one small focused POD
   run later.
