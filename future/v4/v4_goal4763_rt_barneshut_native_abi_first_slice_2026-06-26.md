# Goal4763: RT-BarnesHut Native 3D ABI First Slice

Date: 2026-06-26

Status: complete as native ABI first slice; OptiX traversal/force kernel still not implemented.

## Decision

Goal4762 proved the native V4 author-semantics RT-BarnesHut route was missing. Goal4763 moves the work one step into the native layer:

- the C ABI symbols now exist in the native OptiX backend;
- the rebuilt POD `librtdl_optix.so` exports all three symbols;
- the Python feasibility gate now reports `native_3d_author_semantics_symbols_present_unvalidated`;
- the runtime still fails closed because the actual OptiX traversal and force kernel are not implemented.

This is a real engineering step, but it is not a performance result.

## Code Changed

- `src/native/optix/rtdl_optix_prelude.h`
  - added `RtdlRtBarnesHutAuthor3DOutput`;
  - declared:
    - `rtdl_optix_prepare_rt_barneshut_author_3d`
    - `rtdl_optix_run_rt_barneshut_author_3d`
    - `rtdl_optix_destroy_rt_barneshut_author_3d`

- `src/native/optix/rtdl_optix_api.cpp`
  - added `RtBarnesHutAuthorPrepared3D`;
  - implemented prepare/run/destroy first-slice ABI;
  - validates nonzero 3D device pointers for nonempty input;
  - `run` returns a clear fail-closed error until traversal/force kernel exists.

- `src/rtdsl/v4_rt_barneshut_native_route.py`
  - distinguishes `native_v4_abi_symbols_available` from `native_v4_operator_available`;
  - keeps `native_v4_operator_available=false`;
  - records the next implementation steps after symbols exist.

- `scripts/v4_rt_barneshut_native_feasibility_probe.py`
  - added `--goal`;
  - added optional `--optix-lib` dynamic export check.

- Tests:
  - `tests/v4_goal4762_rt_barneshut_native_feasibility_test.py`
  - `tests/v4_goal4763_rt_barneshut_native_abi_first_slice_test.py`

## Validation

Local:

```text
py -m unittest tests.v4_goal4762_rt_barneshut_native_feasibility_test tests.v4_goal4763_rt_barneshut_native_abi_first_slice_test
Ran 7 tests in 1.308s
OK (skipped=1)
```

The skipped local test is the dynamic library export check, because the local Windows workspace does not have a rebuilt `librtdl_optix.so`.

POD build:

```text
cd /root/rtdl_v4_candidate_pod
make build-optix OPTIX_PREFIX=/workspace/vendor/optix-dev-8.0.0 CUDA_PREFIX=/usr/local/cuda
```

Result: build completed successfully and produced `/root/rtdl_v4_candidate_pod/build/librtdl_optix.so`.

POD tests:

```text
cd /root/rtdl_v4_candidate_pod
export RTDL_OPTIX_LIB=/root/rtdl_v4_candidate_pod/build/librtdl_optix.so
export RTDL_OPTIX_LIBRARY=/root/rtdl_v4_candidate_pod/build/librtdl_optix.so
/root/rtdl_v4_venv/bin/python -m unittest tests.v4_goal4762_rt_barneshut_native_feasibility_test tests.v4_goal4763_rt_barneshut_native_abi_first_slice_test
Ran 7 tests in 0.795s
OK
```

## Evidence

Evidence directory:

`future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/`

| Evidence | Status | Export check |
|---|---|---|
| `v4_goal4763_rt_barneshut_native_abi_first_slice_2026-06-26.json` | `native_3d_author_semantics_symbols_present_unvalidated` | local source scan only |
| `v4_goal4763_rt_barneshut_native_abi_first_slice_pod_2026-06-26.json` | `native_3d_author_semantics_symbols_present_unvalidated` | POD dynamic library exported all 3 symbols |

POD export check:

```json
{
  "rtdl_optix_prepare_rt_barneshut_author_3d": true,
  "rtdl_optix_run_rt_barneshut_author_3d": true,
  "rtdl_optix_destroy_rt_barneshut_author_3d": true
}
```

Important claim boundary:

```json
{
  "native_v4_abi_symbols_available": true,
  "native_v4_operator_available": false,
  "public_rt_barneshut_paper_reproduction_claim_authorized": false,
  "v2_v3_v4_author_speed_table_authorized": false
}
```

## What Changed Compared With Goal4762

Goal4762:

- native author-route symbols were absent;
- evidence status was `blocked_missing_native_3d_author_semantics_rt_core_route`.

Goal4763:

- native author-route symbols are present and exported after rebuild;
- evidence status is `native_3d_author_semantics_symbols_present_unvalidated`;
- the operator is still unavailable because the actual traversal/force implementation is not done.

## Next Goal

Goal4764 should implement the first runnable native route behind `rtdl_optix_run_rt_barneshut_author_3d`:

1. bind 3D author-format points to native device columns;
2. add author-compatible tree/BVH metadata, not the RTDL 2D aggregate-tree rows;
3. implement a first force output buffer path;
4. validate checksum parity against the Goal4760 CPU oracle on 4,096 and 8,192 rows;
5. compare phase timing against the Goal4761 external author binary only after parity passes.

No 1M/10M scale run is authorized before checksum parity.

## Goal-Level Decision Audit

1. Was I being stupid?
   - The stupid path would be to treat ABI symbol export as a complete native operator.

2. What action would make it stupid?
   - Setting `native_v4_operator_available=true`, publishing a speed table, or claiming RT-BarnesHut reproduction before checksum parity.

3. Is there another path that avoids getting stuck on a bad premise?
   - Yes: separate ABI availability from operator availability and make `run` fail closed until traversal/force is real.

4. Can I now try the different path that actually solves the problem?
   - Yes. Goal4764 must fill the implementation behind the ABI and pass checksum parity.

## Non-Authorization

Goal4763 does not authorize:

- V4 release based on RT-BarnesHut;
- RT-BarnesHut paper reproduction claims;
- V2/V3/V4 same-semantics speed table;
- old 2D workflow divided by author binary;
- external author route counted as native V4;
- native operator availability claims;
- generic V4 operator geomean credit.

It authorizes only:

> The native V4 RT-BarnesHut 3D author-route ABI first slice now builds and exports on the POD. The actual OptiX traversal/force operator remains to be implemented and checksum-validated.
