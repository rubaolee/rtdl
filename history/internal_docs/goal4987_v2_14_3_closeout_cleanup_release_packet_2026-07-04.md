# Goal4987 Result: v2.14.3 Closeout, Cleanup Audit, And Release Packet

Date: 2026-07-04

## Verdict

```text
completed_v2_14_3_closeout_packet_ready_for_external_review
```

Goal4987 closes Goals 4983-4987 as a bounded v2.14.3 release packet.

It does not claim the repository is ready to push without human review. It does claim the v2.14.3 technical packet is internally coherent, tested locally, documented, and ready for external review.

## Scope Completed

| Goal | Result | Output |
|---|---|---|
| 4983 | LSI warm/prepare strategy decided | Keep `~2.7s` LSI producer in fresh headline; no warm-only claim |
| 4984 | Correctness and genericity gate passed | 85 local tests OK, 1 GPU runtime subtest skipped locally |
| 4985 | Final bounded performance matrix written | Primary top4 fresh result `4.220s`; secondary steady-process result `3.669s`; no top4 author ratio |
| 4986 | Public docs updated | RayJoin app README and v2.14 release packet now reflect bounded v2.14.3 boundary |
| 4987 | Cleanup/status audit written | Pure transient caches removed; dirty tree classified as project state |

## Final v2.14.3 Technical State

v2.14.3 is a bounded performance and documentation update for the RayJoin paper-reproduction binary route.

The key technical line is:

```text
RTDL as writer-free binary overlay operator, not as paper text-output writer
```

Current top4 County x Zipcode representative evidence:

| Route | Time | Claim boundary |
|---|---:|---|
| Earlier writer-free top4 route | `7.851s` | superseded baseline |
| v2.14.3 fresh/cold binary route | `4.220s` | primary bounded result |
| v2.14.3 repeated full route, LSI included | median `3.669s` | secondary steady-process evidence |
| prepared/cached LSI replay | diagnostic only | not a fresh overlay result |

Top4 author compute ratio:

```text
not measured
```

The smaller public-sample author timing is not used as a top4 denominator.

## What Changed In Code

Tracked modified files:

```text
Paper-reproduction-apps/rayjoin-paper/README.md
docs/release_reports/v2_14/rayjoin_reproduction_packet.md
src/native/optix/rtdl_optix_api.cpp
src/native/optix/rtdl_optix_prelude.h
src/native/optix/rtdl_optix_workloads.cpp
src/rtdsl/embree_runtime.py
src/rtdsl/optix_runtime.py
tests/goal4374_rayjoin_exact_paper_suite_test.py
```

Primary new untracked code/test assets:

```text
Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
scripts/goal4970_run_section57_top4_matrix.py
scripts/goal4970_stage_top4_arcgis_cdb.py
tests/goal4955_projected_descriptor_pipeline_test.py
tests/goal4956_columnar_xsect_pipeline_test.py
tests/goal4964_exact_lsi_pair_id_device_columns_test.py
tests/goal4968_planar_map_lsi_workspace_contract_test.py
tests/goal4972_bounded_exact_lsi_producer_test.py
tests/goal4973_exact_lsi_cost_decomposition_test.py
tests/goal4974_point_location_device_face_columns_route_test.py
tests/goal4977_fast_scaled_point_pack_test.py
tests/goal4978_grouped_carrier_decomposition_test.py
tests/goal4979_grouped_carrier_side_work_metrics_test.py
tests/goal4981_reversed_side_order_binary_route_test.py
```

Internal evidence and review artifacts are stored under:

```text
history/internal_docs/
```

## Cleanup Performed

Pure transient cleanup:

```text
initial cleanup removed __pycache__ dirs: 38
post-validation cleanup removed __pycache__ dirs: 8
total removed __pycache__ dirs: 46
```

No project-state files were deleted.

Reason:

- source changes, tests, scripts, reports, and artifacts are part of the v2.14.3 evidence chain;
- deleting them would destroy reproducibility and review traceability;
- final git cleanup/staging should be a human-reviewed release step, not an automatic reset.

## Current Git Status Summary

```text
modified tracked files: 8
untracked files/dirs:   122
total status entries:   130
```

Untracked top-level categories:

| Category | Count |
|---|---:|
| `history/` | 108 |
| `tests/` | 11 |
| `scripts/` | 2 |
| `Paper-reproduction-apps/` | 1 |

This is dirty, but it is not unexplained cache dirt. It is v2.14.3 project state awaiting external review and release staging.

## Validation

### Public/internal leakage scan

Command:

```text
rg "Goal[0-9]+|Claude|Gemini|Antigravity|Codex|verdict|call_for_review|internal_docs|2\\.04x" README.md docs examples/current tutorials/current Paper-reproduction-apps/rayjoin-paper/README.md -n
```

Result:

```text
0 matches
```

