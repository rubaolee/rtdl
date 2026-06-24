# Goal 1533: OptiX COLLECT_K_BOUNDED Final Union-Rank Negative Result

## Verdict

Rejected as an implementation path in its rank-only form. The prototype built on the NVIDIA pod and made the final merge kernel extremely fast, but it failed output parity. It must not be committed as a runtime path.

This report records the negative result so the next implementation does not repeat the same mistake.

## Prototype

The experiment added an env-gated final-level kernel idea behind:

`RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_MERGE=1`

For two sorted unique row-width-2 segments, the kernel tried to compute output rank independently:

- For rows from segment A: `rank = index_in_A + lower_bound(B, row)`.
- For rows from segment B: skip if row also exists in A, otherwise `rank = index_in_B + lower_bound(A, row)`.
- Duplicate count was tracked with an atomic so emitted count could be exact.

## Pod Scope

- Pod: `root@213.173.110.196 -p 24309`
- Device: `NVIDIA RTX 2000 Ada Generation`
- Driver: `570.172.08`
- OptiX SDK: `/root/vendor/optix-sdk`, NVIDIA `optix-sdk` tag `v8.0.0`
- Base checkout before local experiment: `17dfcdc3`
- Build command: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`
- Probe command included `RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_MERGE=1` and `--allow-local-fallback-smoke`.

## What Worked

- Native build succeeded.
- The prototype preserved emitted counts and overflow flags in the tested cases.
- Final-level sync became tiny because the final merge work was no longer the serial one-thread loop:
  - `4097`: final level sync about `0.005 ms`.
  - `65537`: final level sync about `0.006 ms`.
  - `131072`: final level sync about `0.019 ms`.

## Why It Failed

The rank formula over-counts earlier duplicate rows that are skipped from segment B. That creates holes in the output rank space.

Example:

- A contains `[1, 3]`
- B contains `[1, 2]`
- B row `1` is skipped as a duplicate of A row `1`.
- A row `3` computes `rank = 1 + lower_bound(B, 3) = 3`.
- Correct compacted rank for `3` is `2`.

So the output is not a compact sorted unique sequence even though each row independently computes a plausible merged rank. The Goal1506 parity probe caught this as `same_candidate_rows=False`.

## Required Correction

A correct parallel merge/compact path needs duplicate-prefix information, not just local lower-bound ranks.

The next viable designs are:

- Parallel merge materialization into a temporary full merged buffer followed by duplicate marking and prefix/compact.
- A merge-path partition design where each partition also computes compacted duplicate-prefix offsets.
- A hybrid late-level design that uses parallel materialization and a correct bounded scan/compact for only large final levels.

## Claim Boundary

No source changes from this failed prototype were committed. This report is a negative-result artifact only. It does not authorize speedup claims, stable primitive promotion, release action, or any public-facing performance statement.

