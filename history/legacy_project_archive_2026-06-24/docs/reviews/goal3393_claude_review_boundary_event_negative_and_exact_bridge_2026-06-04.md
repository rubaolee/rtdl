# Goal3393 - Claude Review: Boundary-Event Negative Probe and Exact Bridge

Date: 2026-06-04

Verdict: **accept-with-boundary**

Reviewed goals: 3390, 3391, 3392

---

## Review Questions

### 1. Does Goal3390 correctly classify the 4096 failure as semantic rather than resource/overflow related?

Yes. The JSON artifact records `"any_boundary_overflow": false`,
`"all_boundary_outputs_device_resident": true`,
`"boundary_rows_from_optix_device_columns": true`, and
`"candidate_rows_from_optix_device_columns": true`. Every live-device-residency
and overflow guard passes. The failure is diagnostic and attributable to a
specific geometric case: points 4283, 4284, and 4285 have legitimate exact
memberships against shape 4286, but their first boundary-crossing event carries
`crossing_t ≈ 0.006652`, far above the `1e-5` tolerance the Goal3388 signal
requires. The report additionally notes that loosening the rule to "any boundary
event" introduces false extras such as `(1647, 1641)` and `(2395, 2738)`, and
that `boundary_id > 0` is still insufficient. There is no candidate explanation
that would reduce the miss to a hardware, memory, or overflow artefact. The
semantic classification is correct.

### 2. Does the failure evidence justify blocking promotion of the Goal3388 first-boundary-event route?

Yes. The failure is not a marginal miss at a boundary condition. Three exact
pairs are unrecoverable at any tolerance that does not simultaneously introduce
false positives. The conflict is intrinsic to what the first-boundary-event
stream can represent: it reports only the earliest ray-triangle crossing per
pair, which is not sufficient to reconstruct containment for all degenerate near-
boundary configurations. No parameter adjustment to the crossing-tolerance rule
can solve this: tightening the tolerance drops valid members; loosening it admits
spurious candidates. The 4096-chain slice contains both failure modes
simultaneously (point 3738 extra, points 4283-4285 missing). Blocking route
promotion is justified.

### 3. Is Goal3391's bridge genuinely app-agnostic and honestly bounded?

Yes. The implementation of
`materialize_closed_shape_membership_rows_as_cupy_columns`
(`src/rtdsl/closed_shape_topology.py`, lines 1222–1283) accepts rows via either
`point_id`/`shape_id` or the generic `left_id`/`right_id` aliases and contains
no CDB, RayJoin, county, or application vocabulary. The output metadata contains
six explicit false flags:

```
output_residency = partner_device_after_host_refine_upload
host_refined_rows_materialized = True
native_exact_device_row_stream_produced = False
true_zero_copy_claim_authorized = False
release_authorized = False
public_speedup_claim_authorized = False
rt_core_speedup_claim_authorized = False
```

The naming `partner_device_after_host_refine_upload` is precise: data was
materialized on the host first, then uploaded. It is not zero-copy and it is not
a native device-row stream. The export in `src/rtdsl/__init__.py` (line 606) is
consistent with the implementation. The Goal3391 report (`accept-with-boundary`)
matches the implementation's actual scope. Nothing in Goal3391 overclaims.

One observation about implementation scope: `sort_output=True` is the default,
which lexsorts by `(point_id, shape_id)`. This is a reasonable default for
downstream partner continuations that consume sorted columns, but callers that
want unsorted output must pass `sort_output=False` explicitly. The behavior is
tested and the default is documented. No issue.

### 4. Does Goal3392 prove the bridge preserves exact pair identity on the 4096 slice that broke Goal3388?

