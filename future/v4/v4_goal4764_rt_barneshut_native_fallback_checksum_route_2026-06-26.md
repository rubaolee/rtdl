# Goal4764: RT-BarnesHut Native ABI Checksum Route

Date: 2026-06-26

Status: complete as runnable native-ABI checksum route; not complete as RT-core/native V4 operator.

## Decision

Goal4764 implemented the first runnable route behind the new RT-BarnesHut 3D author-semantics native ABI.

The route now:

- accepts author-format CUDA device columns for point ids, x, y, z, and mass;
- downloads those columns into the native layer;
- runs an author-compatible 3D z-order, bucket-size-32 Barnes-Hut tree and force law on host as a fallback;
- uploads the force output back to a native-owned CUDA device buffer;
- returns nonzero native device output pointers through `RtdlRtBarnesHutAuthor3DOutput`;
- passes checksum parity against the Goal4760 CPU oracle on 4,096 and 8,192 author-format Treelogy rows.

This is a real implementation step because the ABI/dataflow/output/checksum route now runs end to end. It is not a performance step and it is not the RT-core implementation.

## Code Changed

- `src/native/optix/rtdl_optix_api.cpp`
  - added author-compatible host-side z-order comparator;
  - added author-compatible 3D bucket tree construction with bucket size 32;
  - added author-compatible theta `0.5` force computation;
  - changed `rtdl_optix_run_rt_barneshut_author_3d` from fail-closed to runnable fallback;
  - returns `implementation_status_code=2` for `host_fallback_author_semantics_checksum_route`.

- `src/rtdsl/v4_rt_barneshut_native_route.py`
  - added ctypes wrapper for the three native ABI symbols;
  - added `V4RtBarnesHutNativeFallbackRun`;
  - copies native force device output back through CuPy for checksum validation;
  - records `native_v4_operator_available=false`, `host_fallback_used=true`, and `rt_core_execution=false`.

- `scripts/v4_rt_barneshut_native_fallback_route_probe.py`
  - loads author-format data;
  - creates CuPy device columns;
  - calls the native ABI route;
  - compares checksum against the Goal4760 CPU oracle;
  - exits nonzero if checksum tolerance fails.

- Tests:
  - `tests/v4_goal4762_rt_barneshut_native_feasibility_test.py`
  - `tests/v4_goal4763_rt_barneshut_native_abi_first_slice_test.py`
  - `tests/v4_goal4764_rt_barneshut_native_fallback_route_test.py`

## Validation

Local source/static tests:

```text
py -m unittest tests.v4_goal4762_rt_barneshut_native_feasibility_test tests.v4_goal4763_rt_barneshut_native_abi_first_slice_test tests.v4_goal4764_rt_barneshut_native_fallback_route_test
Ran 12 tests in 1.397s
OK (skipped=1)
```

POD native build:

```text
cd /root/rtdl_v4_candidate_pod
make build-optix OPTIX_PREFIX=/workspace/vendor/optix-dev-8.0.0 CUDA_PREFIX=/usr/local/cuda
```

Result: build succeeded and produced `/root/rtdl_v4_candidate_pod/build/librtdl_optix.so`.

POD tests:

```text
cd /root/rtdl_v4_candidate_pod
export RTDL_OPTIX_LIB=/root/rtdl_v4_candidate_pod/build/librtdl_optix.so
export RTDL_OPTIX_LIBRARY=/root/rtdl_v4_candidate_pod/build/librtdl_optix.so
/root/rtdl_v4_venv/bin/python -m unittest tests.v4_goal4762_rt_barneshut_native_feasibility_test tests.v4_goal4763_rt_barneshut_native_abi_first_slice_test tests.v4_goal4764_rt_barneshut_native_fallback_route_test
Ran 12 tests in 0.823s
OK
```

## POD Checksum Evidence

Evidence directory:

`future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/`

| Evidence | Rows | Status | Checksum relative error | Abs-checksum relative error | Pass |
|---|---:|---|---:|---:|---|
| `v4_goal4764_rt_barneshut_native_fallback_4096_pod_2026-06-26.json` | 4,096 | `native_3d_author_semantics_host_fallback_available` | `2.9873327390354115e-15` | `2.9873327390354115e-15` | yes |
| `v4_goal4764_rt_barneshut_native_fallback_8192_pod_2026-06-26.json` | 8,192 | `native_3d_author_semantics_host_fallback_available` | `1.7966991826615097e-14` | `1.7966991826615097e-14` | yes |
| `v4_goal4764_rt_barneshut_native_fallback_feasibility_pod_2026-06-26.json` | n/a | symbols exported and fallback available | n/a | n/a | yes |

The feasibility evidence confirms the rebuilt POD library exports:

```json
{
  "rtdl_optix_prepare_rt_barneshut_author_3d": true,
  "rtdl_optix_run_rt_barneshut_author_3d": true,
  "rtdl_optix_destroy_rt_barneshut_author_3d": true
}
```

## Claim Boundary

Allowed statement:

> RTDL V4 now has a runnable native ABI checksum route for the authors' RT-BarnesHut input/tree/force semantics. It passes 4,096/8,192-row checksum parity on the NVIDIA POD, but currently uses a host fallback behind the ABI.

Forbidden statements:

- V4 has a native RT-core RT-BarnesHut operator.
- V4 reproduces the RT-BarnesHut paper performance.
- V4 is faster than the authors' RT-BarnesHut implementation.
- This result authorizes a V2.14/V3/V4 RT-BarnesHut speed table.
- The old 2D RTDL aggregate-tree workflow is author-equivalent.
- This route can be added to a V4 high-performance geomean.

## What Changed Compared With Goal4763

Goal4763:

- native ABI symbols existed and exported;
- `run` intentionally failed closed;
- no checksum route existed.

Goal4764:

- `run` returns a native-owned force device buffer;
- checksum parity passes on 4,096 and 8,192 author-format rows;
- route status is `native_3d_author_semantics_host_fallback_available`;
- the implementation is explicitly host fallback, not RT-core.

## Next Goal

Goal4765 should replace the host fallback with an author-compatible OptiX traversal/force implementation behind the same ABI.

Required exit evidence:

1. keep the same 4,096/8,192 checksum gates passing;
2. set a new implementation status for RT-core/native traversal only after the route no longer downloads hot force work to host;
3. compare phase timing against the Goal4761 external author binary route only after checksum parity passes;
4. do not run 1M/10M scale tables until the RT-core route passes the small checksum gates.

## Goal-Level Decision Audit

1. Was I being stupid?
   - The stupid path would be to call this a native RT-core performance route just because it runs behind the native ABI.

2. What action would make it stupid?
   - Hiding the host fallback, using the timing as RT-core timing, or counting this route as V4 operator speed evidence.

3. Is there another path that avoids getting stuck on a bad premise?
   - Yes: mark the implementation status as host fallback and use it only as a checksum/dataflow gate for the next RT-core replacement.

4. Can I now try the different path that actually solves the problem?
   - Yes. Goal4765 must port the author-compatible traversal/force work to OptiX while preserving these checksum gates.

## Non-Authorization

Goal4764 does not authorize:

- V4 release based on RT-BarnesHut;
- RT-BarnesHut paper reproduction claims;
- RT-core/native operator availability claims;
- speedup claims;
- V2/V3/V4 author-speed tables;
- old 2D workflow divided by author binary;
- generic V4 operator geomean credit.

It authorizes only:

> The native V4 RT-BarnesHut 3D author-route ABI can now execute a checksum-valid author-semantics host fallback and return native CUDA output columns on the POD. The RT-core traversal/force implementation remains the next required engineering step.
