# Goal2550 Barnes-Hut Final Performance And Closeout

Date: 2026-05-23

## Decision

The Barnes-Hut / RT-BarnesHut-style benchmark app is closed for this phase.

The app remains a promoted RTDL research benchmark, not a public speedup claim
and not a same-contract reproduction of the PPoPP 2025 RT-BarnesHut artifact.
The final implementation boundary is:

- app and force-law semantics remain in Python / benchmark / partner code;
- native RTDL engines must not contain Barnes-Hut-specific or inverse-square
  force-law math;
- the next acceptable engine target is a reviewed app-independent traversal or
  frontier primitive, not a fused benchmark-specific force kernel.

## Final Pod

Pod command:

`ssh root@203.57.40.169 -p 10297 -i ~/.ssh/id_ed25519_rtdl_codex`

Observed GPU:

`NVIDIA RTX A5000, driver 565.57.01`

Runtime:

- Python: `/usr/bin/python3`
- PyTorch: `2.8.0+cu128`
- CUDA device: `NVIDIA RTX A5000`
- source directory used on pod: `/root/rtdl_python_only_final`

The local working tree was synced to the pod before running the final timing.
This matters because Goal2549 removed the rejected app-specific native OptiX
symbol before the final run.

## Final RTDL-Side Performance Test

Command:

```bash
cd /root/rtdl_python_only_final
export PYTHONPATH=src:. MAX_JOBS=2 TORCH_CUDA_ARCH_LIST=8.6
python3 scripts/goal2547_barnes_hut_3d_scalar_subtree_kernel.py \
  --body-count 32768 \
  --input-file /root/rtbarneshut_32768_input.txt \
  --theta 0.5 \
  --softening 0.0 \
  --repeats 20 \
  --json-out docs/reports/goal2550_barnes_hut_final_3d_scalar_subtree_pod_32768_2026-05-23.json
```

Artifact:

`docs/reports/goal2550_barnes_hut_final_3d_scalar_subtree_pod_32768_2026-05-23.json`

Result:

| Metric | Value |
| --- | ---: |
| Bodies | `32768` |
| Tree nodes | `4679` |
| Leaf nodes | `4094` |
| Repeats | `20` |
| Resident kernel min | `0.502848 ms` |
| Resident kernel mean | `0.521787 ms` |
| CPU tree prepare | `330.190 ms` |
| Host-to-device tensor prepare | `202.097 ms` |
| Visited-node delta vs Python reference | `0` |
| Contribution-row delta vs Python reference | `0` |
| Max scalar relative error | `3.301934e-05` |
| Mean scalar relative error | `1.679237e-07` |

Interpretation:

The final RTDL-side test is the partner-resident Torch/CUDA 3-D scalar
subtree-containment diagnostic path. It validates the generic prepared-tree
contract and the app-side inverse-square force interpretation against the RTDL
Python reference. It is not a native RTDL engine primitive.

## Authors Artifact Orientation Row

Authors artifact:

- repository: `https://github.com/vani-nag/OWLRayTracing`
- branch: `BarnesHutRT`
- local pod path: `/root/OWLRayTracing_BarnesHutRT`
- binary: `build-rtdl-bh-optix81-cuda126/rtbarneshut`

Direct same-input reload attempt:

```bash
./build-rtdl-bh-optix81-cuda126/rtbarneshut treelogy /root/rtbarneshut_32768_input.txt
```

Result: five attempted runs segfaulted. Therefore the authors artifact did not
provide a usable same-input baseline on this pod.

Authors-supported `new` mode was rerun as an orientation baseline only:

```bash
./build-rtdl-bh-optix81-cuda126/rtbarneshut new /root/rtbarneshut_final_new_32768_repeat_${i}.txt
```

Artifacts:

`docs/reports/goal2550_barnes_hut_authors_new_mode_pod_logs/`

Observed force-phase timings:

| Repeat | Force phase |
| ---: | ---: |
| 1 | `5.405 ms` |
| 2 | `5.489 ms` |
| 3 | `5.414 ms` |
| 4 | `5.448 ms` |
| 5 | `6.124 ms` |

Authors-supported `new` mode summary:

| Metric | Value |
| --- | ---: |
| Force min | `5.405 ms` |
| Force mean | `5.576 ms` |
| Preprocess min | `18.501 ms` |
| Execution min | `27.059 ms` |

This is useful only as an orientation row. It must not be presented as an
apples-to-apples speedup because RTDL and the authors artifact still differ in
tree construction and traversal contract, and direct same-input authors reload
failed on this pod.

## Final Performance Conclusion

The final engineering conclusion is:

- The best RTDL-side partner-resident diagnostic row is `0.502848 ms` for 32K
  bodies on RTX A5000.
- The authors-supported artifact row observed in `new` mode is `5.405 ms`
  force-phase minimum on the same pod.
- No public speedup ratio is authorized.
- No same-contract authors-code comparison is authorized.
- No native-engine Barnes-Hut or inverse-square force primitive is authorized.

The app is closed because further useful work would be a new design phase:
either a generic native frontier/traversal primitive or a reviewed partner
operator mechanism. Continuing to tune the benchmark-specific Torch/CUDA
diagnostic would not improve the RTDL language/runtime boundary.

## Claim Boundary

Allowed statements:

- Barnes-Hut is a promoted RTDL research benchmark app.
- The benchmark forced new app-agnostic contracts for aggregate trees,
  opening-frontier traversal, materialization-pressure accounting, and
  partner-resident fused accumulation.
- The final RTDL-side 32K A5000 diagnostic run reached `0.502848 ms` min with
  zero structural-count deltas against the RTDL Python reference.
- The authors artifact was built and timed in its supported `new` mode, but
  same-input reload segfaulted on this pod.

Disallowed statements:

- RTDL reproduces the RT-BarnesHut paper.
- RTDL is faster than the authors implementation in a same-contract comparison.
- RTDL has a native app-independent OptiX aggregate-frontier force primitive.
- The `0.502848 ms` versus `5.405 ms` rows authorize a public speedup claim.

## Closeout

Barnes-Hut is done for the current benchmark-app phase.

Next version work should not be another Barnes-Hut app optimization unless it
is explicitly framed as one of:

- generic native aggregate-frontier traversal/frontier-row production;
- partner operator plug-in design for user-supplied force/reduction math;
- same-contract authors-code reproduction after fixing the authors artifact's
  same-input reload path.
