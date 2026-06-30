# Goal 1545: OptiX COLLECT_K_BOUNDED Device-Side Segmented Compact Pod Prep

## Verdict

Prepared and compile-validated, but not performance-accepted. This report defines the next credible pod experiment after Goal 1543 and Goal 1544:

Move the compact offset work from the host to the device while preserving sorted-unique output order.

The implementation is staged behind `RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT=1`. The goal is to make the next pod round efficient by clarifying which designs are safe, which are risky, and what evidence should be collected.

## Current Position

The current best accepted path is Goal 1543:

`RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT=1 RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1 RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL=1 RTDL_OPTIX_COLLECT_K_REUSE_WORKSPACE=1`

Clean RTX 2000 Ada evidence at commit `ddf7d20e737799e6eab527d61afc412ce5fbab1f` measured:

| candidates | total ms | allocation ms | merge launch ms | merge sync ms |
|---:|---:|---:|---:|---:|
| 4097 | 0.138536 | 0.000230 | 0.059423 | 0.007300 |
| 65537 | 0.447407 | 0.000290 | 0.287411 | 0.045182 |
| 131072 | 0.545801 | 0.000190 | 0.346833 | 0.071134 |

Goal 1544 rejected simple launch-count shortcuts:

- Raising `RTDL_OPTIX_COLLECT_K_PARALLEL_COMPACT_MIN_CAPACITY` makes wide levels use the single-thread serial merge and regresses badly.
- Replacing only the final two-segment compact with serial merge also regresses badly.
- Removing a pre-download synchronize was inconclusive and did not improve the largest case.

## Correctness Contract

For every merge pair:

- Input rows are sorted unique row-width-2 tuples.
- Output rows must be sorted unique row-width-2 tuples.
- `emitted_count` is the exact number of unique merged rows, even when the output capacity is smaller.
- Writes must stay within `output_capacity`.
- Pair boundaries must not bleed into neighboring pairs in the same merge level.
- The Python-visible parity checks must keep passing: same rows, same valid count, same overflow flag.

## Why Atomic Compact Is Risky

A tempting two-launch path is:

1. materialize sorted merged rows,
2. mark unique rows and use `atomicAdd(pair_count)` to place kept rows.

This is not acceptable as-is because block scheduling is not deterministic. Later blocks can win the atomic before earlier blocks, so the output can contain the right set of rows but in a non-sorted order. RTDL currently checks exact row order, not only set equality. Sorted order is part of the practical contract for deterministic downstream use.

Atomic compact should only be tested behind a clearly named negative/experimental flag if we intentionally want to prove the failure mode. It should not be the main candidate for accepted evidence.

## Candidate A: Device-Side Block Prefix

This is the safest next implementation candidate and is now staged behind an explicit env flag.

Current Goal 1543 batched compact level:

1. launch level materialize,
2. launch level mark-count,
3. synchronize,
4. download block counts,
5. compute block offsets and pair offsets on host,
6. upload offsets,
7. launch level compact.

Candidate A:

1. launch level materialize,
2. launch level mark-count,
3. launch a small device prefix kernel that computes block offsets, pair offsets, and pair counts,
4. launch level compact.

Expected tradeoff:

- Adds one small kernel launch per compact level.
- Removes host block-count download, host prefix loop, and offset upload from each compact level.
- Preserves deterministic sorted order because compact still uses stable block offsets.
- May or may not be faster, because Goal 1543 metadata time is already small. It still deserves one pod test because it removes a CPU/GPU round trip and may improve variance.

Suggested env flag:

`RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT=1`

Local validation completed before pod timing:

- Windows static/topology tests passed with `py -3 -m unittest`.
- Linux compile validation passed on `192.168.1.20` in `/home/lestat/work/rtdl_codex_local_check`.
- Linux build command: `make build-optix OPTIX_PREFIX=/home/lestat/vendor/optix-dev`.
- The Linux host is a GTX 1070 smoke/compile host only and is not accepted for the row-width-2 tiled performance claim.

Expected topology for CUB + batched compact + reusable workspace + device prefix:

| candidates | tile count | sort launches | merge launches | carry copies |
|---:|---:|---:|---:|---:|
| 4097 | 3 | 1 | 7 | 1 |
| 65537 | 33 | 1 | 23 | 5 |
| 131072 | 64 | 1 | 23 | 0 |

The launch count increases because each batched compact level becomes four launches instead of three. Therefore this candidate should only be accepted if total time improves or variance improves enough to justify the extra launch.

## Candidate B: CUDA Graph Replay

CUDA graph replay may reduce launch overhead without changing compact semantics.

Risk:

- Current compact levels contain host-side downloads and uploads whose values depend on per-call row counts.
- A graph that still requires host intervention between nodes may not provide enough benefit.
- A graph that moves prefixing to device starts looking like Candidate A plus graph capture.

Suggested sequence:

1. Test Candidate A first.
2. If Candidate A preserves parity but loses only by launch overhead, test CUDA graph capture around the materialize, mark-count, device-prefix, compact sequence.

Suggested env flag:

`RTDL_OPTIX_COLLECT_K_COMPACT_GRAPH_REPLAY=1`

## Candidate C: Prepared Execution Model

A prepared execution model would amortize Python and host setup across repeated calls. It is architecturally attractive for Python+RTDL, but it is broader than a kernel micro-optimization.

Use this direction if Candidate A and graph replay fail. It should be designed as an API/architecture goal, not hidden inside the current one-shot wrapper.

## Pod Work Queue

When a pod is available, run these in order:

1. Clean sync to `origin/main` and build OptiX.
2. Re-run Goal 1543 as control with repeats `7` or `9`.
3. Implement or copy Candidate A under `RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT=1`.
4. Run the same counts: `4097 65537 131072`.
5. Compare total, merge launch, merge sync, metadata, and topology.
6. Accept only if parity is perfect and the largest count improves versus the fresh Goal 1543 control.

The helper runner below executes the Goal 1543 control and the device-prefix candidate back-to-back and writes a comparison summary:

```bash
PYTHONPATH=src:. python3 scripts/goal1545_v1_5_4_optix_collect_k_device_prefix_pod_runner.py \
  --library build/librtdl_optix.so \
  --counts 4097 65537 131072 \
  --repeats 7
```

Control command shape:

```bash
RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT=1 \
RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1 \
RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL=1 \
RTDL_OPTIX_COLLECT_K_REUSE_WORKSPACE=1 \
PYTHONPATH=src:. python3 scripts/goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py \
  --library build/librtdl_optix.so \
  --counts 4097 65537 131072 \
  --repeats 7 \
  --json-out docs/reports/goal1545_control_goal1543_probe_2026-05-08.json \
  --md-out docs/reports/goal1545_control_goal1543_probe_2026-05-08.md \
  --profile-jsonl docs/reports/goal1545_control_goal1543_profile_2026-05-08.jsonl
```

Candidate command shape:

```bash
RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT=1 \
RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1 \
RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL=1 \
RTDL_OPTIX_COLLECT_K_REUSE_WORKSPACE=1 \
RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT=1 \
PYTHONPATH=src:. python3 scripts/goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py \
  --library build/librtdl_optix.so \
  --counts 4097 65537 131072 \
  --repeats 7 \
  --json-out docs/reports/goal1545_device_prefix_compact_probe_2026-05-08.json \
  --md-out docs/reports/goal1545_device_prefix_compact_probe_2026-05-08.md \
  --profile-jsonl docs/reports/goal1545_device_prefix_compact_profile_2026-05-08.jsonl
```

## Claim Boundary

This is a local pod-prep design artifact only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, stable primitive promotion, or release action.
