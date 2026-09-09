# RT-DBSCAN Complete-Output RTDL / Public-PyOptiX Transaction

Date: 2026-09-09

Status: `PASS__INTERNAL_ENGINEERING_TARGETS__EXTERNAL_REVIEW_PENDING`

## Answer First

The successor transaction closes the measured prepared-steady implementation
gap for this exact RT-DBSCAN task.  Across eight balanced fresh-process blocks,
the median RTDL/public-PyOptiX ratio is `1.0703272608056769x`; the worst block
is `1.0830616336924297x`.  Both are below the preregistered engineering limits
of `1.20x` and `1.35x`, respectively.  Every retained call returned the same
complete neighbor-count, core-flag, and canonical-component-label output.

This result does not close startup.  The secondary lifecycle endpoint is
`8.675338039 s` for RTDL and `0.611976756 s` for public PyOptiX, a
`14.175927359894695x` RTDL/PyOptiX ratio.  It also does not authorize a paper,
public, hardware-independent, or intrinsic-language performance claim.
The machine claim boundary remains `external_review_completed=false` and
`paper_claim_authorized=false`.

## Exact Task

- Input: deterministic synthetic clustered 3-D point set, 4,096 points.
- Radius: `0.055` in the frozen float32 contract.
- Minimum points: `12`, including the query point itself.
- Frozen exact directed neighbor count: `2,117,472`.
- Frozen result: 4,095 core points, four components of 1,024 points, zero
  noise points, and one non-core boundary point.
- Input manifest SHA-256:
  `69757122d68485f48638a3cc7b1356d924c7de60fed5a666faf257d065dd5978`.
- This is not an original paper dataset and is not described as one.

Both arms return all three full host-visible columns:

1. exact neighbor count for every point;
2. core predicate for every point;
3. canonical component label for every point.

## Compared Arms

Arm A is the public V4 RTDL application path.  It verifies the canonical
spatial callback and lowers it to the app-neutral prepared OptiX grouped-union
path plus generic Numba continuation.  Application names and DBSCAN-specific
formulas are absent from the native engine operation.

Arm C is a competent application-specialized public-PyOptiX implementation.
It owns explicit OptiX programs for exact degree, core-core union, and boundary
assignment, plus CUDA continuation for root extraction and canonical labels.
It does not import `rtdsl`.

For the primary prepared endpoint, both arms execute one symmetric warmup,
reuse exact immutable neighbor counts and core flags, perform exactly two
OptiX launches per timed call, materialize all three output columns, and run
the same external output oracle.  Setup, GAS construction, and exact-count
traversal are excluded from this primary timer and retained in the lifecycle
endpoint.

## Preserved Failure

The first formal transaction at source `c02eccd79d1acfd51b48a7176f8fe01581293ae8`
is immutable adverse evidence:

- median RTDL/public-PyOptiX: `2.3386578819653017x`;
- worst block: `2.3500644568476123x`;
- block-bootstrap 95% interval: approximately `[2.3280, 2.3459]`;
- RTDL block medians: approximately `10.89--11.02 ms`;
- public-PyOptiX block medians: approximately `4.65--4.70 ms`.

No predecessor sample was removed, pooled into the successor, or relabeled.

## Generic Repairs

The successor uses two app-neutral changes.

First, the stable-root boundary pass no longer retraces every source when only
predicate-false sources can change its output.  The existing threshold result
is converted once into maximal contiguous false-source ranges.  A sparse
range schedule is selected only when it does not increase the number of
native launches relative to the full-domain schedule; fragmented predicates
therefore fail safely back to the old full-domain pass.  On this exact input,
the second pass traces one relevant source instead of all 4,096 sources while
still using the existing generic range primitive.

Second, the closed V4 lowering no longer downloads invariant point IDs or
performs Python row-by-row reordering.  The lowering itself constructs dense
IDs, checks the three variable output column shapes, and canonicalizes labels
with a vectorized first-occurrence-equivalent NumPy transformation.  Tests
compare that transformation with the established scalar contract, including
negative/noise labels and non-monotonic root IDs.

No DBSCAN-native ABI, application vocabulary, dataset identity, expected
answer, or inverse outcome test was added to `src/native` or `src/rtdsl`.

## Successor Protocol

- Source commit:
  `30a2273353d1d128977b0ea99b9194e8af9f3e47`.
- Source tree:
  `0ba8e5fbfd0b31166b6613027e2e8289ef9cb541`.
- Hardware: NVIDIA RTX 4000 Ada Generation, CC 8.9.
- GPU UUID: `GPU-2a00572b-6cef-b9e6-db0a-c127783a5d46`.
- Driver: `550.127.05`.
- Python: `3.12.3`; NumPy `2.4.4`; Numba `0.65.1`; CuPy `14.0.1`;
  PyOptiX `9.1.0`.
- Native build: CUDA 12.8, OptiX headers reporting version 8.0.0,
  optimization `-O3`, `sm_89`.
