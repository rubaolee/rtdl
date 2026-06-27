# V4 Goal4747 - RT-Core-Only App Matrix Recheck

Date: 2026-06-26

Status: `in_progress_rt_core_denominator_recheck_not_release`

Decision:
`embree_is_control_only__no_na_public_rows__rt_core_denominators_required`

## Why This Goal Exists

The user challenged two release-facing mistakes:

1. RTDL is an NVIDIA RT-core project. Embree is useful as a CPU/control
   reference, but it is not the primary denominator for V4/V2.14 user claims.
2. Public app matrices must not say `n/a`. If a full-app ratio is missing, the
   table must state the concrete blocker.

Both objections are valid.

## POD And Tooling Facts

Current RTX POD:

```bash
ssh root@194.68.245.170 -p 22089 -i ~/.ssh/id_ed25519_rtdl_codex_current_pod
```

Verified:

```text
host: 0256b71980f1
gpu: NVIDIA RTX A5000
driver: 570.195.03
v2 root: /root/rtdl_v2_14_tag
v3 root: /root/rtdl_v3_0_2_tag
v4 root: /root/rtdl_v4_candidate_pod
python: /root/rtdl_v4_venv/bin/python
```

Important correction: do not use the default `~/.ssh/id_ed25519`; it is the
wrong key for this POD.

Old-tag OptiX compatibility libraries must be exposed through both names:

```bash
RTDL_OPTIX_LIB=/root/rtdl_v2_14_tag/build/librtdl_optix.v4compat.so
RTDL_OPTIX_LIBRARY=/root/rtdl_v2_14_tag/build/librtdl_optix.v4compat.so
```

## Current App Matrix Recheck

| App | Current RT-core comparison status | User-facing interpretation |
| --- | --- | --- |
| `rt_dbscan` | Measured full app on OptiX/partner route: V4/V2.14 hot `1.086x`, V4/V3.0.2 hot `1.083x`. | Real but modest gain; below formal high-performance bar. |
| `raydb_style` | Measured full app on OptiX grouped-reduction route; latest repaired table says V4/V2.14 hot `1.103x`, V4/V3.0.2 hot `1.105x`. | Repaired modest device-output win; not a major app-level win. |
| `triangle_counting` | Measured full app on OptiX weighted any-hit route: V4/V2.14 hot `6.381x`, V4/V3.0.2 hot `1.043x`. | Valid candidate row after high-repeat focused rerun. |
| `librts_spatial_index` | Measured full app on prepared OptiX AABB route: V4/V2.14 hot `1.003x`, V4/V3.0.2 hot `1.004x`. | Parity; V2.14 already had the prepared OptiX primitive. |
| `hausdorff_xhd` | Existing V4/V2.14 `201581x` uses a V2.14 Embree exact-summary denominator. V3/V4 exact nearest-witness routes are RT-core. V2.14 strict RT-core route exists as threshold-decision mode, not the same exact nearest-witness metric. | Do not headline V4/V2.14. Use V4/V3.0.2 `2.546x` only as same-family signal; rerun or redesign a true RT-core-only exact denominator before any V2.14 claim. |
| `rtnn` | Measured serious rows: V4/V2.14 hot `0.999x` at 262,144 and `0.994x` at 1,048,576; V4/V3.0.2 hot `1.005x` and `0.993x`. | Measured no-win at serious scale. |
| `robot_collision` | No certified full-app V4/V2.14 same-primitive row. Current clean boundary evidence: OptiX flags subroute `5.053x` over Embree control, but V2.14 already had prepared OptiX any-hit flags. | Not `n/a`: blocker is "same OptiX primitive existed in V2.14; full-app same-primitive V4 speed row not certified." |
| `contact_manifold` | No fresh generic V4 bounded-witness route. V2.14 already had bounded OptiX collect-k; current target would rebrand existing collect-k and partner witness plumbing. | Not `n/a`: blocker is "design no-go until a fresh generic bounded-witness route exists." |
| `spatial_rayjoin` | No complete current V4 app route. Shape-pair subprobe is RT-core related but failed: V4/V2.14 hot `0.963x`, V4/V3.0.2 hot `0.977x`. | No speed credit; needs a real relation-topology V4 route. |
| `barnes_hut` | Focused full app workflow measured: V4/V2.14 hot `282.468x`, V4/V3.0.2 hot `1.003x`; V2.14 route used OptiX membership with host frontier/CPU continuation. | Candidate versus V2.14 due host-frontier removal; not a new RT-core force-law claim and not a V4-over-V3 speed win. |

