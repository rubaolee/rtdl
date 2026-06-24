# RTDL V4.0 Section 8 Validation Protocol

Date: 2026-06-24
Status: focused validation protocol; not a release claim

## Purpose

Validate or falsify the V4 Tier-2 thesis with one existing fused primitive:

`fixed_radius_count_threshold`

The experiment asks one narrow question:

> Does a fused native fixed-radius threshold-count primitive materially beat the
> separated RTDL row-materialization route on the same contract and hardware?

If it does not, V4.0 must not proceed as a performance release.

## Workload

Use the current outlier-density fixture because it already exposes the same
operator through multiple routes:

- default route: fixed-radius neighbor rows, then Python reduction
- fused route: fixed-radius count-threshold summary, prepared native traversal
- optional device-column route: fused traversal writes partner-owned columns

This is a generic operator test, not an outlier-specific engine kernel.

## Required Routes

Run each route with the same `copies`, radius, threshold, and hardware.

### A. Tier-1 separated route

```bash
PYTHONPATH=src:. python examples/current/apps/ml/rtdl_outlier_detection_app.py \
  --backend optix \
  --copies <copies> \
  --output-mode full \
  --optix-summary-mode rows
```

This route emits neighbor rows and reduces outside traversal. It is the
separated baseline.

### B. Tier-2 fused prepared scalar route

```bash
PYTHONPATH=src:. python examples/current/apps/ml/rtdl_outlier_detection_app.py \
  --backend optix \
  --copies <copies> \
  --output-mode density_count
```

This route uses prepared native fixed-radius count-threshold traversal and
returns only scalar count output.

### C. Tier-2 fused prepared summary route

```bash
PYTHONPATH=src:. python examples/current/apps/ml/rtdl_outlier_detection_app.py \
  --backend optix \
  --copies <copies> \
  --output-mode density_summary \
  --optix-summary-mode rt_count_threshold_prepared
```

This route uses prepared native fixed-radius count-threshold traversal and
returns compact density rows.

### D. Independent hand-written OptiX reference

If an independent hand-written OptiX reference route exists for this exact
contract, run it as the reference ceiling.

If it does not exist, record:

```text
independent_handwritten_optix_reference_available: false
near_handwritten_optix_claim_authorized: false
```

In that case this protocol can validate "fusion beats separated RTDL", but it
cannot authorize "near hand-written OptiX" wording.

## Serious Sizes

Smoke size:

- `copies=1` for correctness and route availability only

Serious sizes:

- `copies=8192`   -> 65,536 points
- `copies=32768`  -> 262,144 points
- `copies=131072` -> 1,048,576 points

The serious result must not be read from `copies=1`.

## Repeats

For each serious size:

- warmup: 1 run per route
- measured repeats: 7 runs per route
- report median, min, max, and all raw timings

## Correctness Gate

Every measured route must report:

- `matches_oracle: true`
- same `point_count`
- same `outlier_count`
- same `threshold_reached_count` when present

Any correctness mismatch kills the experiment.

## Performance Gate

The V4 Tier-2 thesis is considered locally validated only if:

- fused prepared scalar route beats the Tier-1 separated route by at least
  `2.0x` median wall time on at least two serious sizes; and
- fused prepared summary route beats the Tier-1 separated route by at least
  `1.5x` median wall time on at least two serious sizes; and
- the winning route uses the native fixed-radius count-threshold continuation,
  not an app-identity kernel.

If those gates fail, V4.0 must not continue as a performance release.

## Claim Boundary

Passing this protocol authorizes only:

```text
On the measured fixed-radius threshold-count rows, the fused native primitive
beats the separated row-materialization route on the measured hardware.
```

It does not authorize:

- broad V4 speedup wording
- broad V3-over-V2 wording
- near hand-written OptiX wording without route D
- any Tier-3 PTX/user-callback claim
- any app-specific native engine claim

## Harness

Use:

```bash
PYTHONPATH=src:. python scripts/v4_section8_fixed_radius_count_threshold_validation.py --dry-run
```

For the serious run on GPU hardware:

```bash
PYTHONPATH=src:. python scripts/v4_section8_fixed_radius_count_threshold_validation.py \
  --copies 8192 --copies 32768 --copies 131072 \
  --repeat 7 --warmup 1 \
  --progress \
  --json-out docs_or_tmp_v4_section8_fixed_radius_result.json
```

The result file must be externally reviewed before any V4 build decision.

The harness result must include:

- `correctness.correctness_passed` per serious size
- raw per-route timings and medians
- `comparisons.*.speedup_over_optix_rows_median`
- `performance_gate.status`
- `performance_gate.v4_tier2_thesis_locally_validated`
- `performance_gate.authorized_next_step`

If `performance_gate.status != "pass"`, stop the V4 performance-release path and
revisit the architecture before adding more fused primitives.
