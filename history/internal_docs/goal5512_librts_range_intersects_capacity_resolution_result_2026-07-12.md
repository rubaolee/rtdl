# Goal5512 LibRTS Large-Case Capacity Resolution

Status: `implemented__one_exact_count_match__one_author_cuda_capacity_failure__review_pending`

## Objective

Resolve the two cases left without independent checkpoints by Goal5509. Run
each case separately, preserve the author failure class if the author cannot
complete, and avoid turning missing output into a semantic mismatch.

## Results

| Case | Author status | RTDL status | Result |
|---|---|---|---|
| parks.bz2 | CUDA allocation failure (`cudaErrorMemoryAllocation`) | not run after author failure | author capacity failure |
| lakes.bz2 | completed, `10,579,596` | completed, `10,579,596` | count match |

The parks author run used the normal workspace serialize path and failed with
Thrust `bad_alloc`. A capacity audit showed the POD had substantial free host
memory; the failure is the author CUDA workload allocation, not evidence of an
RTDL semantic mismatch. RTDL was correctly not run after the author failed.

The lakes author run initially hit a workspace output-stream error. A retry
using a temporary local serialize directory avoided the workspace quota path;
the author completed and the RTDL generic route matched its result count. The
retry result is stored as the canonical lakes case after normalizing its
temporary retry case id.

## Claim boundary

This goal resolves the process state of the two Goal5509 cases, but does not
complete the exact archive matrix. It establishes one additional count-level
match and one author-side capacity boundary. It does not claim pair-row
equality, Figure 6 reproduction, full-paper reproduction, performance parity,
zero-copy, author algorithm equivalence, or Embree evidence. No performance
ratio is authorized.

Machine-readable evidence:

```text
Paper-reproduction-apps/librts-paper/results/goal5512_parks_bz2_select0001_10000.json
Paper-reproduction-apps/librts-paper/results/goal5512_lakes_bz2_select0001_10000.json
Paper-reproduction-apps/librts-paper/results/goal5512_range_intersects_capacity_resolution_gate.json
```

The remaining exact archive pairs are still separate work. A future attempt to
make parks.bz2 executable must be a new capacity question, not an implicit
semantic correction or a performance comparison.