Yes, cleanly. The live probe JSON records `"pairs_match_exact_rows": true`,
`"missing_exact_pair_count": 0`, `"extra_pair_count": 0`,
`"exact_row_count": 11316` = `"bridge_row_count": 11316`, on NVIDIA RTX A5000
with driver 580.126.09 against the identical slice (start=256, count=4096) that
produced the Goal3390 failure. The probe methodology is sound: it runs the same
`prepare_point_closed_shape_membership_2d_optix` → `prepared.run(points)` exact
path, passes the returned rows directly to
`materialize_closed_shape_membership_rows_as_cupy_columns`, synchronizes the
CUDA stream with `cp.cuda.Stream.null.synchronize()`, and then does a set-
equality comparison between `_row_pairs(exact_rows)` and
`_column_pairs(cp, columns)`. The probe and its test verify that the bridge
introduces neither missing nor spurious pairs.

The probe ran at commit `d7c7f92d` while the tests in the test suite ran at
`5a1d9ac1`. This is expected sequence (probe run first, tests locked against the
resulting artifact). The test suite's pass against the artifact file is the
correct verification chain.

### 5. Are all release/public-speedup/RayJoin/RT-core/true-zero-copy/default-route claims blocked correctly?

Yes. All seven claim-boundary fields are false in all three goal artifacts:

- Goal3390 JSON `claim_boundary`: `release_authorized`, `public_speedup_claim_authorized`, `rayjoin_paper_reproduction_claim_authorized`, `rtdl_beats_rayjoin_claim_authorized`, `rt_core_speedup_claim_authorized`, `true_zero_copy_claim_authorized`, `native_default_route_authorized` — all false.
- Goal3391 implementation metadata: `true_zero_copy_claim_authorized`, `release_authorized`, `public_speedup_claim_authorized`, `rt_core_speedup_claim_authorized` — all false. The `native_exact_device_row_stream_produced` false flag additionally disambiguates what the bridge is.
- Goal3392 JSON `claim_boundary` and `bridge_metadata`: all authorization fields false.

The `owner_face_priority_pipeline_contract()` in `closed_shape_topology.py` also
keeps its own claim-boundary block entirely false. No false promotion paths are
present in any of the three goal artifacts, source files, or tests.

### 6. Is the next primitive direction correct?

Yes. Goal3390's report specifies:

> inputs: points, prepared closed-shape geometry, optional candidate pair filter;
> outputs: point id, shape id, relation/witness fields, device-resident status;
> no RayJoin, CDB, county, owner-face, or application vocabulary in the native ABI;
> explicit overflow and claim-boundary metadata;
> tests that compare against existing exact host rows but keep oracle out of signal inputs.

This is the right abstraction boundary. A first-boundary-event stream is
fundamentally a signal, not an exact relation witness: it can tell you that a
ray crossed a shape boundary once at a small `t`, but it cannot reliably
distinguish interior membership from grazing or near-boundary exterior cases for
all geometry. The needed primitive is one that either produces exact containment
on-device (avoiding host refinement entirely) or emits enough per-pair geometric
evidence for a partner continuation to decide membership without re-running OptiX
or materializing host rows.

The direction avoids inventing another app-specific special case. The ABI
constraints (no RayJoin/CDB/county vocabulary, generic point/shape ids, explicit
overflow flag, claim-boundary block) are correct preconditions for the next
primitive to be promotable.

---

## Overall Assessment

The three-goal package is internally consistent and honest. Goal3390 provides a
principled negative result at the 4096-chain scale requested by the Goal3389
review, with specific geometric failure analysis and no ambiguity about
resource vs. semantic cause. Goal3391 is a small, correctly-scoped utility that
gives partner code a consistent column shape for exact rows without overclaiming
its implementation character. Goal3392 closes the loop by proving pair identity
on the exact slice that exposed the Goal3388 signal's limits.

The failure analysis leads correctly to the next primitive gap without defaulting
to an app-shaped workaround. All claim boundaries are properly maintained.

**Verdict: accept-with-boundary**

The boundary is: Goal3391's bridge is a correctness and usability utility for
current partner code; it does not satisfy any release, performance, paper-
reproduction, or zero-copy gate. The next engineering target is a generic native
exact closed-shape relation stream or relation-witness stream as specified in
Goal3390, not another tolerance parameter or app-specific filter layer.
