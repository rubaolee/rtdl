# Goal5094 RT-DBSCAN AuthorOfficial Component-Signature Gate

Date: 2026-07-07

## Verdict

`completed_rt_dbscan_authorofficial_component_signature_gate_pod_optix_numba`

Goal5094 extends Goal5093 from scalar core-count equality to a bounded
same-input component-signature gate. The patched AuthorOfficial binary and RTDL
generic OptiX+Numba fixed-radius graph component signature route agree on the
tiny 3D fixture:

```text
core_count=7
component_count=2
component_sizes=[3,4]
noise_count=1
matched=true
```

This is a stronger bounded RT-DBSCAN reproduction result than Goal5093, but it
still does not claim full DBSCAN label parity, exact author label IDs, exact
paper inputs, or performance.

## What Changed

AuthorOfficial patch:

```text
Paper-reproduction-apps/rt-dbscan-paper/author_patches/goal5092_authorofficial_core_count_output.patch
```

The patch now emits:

```text
core_count
component_labels
component_sizes
noise_count
core_flags
parent_roots
```

It remains a comparator-output patch. It does not change the author's RT-DBSCAN
core-count or cluster-formation kernels.

RTDL runner:

```text
Paper-reproduction-apps/rt-dbscan-paper/scripts/run_authorofficial_component_signature_gate.py
```

Backends:

```text
cpu_reference
optix_numba_component_signature
```

The positive comparison is intentionally signature-based:

```text
{core_count, component_count, component_sizes, noise_count}
```

It does not require exact author root IDs or component-label IDs.

## RTDL Generic System Path

The RTDL POD gate used:

```text
prepare_optix_numba_radius_graph_grouped_stream_continuation_3d
radius_graph_component_signature_3d_optix_numba_prepared_grouped_stream_partner_columns
```

Key metadata from the passing POD summary:

```text
partner_reference_contract=generic_prepared_optix_numba_grouped_stream_component_size_signature_3d
native_engine_row_contract=generic_prepared_fixed_radius_grouped_union_3d_self_device_workspaces
native_execution_path=prepared_rt_core_grouped_union_3d_self_query
materializes_neighbor_rows=false
materializes_component_labels=false
materializes_directed_adjacency_stream=false
rt_core_accelerated=true
partner=numba
raw_cuda_kernel_required=false
```

This preserves the project principle: RTDL supplies a generic fixed-radius graph
component-signature operator; RT-DBSCAN remains an app that supplies epsilon,
min-points, fixture choice, and comparator policy.

## POD Execution

POD:

```text
root@213.173.108.24 -p 13502
gpu=NVIDIA RTX 4000 Ada Generation
driver=550.127.05
```

Author build:

```text
WORK_DIR=/tmp/rt_dbscan_authorofficial_goal5094 \
  bash Paper-reproduction-apps/rt-dbscan-paper/scripts/setup_authorofficial_core_count.sh
```

Author binary:

```text
/tmp/rt_dbscan_authorofficial_goal5094/build/sample02-rtdbscan
```

The POD had a Numba CUDA toolchain mismatch:

```text
Numba used CUDA 12.8 NVVM -> emitted PTX 8.7
driver JIT accepted only PTX 8.4
```

Resolution:

```text
/tmp/cuda12_0_for_numba/nvvm/lib64/libnvvm.so.4.0.0 -> /usr/lib/x86_64-linux-gnu/libnvvm.so.4.0.0
/tmp/cuda12_0_for_numba/nvvm/libdevice/libdevice.10.bc -> /usr/lib/nvidia-cuda-toolkit/libdevice/libdevice.10.bc
CUDA_HOME=/tmp/cuda12_0_for_numba
CUDA_PATH=/tmp/cuda12_0_for_numba
```

This made Numba compile kernels through the system CUDA 12.0-compatible NVVM and
libdevice stack, matching the installed driver JIT capability.

## Evidence Files

Local:

```text
Paper-reproduction-apps/rt-dbscan-paper/results/component_signature_gate_local_cpu_summary.json
```

POD:

```text
Paper-reproduction-apps/rt-dbscan-paper/results/authorofficial_component_signature_gate_pod_cpu_summary.json
Paper-reproduction-apps/rt-dbscan-paper/results/authorofficial_component_signature_gate_pod_optix_summary.json
Paper-reproduction-apps/rt-dbscan-paper/results/authorofficial_component_signature_gate_pod_author_output_optix.jsonl
```

POD AuthorOfficial payload:

```text
component_labels=[0,0,0,0,1,1,1,-1]
component_sizes=[4,3]
core_flags=[1,1,1,1,1,1,1,0]
parent_roots=[0,0,0,0,4,4,4,7]
noise_count=1
```

Normalized signature:

```text
component_sizes=[3,4]
core_count=7
noise_count=1
```

## Validation

Local tests:

```text
py -m unittest \
  tests.goal5092_rt_dbscan_authorofficial_gate_packet_test \
  tests.goal5094_rt_dbscan_authorofficial_component_signature_gate_test
```

Observed:

```text
Ran 6 tests
OK
```

JSON validation:

```text
manifest + result JSON files parse successfully
```

Patch reproducibility:

```text
git apply --check Paper-reproduction-apps/rt-dbscan-paper/author_patches/goal5092_authorofficial_core_count_output.patch
```

Observed:

```text
OK
```

## Claim Boundary

Authorized:

- bounded same-input component-signature gate passed against AuthorOfficial;
- RTDL generic OptiX+Numba fixed-radius graph component-signature route matched
  AuthorOfficial on the tiny 3D fixture;
- RT-DBSCAN app now exercises a second paper-reproduction-app gate stronger than
  scalar core count.

Not authorized:

- full RT-DBSCAN paper reproduction;
- exact paper dataset reproduction;
- exact author label ID parity;
- full DBSCAN output-format parity;
- whole-program speedup;
- author performance parity.

## Next Work

Recommended next step:

```text
Goal5095: add a second bounded same-input fixture with nontrivial border-point
assignment or multiple noise/border cases, then rerun the same component
signature gate.
```

Do not add an RT-DBSCAN-specific RTDL core primitive. Continue to use generic
fixed-radius graph component APIs.
