# Goal5093 RT-DBSCAN AuthorOfficial Core-Count POD Execution

Date: 2026-07-07

## Verdict

`completed_rt_dbscan_authorofficial_core_count_gate_pod_optix`

The bounded same-input RT-DBSCAN core-count gate passed on the live CUDA/OptiX
POD. The patched AuthorOfficial sample and RTDL OptiX backend both reported:

```text
point_count=8
epsilon=0.35
min_points=3
core_count=7
matched=true
```

This closes the Goal5092 packet as an executed same-input AuthorOfficial
comparator gate for the call-1 RT-DBSCAN core predicate count.

## Scope

Closed:

- patched author `sample02-rtdbscan` builds and runs on POD;
- AuthorOfficial emits bounded JSON core-count payload;
- RTDL `fixed_radius_count_threshold_3d` OptiX route runs on the same input;
- exact integer equality holds for `core_count`.

Not closed:

- full DBSCAN label reproduction;
- exact paper dataset reproduction;
- cluster formation parity;
- whole-program speedup;
- author performance parity.

The positive claim is only:

```text
bounded_core_count_reproduction_claim_authorized=true
paper_reproduction_claim_authorized=false
performance_claim_authorized=false
whole_program_speedup_claim_authorized=false
```

## POD Environment

POD:

```text
root@213.173.108.24 -p 13502
hostname=45c502cfccb5
gpu=NVIDIA RTX 4000 Ada Generation
driver=550.127.05
```

The working SSH identity was:

```text
~/.ssh/id_ed25519_rtdl_codex_current_pod
```

Tooling available:

```text
git
cmake
nvcc
/root/vendor/optix-dev/include/optix.h
```

## AuthorOfficial Build

Author source:

```text
repo=https://github.com/vani-nag/OWLRayTracing
branch=rt-dbscan
commit=92749fe82ed001e5b7303265d4a2a73aa1bbf529
sample=samples/cmdline/s02-rtdbscan
```

Setup script:

```text
Paper-reproduction-apps/rt-dbscan-paper/scripts/setup_authorofficial_core_count.sh
```

Patch:

```text
Paper-reproduction-apps/rt-dbscan-paper/author_patches/goal5092_authorofficial_core_count_output.patch
```

Patch contents:

- removes the author's absolute local `parallel_for.h` include;
- emits a bounded JSON payload with `core_count`;
- leaves the RT-DBSCAN kernels intact;
- adds an OWL/OptiX compatibility flag:

```text
OPTIX_PRIMITIVE_TYPE_FLAGS_CUSTOM
```

The compatibility flag was required on this OptiX driver/toolchain. Without it,
the author sample linked OptiX program groups without custom-primitive support
and failed at pipeline launch.

Build location:

```text
/tmp/rt_dbscan_authorofficial_goal5093/build/sample02-rtdbscan
```

## RTDL OptiX Build

RTDL native library was built on the POD with:

```text
make build-optix OPTIX_PREFIX=/root/vendor/optix-dev CUDA_PREFIX=/usr CXX_OPTIX="/usr/bin/nvcc -ccbin /usr/bin/g++-12"
```

Native library:

```text
/root/rtdl_goal5093/build/librtdl_optix.so
```

Runtime environment:

```text
RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so
RTDL_OPTIX_PTX_COMPILER=nvcc
RTDL_OPTIX_PTX_ARCH=compute_89
RTDL_OPTIX_CUBIN_ARCH=sm_89
```

## Evidence Files

Local evidence copied back from POD:

```text
Paper-reproduction-apps/rt-dbscan-paper/results/authorofficial_core_count_gate_pod_cpu_summary.json
Paper-reproduction-apps/rt-dbscan-paper/results/authorofficial_core_count_gate_pod_optix_summary.json
Paper-reproduction-apps/rt-dbscan-paper/results/authorofficial_core_count_gate_pod_author_output.jsonl
Paper-reproduction-apps/rt-dbscan-paper/results/authorofficial_core_count_gate_pod_author_output_optix.jsonl
```

CPU-reference gate:

```text
author.core_count=7
rtdl.backend=cpu_reference
rtdl.core_count=7
author_comparator_used=true
matched=true
bounded_core_count_reproduction_claim_authorized=true
paper_reproduction_claim_authorized=false
```

RTDL OptiX gate:

```text
author.core_count=7
rtdl.backend=optix
rtdl.core_count=7
author_comparator_used=true
matched=true
bounded_core_count_reproduction_claim_authorized=true
paper_reproduction_claim_authorized=false
```

RTDL OptiX metadata:

```text
native_engine_row_contract=generic_fixed_radius_count_threshold_3d_device_columns
native_execution_path=prepared_rt_core_count_threshold_3d
native_symbol=rtdl_optix_write_prepared_fixed_radius_count_threshold_3d_device_outputs
materializes_neighbor_rows=false
rt_core_accelerated=true
partner=numba
```

The author JSON records timing fields, but Goal5093 does not authorize any
performance claim. They are diagnostic only.

## Verification

Local packet test:

```text
py -m unittest tests.goal5092_rt_dbscan_authorofficial_gate_packet_test
```

Observed:

```text
Ran 3 tests
OK
```

Patch reproducibility check:

```text
git apply --check Paper-reproduction-apps/rt-dbscan-paper/author_patches/goal5092_authorofficial_core_count_output.patch
```

Observed:

```text
OK
```

The local test now also guards that the AuthorOfficial patch contains the OWL
custom-primitive compatibility hunk.

## Claim Boundary

Authorized:

- bounded same-input RT-DBSCAN core-count gate passed against AuthorOfficial;
- RTDL OptiX generic fixed-radius count-threshold route matched AuthorOfficial
  for the tiny 3D fixture;
- the paper app now has a live AuthorOfficial comparator result for the first
  bounded RT-DBSCAN reproduction gate.

Not authorized:

- full RT-DBSCAN paper reproduction;
- exact paper input reproduction;
- independent cluster label parity;
- whole-program DBSCAN correctness;
- performance or speedup;
- claim that this bounded gate covers the author's cluster formation pass.

## Next Work

The next RT-DBSCAN paper-app step should be chosen explicitly:

1. Expand from core-count to a bounded label/component signature gate.
2. Add a second same-input fixture to test nontrivial cluster formation.
3. Keep the RTDL side on generic fixed-radius / threshold primitives; do not add
   an RT-DBSCAN-specific core primitive.

The immediate Goal5093 result is complete.