## Hausdorff RT-Core Smoke Recheck

The old V2.14 CLI does not accept V4's backend spelling:

```text
--backend optix_device_max_nearest
```

It accepts:

```text
--backend optix --optix-summary-mode directed_threshold_prepared --require-rt-core
```

Smoke command:

```bash
cd /root/rtdl_v2_14_tag
PYTHONPATH=src:. \
RTDL_OPTIX_LIB=/root/rtdl_v2_14_tag/build/librtdl_optix.v4compat.so \
RTDL_OPTIX_LIBRARY=/root/rtdl_v2_14_tag/build/librtdl_optix.v4compat.so \
/root/rtdl_v4_venv/bin/python \
  examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py \
  --backend optix \
  --optix-summary-mode directed_threshold_prepared \
  --hausdorff-threshold 0.4 \
  --require-rt-core \
  --copies 1024 \
  --repeat 3 \
  --warmup 1
```

Result:

- `rt_core_accelerated: true`
- `matches_oracle: true`
- `native_continuation_backend: optix_threshold_count`
- `run_phases.query_fixed_radius_threshold_reached_count_sec: 0.0097148567`
- `run_phases.scene_prepare_sec: 2.0275066085`

Interpretation: V2.14 has an RT-core Hausdorff decision route, but it is a
threshold-decision route, not the same exact nearest-witness/max route used by
V3/V4. Therefore it cannot replace the Embree denominator as a clean V2.14
exact Hausdorff speed ratio without a new protocol.

## Immediate Corrections Applied

- Public app tables no longer use `n/a` for Robot or Contact.
- Hausdorff is marked as a V2.14 denominator outlier where the raw `201581x`
  appears.
- Refresh runbook now records the correct POD key, old-tag OptiX env vars,
  local Linux GPU limitation, Embree-as-control-only rule, and no-`n/a` rule.

## Required Next Work

1. Build or write a V2.14/V3/V4 RT-core-only app-matrix runner.
   - It must not use Embree as a primary denominator.
   - It may keep Embree as a side control column.
   - It must fail closed when a version lacks same semantics.

2. Replace the Hausdorff V2.14 denominator.
   - Either find/build a same-semantics V2.14 exact nearest-witness OptiX route,
     or keep Hausdorff V4/V2.14 unclaimed and report only V4/V3.0.2.

3. Replace Robot/Contact status cells with measured rows only after a full
   route exists.
   - Robot requires frozen same-primitive V2.14-vs-V4 full-app timing.
   - Contact requires a fresh generic bounded-witness V4 route first.

4. Re-run public docs/tests after the table correction.

## Claim Boundary

Goal4747 authorizes no V4 tag, no broad speedup claim, no all-benchmark claim,
no Hausdorff V4/V2.14 headline, no Robot speed claim, no Contact speed claim,
and no Embree-primary app-level release claim.

## Goal-Level Decision Audit

1. Was I foolish?

Yes.

2. What action made the decision foolish?

I used the wrong SSH key, then hand-set the wrong old-tag OptiX env var, and I
let public app tables retain `n/a` instead of naming the blocker.

3. Was there another path?

Yes. Read the refresh runbook first, update it when it lacked key facts, use
the known POD key, use the runner helper env contract, and make missing app
rows explicit blockers.

4. Can I now try a different path that actually solves the problem?

Yes. Treat Embree as control-only, require RT-core app denominators, and build
the next runner around same-semantics V2.14/V3/V4 routes instead of reusing the
old mixed-denominator matrix.
