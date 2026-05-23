# Goal2545-2547 Barnes-Hut Resident, Float32, And 3-D Optimization

Date: 2026-05-23

## Scope

This packet follows Goal2544's subtree-containment optimization. It covers:

- Goal2545: resident-state repeated timestep benchmark;
- Goal2546: float32 subtree-containment kernel;
- Goal2547: 3-D scalar inverse-square subtree-containment prototype.

These are still app-agnostic RTDL partner prototypes. They do not put
Barnes-Hut app names or app-specific logic into the native engine.

## Pod

Pod:

`ssh root@203.57.40.169 -p 10297 -i ~/.ssh/id_ed25519_rtdl_codex`

Device:

`NVIDIA RTX A5000`, driver `565.57.01`

## Goal2545 Resident-State Result

Script:

`scripts/goal2545_barnes_hut_resident_state_benchmark.py`

Artifact:

`docs/reports/goal2545_barnes_hut_resident_state_pod_32768_2026-05-23.json`

At 32,768 bodies, with prepared tree/tensors reused for 100 launches:

| Metric | Time |
|---|---:|
| CPU tree preparation | `514.319 ms` |
| host-to-device tensor preparation | `196.769 ms` |
| resident event min per timestep | `3.565 ms` |
| resident event mean per timestep | `3.698 ms` |
| resident wall per timestep | `3.721 ms` |

Interpretation: after setup, the repeated resident execution path is stable at
about `3.6-3.7 ms` per force evaluation for the 2-D float64 generic vector-sum
contract.

## Goal2546 Float32 Result

Script:

`scripts/goal2546_barnes_hut_float32_subtree_kernel.py`

Artifacts:

- `docs/reports/goal2546_barnes_hut_float32_subtree_pod_32768_2026-05-23.json`
- `docs/reports/goal2546_barnes_hut_float32_subtree_pod_32768_r20_2026-05-23.json`

At 32,768 bodies:

| Kernel | Resident min (ms) | Resident mean (ms) | Notes |
|---|---:|---:|---|
| Goal2544 float64 subtree | `3.971` | `3.978` | 5 repeats |
| Goal2546 float32 subtree | `0.473` | `0.611` | 20 repeats; one launch outlier |

Accuracy versus the float64 Python reference:

| Metric | Value |
|---|---:|
| visited-node delta | `0` |
| contribution-row delta | `0` |
| max vector relative error | `8.545e-05` |
| mean vector relative error | `8.121e-07` |

Interpretation: float32 is a major speed lever for this benchmark shape. It
needs an explicit precision policy before it can be promoted beyond diagnostic
prototype status.

## Goal2547 3-D Scalar Result

Script:

`scripts/goal2547_barnes_hut_3d_scalar_subtree_kernel.py`

Artifacts:

- `docs/reports/goal2547_barnes_hut_3d_scalar_subtree_pod_authors_input_8192_2026-05-23.json`
- `docs/reports/goal2547_barnes_hut_3d_scalar_subtree_pod_authors_input_32768_2026-05-23.json`

This path changes the RTDL prototype from the earlier 2-D vector force contract
to a 3-D scalar inverse-square force-sum contract:

`generic_aggregate_frontier_inverse_square_scalar_sum_3d_v1`

It uses authors-generated input files from the pod:

- `/root/rtbarneshut_8192_repeat_1.txt`
- `/root/rtbarneshut_32768_repeat_1.txt`

At 32,768 bodies on the authors-generated input:

| System | Resident/force phase min (ms) | Boundary |
|---|---:|---|
| Authors OWL/OptiX RT-BarnesHut | `6.616` | published artifact force phase |
| RTDL Goal2547 3-D scalar CUDA | `0.509` | same dimension/input/force shape, not same tree contract |

The authors artifact was recompiled at `NUM_POINTS=32768` for the diagnostic
comparison and patched from device ordinal `1` to `0` for the one-GPU pod.
RTDL correctness here is against RTDL's own 3-D Python reference, not the
authors' per-body force output. No speedup ratio should be inferred from this
table.

Correctness versus RTDL's own 3-D Python reference:

| Metric | Value |
|---|---:|
| visited-node delta | `0` |
| contribution-row delta | `0` |
| max scalar relative error | `4.329e-05` |
| mean scalar relative error | `1.741e-07` |

Interpretation: this is a much stronger comparison setup than the earlier 2-D
vector prototype because it shares the authors' dimensionality, scalar
inverse-square force shape, and input file. It is still not a same-contract
authors-code claim because the RTDL tree construction and traversal contract
are generic RTDL subtree-containment, not the authors' exact OWL/OptiX
triangle/autorope traversal.

## Overall Timing Matrix

| Stage | 32K resident min (ms) | Meaning |
|---|---:|---|
| Goal2542 2-D rope float64 | `37.036` | before subtree containment |
| Goal2544 2-D subtree float64 | `3.971` | O(1) source containment |
| Goal2545 2-D resident repeated float64 | `3.565` | prepared-state repeated launch |
| Goal2546 2-D subtree float32 | `0.473` | precision-reduced diagnostic path |
| Goal2547 3-D scalar float32 | `0.509` | same dimension/input/force shape as authors, not same tree |
| Authors OWL/OptiX force phase | `6.616` | published artifact, force phase only |

The `0.509 ms` and `6.616 ms` figures are both phase-only orientation numbers
under different tree/traversal contracts. They are not a public speedup ratio.

## Engineering Conclusion

The next RTDL language/runtime features forced by this benchmark are now clear:

- prepared aggregate-tree descriptors need subtree-end and source-leaf metadata;
- partner/native paths need resident state as a first-class execution mode;
- precision must be part of the contract, not an accidental implementation
  detail;
- a 3-D scalar aggregate-frontier reduction is required for credible
  authors-facing Barnes-Hut comparisons;
- exact public claims still need same-tree/same-contract alignment or an
  explicitly reviewed claim boundary.

## Claim Boundary

Authorized internal statements:

- Resident-state repeated execution is stable around `3.6-3.7 ms` per 32K
  2-D float64 force evaluation after setup.
- The 32K float32 2-D diagnostic path reaches `0.473 ms` min with small
  relative error against the float64 reference.
- The 32K 3-D scalar diagnostic path on an authors-generated input reaches
  `0.509 ms` min and matches RTDL's own Python reference counts.

Not authorized:

- public speedup claims;
- paper reproduction claims;
- same-contract RTDL-vs-authors claims;
- claims that the native OptiX engine already implements this path.
