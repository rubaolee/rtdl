# Goal4266 Large-Scale CuPy vs Numba Partner Comparison

Date: 2026-06-09

Status: RTX 3090 large-scale partner evidence collected for the two partner-needed contract families.

## Purpose

The previous user-facing CuPy-vs-Numba comparison table included several rows whose measured hot time was below one second, and two rows had no same-contract CuPy opponent. That is easy to misread. A user deciding between partners needs evidence that is:

- same-contract,
- correctness-checked,
- large enough to be meaningful,
- explicit about whether the row is partner-only, primitive-first, or whole-app,
- explicit about what the result does **not** authorize.

Goal4266 adds a dedicated large-scale comparison runner:

`scripts/goal4266_large_scale_partner_comparison.py`

The runner first calibrates a repeat count for each contract, then runs CuPy and Numba with that **same repeat count**. The calibrated count is chosen so the faster partner should still exceed the requested aggregate hot-time floor, defaulting to `1.25s`, unless `--max-repeat` is exhausted. It reports both comparable hot aggregate time and median per invocation.

## Contracts Tested

| Contract | User-facing meaning | Partners | Default scale | Why this belongs in the table |
| --- | --- | --- | ---: | --- |
| `segmented_count_i64` | grouped count continuation | CuPy, Numba | 4,000,000 rows / 4,096 groups | RayDB-style unfused grouped continuation |
| `segmented_sum_f64` | grouped sum continuation | CuPy, Numba | 4,000,000 rows / 4,096 groups | RayDB-style unfused grouped continuation |
| `segmented_min_f64` | grouped min continuation | CuPy, Numba | 4,000,000 rows / 4,096 groups | RayDB-style unfused grouped continuation |
| `segmented_max_f64` | grouped max continuation | CuPy, Numba | 4,000,000 rows / 4,096 groups | RayDB-style unfused grouped continuation |
| `avg_as_sum_count` | average represented as sum plus count | CuPy, Numba | derived | avoids pretending average needs a separate custom kernel |
| `compact_mask_i64` | stable row-stream/candidate-row compaction | CuPy, Numba | 8,000,000 rows | triangle/RayJoin-style candidate continuation |

## User-Reading Rule

Every published row must answer:

1. What should a user conclude?
2. What should a user **not** conclude?
3. Is the timing above the one-second aggregate floor?
4. Did both partners match the same CPU oracle?
5. Is this partner-only continuation evidence, not whole-app or RT-core evidence?

The runner therefore emits `claim_boundary` flags and a `subsecond_hot_total_rows` list. If a row stays below `1s`, it is visible and should not be used as decision-grade evidence. Speedups must be read from rows where both partners used the same repeat count.

## Runtime Fix

While preparing the large-scale runner, the v2.8 typed-stream front door had a metadata anti-pattern:

`len(_adapter_like(...))`

For large device arrays that could build a Python tuple just to discover row count. Goal4266 replaces those metadata lengths with `_partner_column_length(...)`, preserving semantics while avoiding accidental million-row host-side expansion.

Touched file:

`src/rtdsl/v2_8_segmented_typed_stream_adapter.py`

## Current Validation

Local validations passed on Windows:

```text
py -3 -m py_compile scripts/goal4266_large_scale_partner_comparison.py src/rtdsl/v2_8_segmented_typed_stream_adapter.py
py -3 scripts/goal4266_large_scale_partner_comparison.py --dry-run --output scratch/goal4266_dry_run.json
py -3 -m unittest tests.goal4266_large_scale_partner_comparison_test tests.goal3147_compact_mask_front_door_test tests.goal3162_raydb_grouped_reduction_typed_stream_front_door_test
```

Result:

```text
Ran 10 tests in 1.151s
OK (skipped=1)
```

The skipped test is an existing CUDA-gated path on this Windows host.

## RTX 3090 Evidence

Artifact:

`docs/reports/goal4266_large_scale_partner_comparison/summary.json`

Hardware and source:

| Field | Value |
| --- | --- |
| GPU | NVIDIA GeForce RTX 3090 |
| Driver | 580.159.03 |
| Source commit | `9c628b46eefa...` |
| CuPy | 14.1.1 |
| Numba | 0.65.1 |
| NumPy | 2.4.6 |

