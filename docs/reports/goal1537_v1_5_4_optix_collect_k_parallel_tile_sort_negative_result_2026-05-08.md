# Goal 1537: OptiX COLLECT_K_BOUNDED Parallel Tile-Sort Negative Result

## Verdict

Rejected as an implementation path in the tested form. The prototype was intended to reduce the remaining long-count sort bottleneck by replacing one sort launch per tile with a single multi-block tile-sort launch, but it failed on the NVIDIA pod before producing accepted parity or performance evidence.

This report records the negative result so the next implementation does not repeat the same unstable launch shape. Do not commit the unstable runtime path.

## Prototype

The experiment added an env-gated path behind:

`RTDL_OPTIX_COLLECT_K_PARALLEL_TILE_SORT=1`

The intended topology was:

- Keep the accepted late-level compact path behind `RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1`.
- Use `tile_size=2048` for larger counts so the metadata arrays could cover up to `64` tiles for `131072` candidates.
- Launch one `collect_k_bounded_i64_row_width2_sort_tiles` grid with one CUDA block per tile.
- Preserve the existing per-tile sort path when the env flag was absent.

## Pod Scope

- Pod: `root@213.173.110.196 -p 24309`
- Device: `NVIDIA RTX 2000 Ada Generation`
- Driver: `570.172.08`
- OptiX SDK: `/root/vendor/optix-sdk`, NVIDIA `optix-sdk` tag `v8.0.0`
- Base accepted commit before local experiment: `4e3bbf2e`
- Build command: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`
- Probe command shape: `RTDL_OPTIX_COLLECT_K_PARALLEL_TILE_SORT=1 RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1 PYTHONPATH=src:. python3 scripts/goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py --library build/librtdl_optix.so --counts 65537 --repeats 1 ...`

## What Worked

- Local source-structure tests passed for the prototype.
- The accepted late-level compact path stayed stable when the tile-sort flag was not used.
- The short `4097` case stayed outside the new batched tile-sort path after the large shared-memory attribute was no longer applied to the unused tile-sort function.

## Why It Failed

The pod rejected the actual larger-count tile-sort launch during the `65537` warmup with:

`RuntimeError: CUDA driver error: invalid resource handle`

Two launch-shape variants were tested and both failed at the same point:

- Runtime `tile_size` argument, `tile_size=2048`, dynamic shared memory `34816` bytes, `512` threads per block.
- Hardcoded `tile_size=2048`, explicit shared-memory attribute on the tile-sort function, dynamic shared memory `34816` bytes, `256` threads per block.

No accepted JSON/Markdown/profile artifacts were produced because the run did not reach parity validation or measured timing.

## Required Correction

The current best accepted result remains the late-level compact path. Its long-count bottleneck moved from merge to sort, so sort remains the dominant remaining stage: at `131072`, the accepted Goal 1536 evidence recorded total `32.583600 ms`, sort `23.395900 ms`, and merge `8.518870 ms`.

The next sort optimization should use a different design rather than this failed multi-block shared-memory bitonic kernel shape. Viable next directions are:

- A smaller, independently validated tiled kernel with a standalone launch smoke test before wiring it into `collect_k_bounded`.
- A CUB/Thrust-backed sort/unique prototype if dependency boundaries allow it.
- A merge-oriented design that reduces the number of required tile sorts rather than batching the current bitonic sort body.

## Claim Boundary

No source changes from this failed prototype were committed. This report is a negative-result artifact only. It does not authorize speedup claims, stable primitive promotion, release action, or any public-facing performance statement.