A broader exploratory scan for `author.*parity` found one Barnes-Hut benchmark non-goal string:

```text
"authors-code timing or parity"
```

This is not a RayJoin/v2.14.3 leak and not an internal process leak.

### Local test gate

Command:

```text
$env:PYTHONPATH='src'; py -m unittest tests.goal4977_fast_scaled_point_pack_test tests.goal4978_grouped_carrier_decomposition_test tests.goal4979_grouped_carrier_side_work_metrics_test tests.goal4981_reversed_side_order_binary_route_test tests.goal4948_non_rayjoin_hit_stream_numba_genericity_test tests.goal4964_exact_lsi_pair_id_device_columns_test tests.goal4968_planar_map_lsi_workspace_contract_test tests.goal4972_bounded_exact_lsi_producer_test tests.goal4973_exact_lsi_cost_decomposition_test tests.goal4974_point_location_device_face_columns_route_test tests.goal4374_rayjoin_exact_paper_suite_test tests.goal4866_rayjoin_section57_output_contract_test tests.goal4373_rayjoin_cdb_point_location_route_test tests.goal4834_rayjoin_sos_synthetic_contract_test tests.goal4894_directed_point_location_fine_grained_default_test tests.goal4955_projected_descriptor_pipeline_test
```

Result:

```text
Ran 85 tests in 2.580s
OK (skipped=1)
```

The skip is a local OptiX + Numba CUDA runtime subtest. This local Windows machine did not execute that GPU runtime subtest.

### Local Linux non-RayJoin runtime genericity gate

The skipped Windows GPU runtime subtest was rerun on local Linux:

```text
host: lx1 / 192.168.1.20
GPU: NVIDIA GeForce GTX 1070
driver: 580.126.09
```

Command:

```text
cd /home/lestat/work/v2143_p1_runtime_check
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=/home/lestat/work/v2_v3_v4_serious_lx1_20260619_221102/build/librtdl_optix.so
export RTDL_OPTIX_LIB=/home/lestat/work/v2_v3_v4_serious_lx1_20260619_221102/build/librtdl_optix.so
python3 -m unittest tests.goal4948_non_rayjoin_hit_stream_numba_genericity_test
```

Result:

```text
Ran 2 tests in 0.714s
OK
```

This is a non-RayJoin runtime genericity smoke only. It is not a performance benchmark.

### Compile gate

Command:

```text
$env:PYTHONPATH='src'; py -m py_compile Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py src/rtdsl/embree_runtime.py src/rtdsl/optix_runtime.py
```

Result:

```text
passed
```

## Known Boundaries

Authorized:

- v2.14.3 bounded writer-free binary route improvement;
- public docs explaining the binary route as pipeline-operator evidence;
- no top4 author ratio measured;
- LSI producer remains the main unresolved cost;
- paper text route remains the correctness anchor.

Not authorized:

- no author-performance parity;
- no warm-only headline;
- no prepared/cached replay as fresh overlay;
- no broad RTDL speedup claim;
- no public claim that true device-resident overlay is complete;
- no claim that RTDL core has no remaining RayJoin identity traces;
- no claim that legacy `rayjoin_cdb` names or bundled `rtdsl.rayjoin_overlay` have already been renamed/relocated.

## Release Staging P1 Gates From Full Technical Review

The full technical review returned:

```text
approve_technical_packet_but_require_release_staging_cleanup
```

No P0 blocker was found, but these P1 gates must be handled before any human push:

1. **Genericity wording gate.** Public/release-stage wording must say that the new v2.14.3 primitives and public route are generic, while legacy `rayjoin_cdb` native symbols and bundled `rtdsl.rayjoin_overlay` remain in-tree pending rename/relocation.
2. **Non-RayJoin runtime gate.** The local Windows non-RayJoin GPU runtime genericity subtest was skipped, then rerun on local Linux + GTX 1070 and passed. This closes the runtime genericity smoke for staging, but it authorizes no performance claim.
3. **Performance matrix provenance gate.** The `7.851s -> 4.220s` matrix is assembled from separated validated runs, not a same-session benchmark sweep. Either rerun a same-session matrix or disclose this boundary.
4. **Internal-doc exclusion gate.** `history/internal_docs/` contains internal goal IDs, reviewer names, process language, and review artifacts. It must be explicitly excluded from public artifacts unless intentionally archived as internal history.

## Recommended External Review Verdict

```text
approve_v2_14_3_closeout_packet_for_release_staging
```

or, if the reviewer requires a cleaner working tree before approval:

```text
approve_technical_packet_but_require_release_staging_cleanup
```

## Next After Approval

After external approval:

1. decide which internal artifacts remain in `history/internal_docs/`;
2. stage source/docs/tests/scripts intentionally;
3. avoid staging transient run outputs unless needed as evidence;
4. create a v2.14.3 release/staging commit or handoff branch;
5. keep the next performance line separate from v2.14.3.