All rows below use the same repeat count for CuPy and Numba within that contract. All rows match the CPU oracle. No row has less than one second of aggregate hot time.

| Contract | Scale | Equal repeats | CuPy total sec | Numba total sec | CuPy speedup vs Numba | CuPy median ms | Numba median ms | User reading |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `segmented_count_i64` | 4,000,000 rows / 4,096 groups | 2,043 | 1.534 | 2.361 | 1.54x | 0.7000 | 1.0829 | CuPy is faster |
| `segmented_sum_f64` | 4,000,000 rows / 4,096 groups | 3,671 | 1.149 | 4.626 | 4.03x | 0.2949 | 1.1914 | CuPy is faster |
| `segmented_min_f64` | 4,000,000 rows / 4,096 groups | 759 | 1.513 | 2.497 | 1.65x | 1.8852 | 3.0781 | CuPy is faster |
| `segmented_max_f64` | 4,000,000 rows / 4,096 groups | 623 | 1.276 | 2.077 | 1.63x | 1.9014 | 3.1098 | CuPy is faster |
| `compact_mask_i64` | 8,000,000 rows | 3,034 | 1.463 | 34.324 | 23.45x | 0.4595 | 10.9947 | CuPy is much faster |

Suite summaries:

| Suite | CuPy total sec | Numba total sec | CuPy speedup vs Numba | User reading |
| --- | ---: | ---: | ---: | --- |
| RayDB-style unfused grouped reductions | 5.472 | 11.562 | 2.11x | Choose CuPy for performance on these grouped contracts |
| Triangle/RayJoin-style compact mask | 1.463 | 34.324 | 23.45x | Choose CuPy unless no-RawKernel/no-CuPy policy is more important |

## User-Facing Conclusion

For the two benchmark contract families where users really need a partner:

- If the user wants maximum performance on this RTX 3090-class NVIDIA GPU, choose CuPy for grouped reductions and compact-mask continuation.
- If the user strongly wants "no hand-written RawKernel" reference code, Numba remains useful and correct, but it is not the fastest path in this packet.
- If the app can be answered by a fused RTDL primitive, do not force either partner. Primitive-first still wins the design rule.
- These rows are partner-continuation timings only. They are not whole-app speedups, RT-core speedups, release authorization, or universal CuPy-vs-Numba results.

## Hardware Status

Accepted same-contract timing evidence has now been produced on the RTX 3090 pod above.

Checked endpoints:

| Target | Result |
| --- | --- |
| `192.168.1.20` | SSH timed out |
| `root@69.30.85.203 -p 22057` | connection refused |
| `root@157.157.221.29 -p 24101` | key rejected |
| Windows local | no CuPy and no Numba installed |
| `root@213.192.2.91 -p 40030` | RTX 3090 run completed with the repo-local RTDL pod key |

## Pod Command

Once a reachable CUDA pod is available, run:

```bash
cd /root/rtdl_v0_4_release_prep_review
git fetch origin main
git reset --hard origin/main
export PYTHONPATH=src:.
python3 scripts/goal4266_large_scale_partner_comparison.py \
  --grouped-rows 4000000 \
  --groups 4096 \
  --compact-rows 8000000 \
  --target-hot-total-sec 1.25 \
  --warmup 2 \
  --calibration-repeat 10 \
  --calibration-safety-factor 1.15 \
  --max-repeat 5000 \
  --progress-every 10 \
  --output docs/reports/goal4266_large_scale_partner_comparison/summary.json
```

If the pod is fast enough that any contract still fails the one-second floor after 5000 repeats, increase `--max-repeat` or increase row counts and rerun. Do not publish a winner table with any non-empty `subsecond_hot_total_rows`, or with rows where `same_repeat_count_for_both_partners` is not true.

## Claim Boundary

This goal does not authorize:

- release,
- public speedup claims,
- whole-app speedup claims,
- RT-core speedup claims,
- true zero-copy claims,
- universal CuPy-vs-Numba winner claims.

It only creates a clean same-contract measurement path for the two partner families users actually ask about.
