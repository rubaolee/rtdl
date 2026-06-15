# Goal4388 Partner Dual-Implementation Policy And Current App Performance

Date: 2026-06-15

Status: v2.14 closeout addendum. The RTDBSCAN partner gap is closed by
Goal4389; the same rule remains binding for future V3.0 M1 claims.

## Conclusion

Current v2.14 app performance is strongest where the benchmark row is primitive-first: RTDL native primitives return compact counts, flags, summaries, or bounded rows without app-specific continuation dominating the runtime. Performance is weaker or more caveated where the app still needs partner or Python continuation after RT traversal.

New rule:

> If a benchmark-app claim needs partner continuation, the project must test at least two partner implementations: the current best-performance partner for that contract, and a Numba implementation because it gives users a Python-source, no-C++/CUDA-kernel-writing path.

This rule does not mean Numba must win. It means Numba must be present as an accessibility/reference implementation whenever partner continuation is part of the story.

## Current Performance Snapshot

| Row | Current performance readout | Partner posture | Interpretation |
| --- | --- | --- | --- |
| RTNN ranked summary | exact OptiX 10.14x-11.80x over Embree; separate float32 CuPy graph path 47.36x-89.85x | exact row primitive-first; CuPy best path separated | strong primitive row; partner-best row needs precision caveat |
| RTDBSCAN core flags | 524K total 1.05x OptiX over Embree; threshold stage 1.37x; Goal4389 partner sweep: RT+Numba 8.900s vs RT+CuPy 10.662s | fixed Numba continuation for backend comparison; same-contract CuPy opponent measured | fair but continuation-dominated; current best measured partner for this contract is Numba |
| RayJoin LSI | OptiX 29.93x over Embree | primitive-first | strong scalar-count row |
| RayJoin PIP | OptiX 1.10x over Embree | primitive-first final row; CuPy/Numba routes separated | modest row; partner routes need dual testing before partner claims |
| RayJoin overlay | 2 exact-ready pairs: OptiX 2.61x and 1.88x over Embree | app orchestration; partner/fusion debt | public-review-ready for the available 2/8 exact subset; full 8/8 Section 5.7 wording remains blocked |
| RayDB-style grouped count | OptiX 14.05x per iteration | primitive-first native grouped reduction | strong fused reduction row |
| LibRTS AABB | 1M hot query 13.39x; cold total 2.27x | primitive-first | strong prepared AABB row |
| Triangle counting | largest row total 2.44x; hot query 107.61x | primitive-first scalar; optional CuPy/Numba for compaction/preprocess | strong primitive row; partner only for non-scalar continuation |
| Barnes-Hut node coverage | 1M bodies x 65,536 nodes hot query 2.06x | primitive-first node coverage | useful traversal row; full force requires partner/native continuation |
| Hausdorff threshold | 1,048,576 points per side hot query 1.58x | primitive-first threshold | useful decision row, not exact witness distance |
| Robot collision | xlarge total 1.86x; traversal 6.69x | primitive-first prepared buffers | strong traversal row, not planner/continuous collision |
| Contact manifold | AABB query 1.23x; hot path 1.16x | primitive-first broadphase; Python refinement app-owned | modest but clean broadphase row |

## Partner-Needed Rows And Required Dual Tests

| Workload family | When partner is needed | Best-performance partner to test | Required Numba test | Current v2.14 status |
| --- | --- | --- | --- | --- |
| RTDBSCAN | component labeling / union / convergence after core flags | Numba prepared-grid component continuation for the current contract; CuPy remains the same-contract opponent | Numba prepared-grid component continuation | current v2.14 gap closed by Goal4389: 524K RT+Numba 8.900s, RT+CuPy 10.662s, signatures equal |
| RayJoin PIP/overlay | exact ring/refinement, topology filtering, face-id continuation, overlay output assembly | CuPy for dense/device refinement where fastest | Numba scalar/topology/reference continuation | final v2.14 scalar rows are primitive-first; partner-dependent claims remain separated |
| Barnes-Hut full force | force-vector accumulation after frontier/node coverage | CuPy/Torch/Triton best measured path | Numba no-RawKernel block-reduction reference | v2.14 reports node coverage only |
| Triangle candidate compaction | compact mask / candidate-row interpretation after scalar answer | CuPy for current compact-mask performance | Numba compact-mask continuation | v2.14 reports scalar any-hit summary only |
| RayDB unfused grouped continuation | grouped reductions when not already fused native | current best among Triton/CuPy/Torch for the contract | Numba grouped continuation reference | v2.14 release row uses fused native grouped reduction |
| Hausdorff exact path | exact nearest-witness / grouped frontier continuation | CuPy RawKernel or best CUDA partner | Numba reference if available for same contract | v2.14 reports threshold decision only |
| Contact exact refinement | triangle refinement/contact interpretation after AABB broadphase | CuPy or best geometry refinement partner | Numba geometry refinement reference | v2.14 reports Python refinement as app-owned, not partner performance |

## Gate Rule

For any future partner-dependent benchmark claim:

1. Fix the RTDL primitive output contract first.
2. Hold the RTDL backend comparison separate from the partner comparison.
3. Test the current best-performance partner.
4. Test Numba on the same contract, data, repeat protocol, and validation oracle.
5. Report both correctness and phase timing.
6. Do not claim automatic partner selection.
7. Do not let a partner-specific route change native RTDL semantics.

## Effect On v2.14

v2.14 can close because its public-review-ready rows are mostly primitive-first or explicitly mark partner-dependent claims as separated. RTDBSCAN also now has a same-contract best-partner plus Numba supplement. The rule above remains binding for V3.0 M1 design and for any future v2.14 public wording expansion.

The immediate practical consequence:

- RTDBSCAN is acceptable as a fixed-Numba same-continuation engineering row.
- RTDBSCAN is also acceptable as a current partner-dual-tested row for the prepared-grid component-continuation contract; Numba is the measured winner at 524K.
- Any V3.0 RayJoin/Barnes-Hut/Triangle/RayDB partner claim must include best partner plus Numba, with no-C++/CUDA-kernel-writing Numba called out as the accessibility path.
