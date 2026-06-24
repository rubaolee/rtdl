# Goal 1538: OptiX COLLECT_K_BOUNDED CUB Tile-Sort Feasibility

## Verdict

CUB block-level sorting is feasible as the next OptiX `COLLECT_K_BOUNDED` sort optimization direction. A standalone pod smoke test compiled a `cub::BlockMergeSort<Row2, 256, 8>` kernel to PTX, loaded it through the CUDA Driver API, launched it on the RTX pod, and verified correct lexicographic sorting for `2048` `(int64,int64)` rows.

This is not yet an RTDL runtime implementation and does not replace the accepted Goal 1536 late-level compact path.

## Scope

- Pod: `root@213.173.110.196 -p 24309`
- Device: `NVIDIA RTX 2000 Ada Generation`
- Driver: `570.172.08`
- CUDA headers: `/usr/local/cuda/include`
- CUB headers observed:
  - `/usr/local/cuda/include/cub/block/block_merge_sort.cuh`
  - `/usr/local/cuda/include/cub/block/block_radix_sort.cuh`
  - `/usr/local/cuda/include/cub/cub.cuh`
- Base repo commit revalidated before smoke: `45105e72a5813bbb59bb31f1950ed78a8b2bb331`

## Smoke Test

The standalone CUDA kernel used:

- `struct Row2 { long long a; long long b; };`
- A custom comparator implementing lexicographic `(a,b)` ordering.
- `cub::BlockMergeSort<Row2, 256, 8>`, so one block sorts `2048` row keys.
- CUDA Driver API load/launch from generated PTX.

The driver smoke generated `2048` random signed row pairs, sorted the same rows with `std::sort` on the host, launched the CUB kernel, copied results back, and compared every output row.

Observed output:

`cub_block_merge_sort_smoke_ok n=2048`

## Why This Matters

The accepted Goal 1536 path made merge much faster for long counts, but sort remains the dominant remaining stage. On the clean pushed state revalidation, `131072` candidates measured about:

- total: `32.577200 ms`
- sort sync: `23.399900 ms`
- merge sync: `8.519050 ms`

The rejected Goal 1537 hand-written multi-block shared-memory sort failed at launch time. CUB is a better next candidate because it provides a tested block-level sort implementation with a custom comparator for full signed `int64,int64` row semantics, avoiding lossy key packing.

## Next Implementation Direction

The next RTDL prototype should be env-gated and fail closed:

- Add a CUB-backed row-width-2 tile-sort kernel compiled with the existing NVCC fallback path.
- Keep the current accepted per-tile bitonic sort as the default.
- Use the same output contract as the existing sort tile: sorted unique rows, emitted count, and overflow flag per tile.
- Validate first with a small native smoke path before wiring it into the full `collect_k_bounded` tiled merge path.
- Only promote the path after pod evidence proves parity and improves long-count timing.

## Claim Boundary

This report records feasibility only. It does not authorize speedup claims, stable primitive promotion, public release wording, or replacing the accepted Goal 1536 runtime path.
