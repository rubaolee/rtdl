# Goal4762: RT-BarnesHut Native V4 Feasibility Gate

Date: 2026-06-26

Status: complete as fail-closed feasibility gate; native V4 RT-BarnesHut author route remains not implemented.

## Decision

Goal4762 answers the immediate question: can the existing RTDL native V4 route honestly host the RT-BarnesHut paper semantics?

Answer: **not yet**.

The existing native surface contains the 2D RTDL aggregate-tree fused weighted-vector-sum route:

- `rtdl_optix_prepare_aggregate_tree_fused_weighted_vector_sum_2d`
- `rtdl_optix_run_aggregate_tree_fused_weighted_vector_sum_2d`
- `rtdl_optix_destroy_aggregate_tree_fused_weighted_vector_sum_2d`

That route is useful and remains valid for the RTDL 2D aggregate workflow, but it is not the author RT-BarnesHut program. The author route needs a 3D author-contract native ABI and it does not exist yet:

- `rtdl_optix_prepare_rt_barneshut_author_3d`
- `rtdl_optix_run_rt_barneshut_author_3d`
- `rtdl_optix_destroy_rt_barneshut_author_3d`

Goal4762 therefore adds a fail-closed V4 gate so future code cannot silently fall back to the old 2D route or the external author binary and call that a native V4 RT-BarnesHut result.

## Code Added

- `src/rtdsl/v4_rt_barneshut_native_route.py`
  - records required native 3D author-route symbols;
  - records existing 2D aggregate-tree symbols;
  - inspects the source tree for those symbols;
  - exposes `run_v4_rt_barneshut_native_author_route`, which fails closed until native symbols and validation exist;
  - preserves non-release/non-speed claim boundaries.

- `scripts/v4_rt_barneshut_native_feasibility_probe.py`
  - emits machine-readable native feasibility evidence.

- `tests/v4_goal4762_rt_barneshut_native_feasibility_test.py`
  - verifies the existing 2D symbols are present;
  - verifies the 3D author symbols are missing;
  - verifies the native route fails closed instead of falling back;
  - verifies the probe writes reviewable JSON evidence.

## Validation

Local:

```text
py -m unittest tests.v4_goal4760_rt_barneshut_author_contract_test tests.v4_goal4761_rt_barneshut_author_route_test tests.v4_goal4762_rt_barneshut_native_feasibility_test
Ran 11 tests in 4.098s
OK
```

POD:

```text
cd /root/rtdl_v4_candidate_pod
/root/rtdl_v4_venv/bin/python -m unittest tests.v4_goal4760_rt_barneshut_author_contract_test tests.v4_goal4761_rt_barneshut_author_route_test tests.v4_goal4762_rt_barneshut_native_feasibility_test
Ran 11 tests in 2.033s
OK
```

## Evidence

Evidence directory:

`future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/`

| Evidence | Source root | Status | Existing 2D symbols | Missing native 3D author symbols |
|---|---|---|---:|---:|
| `v4_goal4762_rt_barneshut_native_feasibility_2026-06-26.json` | local workspace | `blocked_missing_native_3d_author_semantics_rt_core_route` | 3/3 | 3/3 |
| `v4_goal4762_rt_barneshut_native_feasibility_pod_2026-06-26.json` | `/root/rtdl_v4_candidate_pod` | `blocked_missing_native_3d_author_semantics_rt_core_route` | 3/3 | 3/3 |

The POD evidence records the required dataflow:

- author-format input or device-column ingest;
- 3D `x/y/z` float32 position columns;
- mass column with author CSV scaling when applicable;
- author z-order or equivalent tree order;
- bucket-size-32 leaf contract;
- 3D tree/BVH nodes with child or rope/resume metadata;
- theta `0.5` author opening rule;
- author force-law checksum parity;
- phase seconds for preprocessing, RT force, execution, and wall.

## Meaning

Goal4762 closes the ambiguity that caused the earlier bad comparison:

- The RTDL 2D aggregate-tree Barnes-Hut-style workflow is real, but not author-equivalent.
- The external author binary route is real RT-core evidence, but not native V4.
- V4 still needs a native 3D author-semantics route before any RT-BarnesHut paper-reproduction speed claim is allowed.

This is a blocker, not a release win.

## Next Goal

Goal4763 should implement the first native V4 3D RT-BarnesHut author-route slice:

1. add the native ABI symbols listed above;
2. bind 3D `x/y/z/mass/id` device columns and author-compatible tree metadata;
3. run the native route on 4,096 and 8,192 author-format rows;
4. compare checksum against the Goal4760 oracle;
5. compare phase timings against the Goal4761 external author reference route;
6. do not scale to 1M until checksum parity passes.

## Goal-Level Decision Audit

1. Was I being stupid?
   - The stupid path would be to treat the existing 2D aggregate-tree route as sufficient for RT-BarnesHut paper reproduction.

2. What action would make it stupid?
   - Dividing the old 2D RTDL workflow by the authors' 3D binary, or calling the external author binary a native V4 operator.

3. Is there another path that avoids getting stuck on a bad premise?
   - Yes: a fail-closed native feasibility gate that names the missing 3D ABI and refuses fallback.

4. Can I now try the different path that actually solves the problem?
   - Yes. Goal4763 must implement the missing native 3D route and pass checksum parity before any performance table.

## Non-Authorization

Goal4762 does not authorize:

- V4 release based on RT-BarnesHut;
- public RT-BarnesHut paper reproduction wording;
- V2/V3/V4 RT-BarnesHut same-semantics speed table;
- old 2D Barnes-Hut workflow divided by author binary;
- external author binary counted as native V4;
- generic V4 operator geomean credit from this route.

It authorizes only:

> V4 now has a machine-checked fail-closed gate proving that the native RT-BarnesHut author-semantics route is still missing, with exact symbols and dataflow required for the next implementation goal.