- Public-PyOptiX PTX: NVRTC 12.4, PTX ISA 8.4.
- Fresh native SHA-256:
  `0a37b14940e282be65bd86e9751644d385d1a277042bb22ce72d89c83071f488`.
- Public-PyOptiX device PTX SHA-256:
  `3b2407de4182e53e528b92d763e5e056aa79104954e45e6784e22527dcfc177e`.
- Public-PyOptiX continuation PTX SHA-256:
  `ca01598742579370504588189da54808a4f78c6a6be17c7e8afd392b7aa90bd1`.
- Eight preregistered alternating-order blocks.
- Sixteen fresh-process workers, one arm per worker.
- One warmup and 215 timed calls per worker.
- 3,440 retained timed calls and 16 retained warmups.
- Zero retry and zero discard.
- Fresh first-call and lifecycle checks require three successful OptiX
  launches; every prepared timed call requires exactly two.
- Final statistical units are the sixteen worker medians paired into eight
  blocks, not the 3,440 individual calls.

## Successor Results

| Block | Order | RTDL median | PyOptiX median | RTDL / PyOptiX |
|---:|:---:|---:|---:|---:|
| 0 | A,C | 4.984218 ms | 4.711149 ms | 1.057962x |
| 1 | C,A | 5.074331 ms | 4.688108 ms | 1.082384x |
| 2 | A,C | 5.021200 ms | 4.671608 ms | 1.074833x |
| 3 | C,A | 5.045591 ms | 4.658637 ms | 1.083062x |
| 4 | C,A | 5.024949 ms | 4.709989 ms | 1.066871x |
| 5 | A,C | 5.018329 ms | 4.701529 ms | 1.067382x |
| 6 | C,A | 5.016779 ms | 4.709999 ms | 1.065134x |
| 7 | A,C | 5.068002 ms | 4.722010 ms | 1.073272x |

The median of block ratios is `1.0703272608056769x`.  The block-bootstrap
95% interval is `[1.0651337717906098, 1.0823835543037832]`.  The maximum block
ratio is `1.0830616336924297x`.  Median worker times across blocks are
`5.0230745 ms` for RTDL and `4.705759 ms` for public PyOptiX; these latter
pooled summaries are descriptive and are not substituted for the registered
paired estimator.

Both lifecycle arms had the same sampled peak GPU-memory delta of
`194,117,632` bytes at a 5 ms sampling period.  That sampler can miss shorter
peaks and is not a precise allocator trace.

## Hostile Self-Review

1. The steady result is not evidence that RTDL is faster.  PyOptiX is faster
   by about 6.6% under the registered paired estimator.
2. The strong baseline is application-specialized, while RTDL uses a generic
   path.  This supports an overhead statement for the exact task, not an
   intrinsic language comparison.
3. The sparse-source gain depends on predicate distribution.  The launch-count
   dominance rule prevents launch explosion, but other distributions can
   obtain less or no gain.
4. The primary endpoint assumes reuse.  Cold lifecycle remains roughly 14.18x
   slower for RTDL and is a material limitation for one-shot workloads.
5. The data is synthetic, one size is tested, only one GPU/driver combination
   is measured, GPU clocks are not locked, and no cross-generation result is
   available.
6. The bootstrap has eight block ratios.  Its interval describes those blocks;
   it is not a population guarantee.
7. Native and Python build identities are exact, but this internal report has
   no independent external acceptance.  Paper/public wording remains false.

## Evidence Bundles

`ADVERSE_PREDECESSOR_COMPLETE_BUNDLE.tar.zst` contains the complete failed
transaction, its native build, public-PyOptiX PTX build, and frozen input.

- Bytes: `3,675,726`.
- SHA-256:
  `d4a2817699c1b25075b7c1f819ccb169593355778543acb93877e50137ad0a42`.

`SUCCESSOR_COMPLETE_BUNDLE.tar.zst` contains the complete passing transaction,
its native build, public-PyOptiX PTX build, and the same frozen input.

- Bytes: `3,739,655`.
- SHA-256:
  `9a873a2eca02d14fcd5706c57c4dfd2739e6d11d930ed7df60e9580e33bbbe6f`.

Local SHA-256 values equal the pod values, and both archives pass complete
member listing after download.  Exact source bytes are supplied by the pushed
Git commits rather than duplicated inside either archive.

## Verdict And Next Work

The exact prepared-steady DBSCAN implementation debt is internally closed at
the preregistered engineering target.  The lifecycle debt is not closed.  The
result is ready for independent review but not for manuscript or public claim
promotion.

The next nine-application work should not continue tuning this passed row.
Priority moves to the public-authored Particle full cell-transition output
cost and the RTNN distinct-top-K duplicate-delivery correctness contract.  Any
successor for those tasks requires its own source identity, negative controls,
preregistration, complete evidence, and adverse-result retention.
