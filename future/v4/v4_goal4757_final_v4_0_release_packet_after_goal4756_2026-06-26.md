# V4 Goal4757 Final V4.0 Release Packet After Goal4756

Status: `ready_for_external_review_not_public_tag_authorized`

This packet supersedes older bounded-operator-only V4.0 release wording. The
current V4.0 candidate is a Python eDSL/operator-pushdown release candidate and
a V2/V3 superset with a complete NVIDIA RT-core app matrix.

## Release Candidate Claim

Allowed public claim:

```text
RTDL V4.0 is a Python eDSL/operator-pushdown release candidate and V2/V3
superset. On the current NVIDIA RTX A5000 RT-core 10-app matrix, every promoted
benchmark app has V2.14, V3.0.2, and V4.0 rows. V4.0 has two material
hot-path candidate wins over V2.14 and parity/control elsewhere. Separate V4
operator surfaces and the constrained Numba custom predicate early-exit
workflow show additional bounded V4 value.
```

Not allowed:

- broad V4 speedup wording;
- broad V4-over-V2.14 or V4-over-V3 wording;
- "all benchmark apps are faster";
- unqualified app-level high-performance wording;
- public true-zero-copy wording;
- raw OptiX callback support wording;
- Tier-3 callback/PTX support wording;
- broad CuPy performance wording;
- C ABI, embedding, or non-Python host claims;
- app-specific native engine/kernel claims;
- Barnes-Hut new V4-over-V3 speedup;
- Spatial RayJoin speedup;
- LibRTS paper reproduction.

## Complete App Matrix

Evidence directory:
`future/v4/evidence/v4_goal4756_serious_all30_generated_spatial_2026-06-26/`

Analysis:

- `future/v4/evidence/v4_goal4756_final_rt_core_matrix_analysis_2026-06-26.json`
- `future/v4/v4_goal4756_final_rt_core_matrix_analysis_2026-06-26.md`
- `future/v4/v4_goal4756_final_rt_core_matrix_release_readout_2026-06-26.md`

Matrix facts:

- `10/10` promoted benchmark apps covered;
- `30/30` V2.14/V3.0.2/V4.0 rows executed successfully;
- all rows returned parseable JSON;
- no `n/a` rows;
- Embree is not used as a primary denominator;
- Spatial RayJoin uses generated grid64 shape-pair input, not the old tiny
  smoke/overlay input;
- no hot-path regressions in the Goal4756 table;
- hot-path geomean V4/V2.14 is `2.10069x`, but must not be headlined because
  it is dominated by Barnes-Hut and Triangle.

| App | V4/V2.14 hot | V4/V3.0.2 hot | Release reading |
| --- | ---: | ---: | --- |
| RTDBSCAN | `0.998x` | `0.993x` | Parity/control. |
| RayDB-style | `1.113x` | `1.111x` | Modest hot gain. |
| Triangle counting | `4.360x` | `1.021x` | Material hot-path candidate. |
| LibRTS spatial index | `0.999x` | `1.002x` | Parity/control. |
| Hausdorff XHD threshold route | `1.032x` | `0.983x` | Same-primitive threshold parity/control. |
| Robot collision | `1.020x` | `1.000x` | Parity/control. |
| Contact manifold | `1.116x` | `1.477x` | Parity/control/modest gain. |
| RTNN | `1.029x` | `1.024x` | Parity/control. |
| Spatial RayJoin shape-pair | `1.000x` | `1.004x` | Serious generated-input parity/control. |
| Barnes-Hut aggregate frontier | `286.142x` | `0.993x` | Material V3/V4-over-V2.14 candidate; not a new V4-over-V3 speed claim. |

Goal4770 Barnes-Hut delta:

- The table above remains the historical Goal4756 30-row matrix and is not
  rewritten.
- Newer RT-BarnesHut author-semantics evidence shows a checksum-valid native
  V4 RT-core route at 10M.
- After rebuilding the authors' binary with full phase printing, the authors'
  total internal program time is `10.4391s`; RTDL V4 warm execution plus input
  download is about `7.513s`.
- This corrects the earlier author-loss interpretation, but still does not
  authorize paper-reproduction wording, no-copy tree-build wording, or a public
  V2/V3/V4 RT-BarnesHut speed table.

## Operator And Workflow Evidence

The V4 operator catalog remains part of the release candidate, but it is not a
substitute for the app matrix:

- `future/v4/tier2_operator_catalog.md`
- `future/v4/README.md`
- `docs/current_v4_status.md`
- `docs/app_level_benchmark_summary.md`
- `docs/learn/performance_wording.md`

Measured V4 surfaces include fixed-radius count-threshold, closest-hit grouped
argmin, ray/triangle any-hit flags, primitive grouped-i64 reduction,
point-group nearest witness, ray/triangle weighted sum, component union, AABB
all-ops, aggregate-frontier device columns, and constrained Numba custom
predicate early-exit.

These surfaces have explicit denominators and partner scopes. They do not
authorize broad whole-application speedup claims.

## Local Verification

Targeted gate after Goal4756:

```text
Ran 44 tests in 29.779s
OK
```

Final public docs/examples/user-facing gate:

```text
Ran 33 tests in 10.971s
OK
```

Final full V4 local gate after Goal4759 evidence-manifest refresh:

```text
Ran 601 tests in 78.233s
OK
```

Full log:
`future/v4/evidence/v4_goal4759_full_v4_unittest_discover_with_review_manifest_2026-06-26.log`

Goal4757 machine gate:

- `src/rtdsl/v4_goal4757_final_release_packet.py`
- `tests/v4_goal4757_final_release_packet_test.py`

Final review evidence manifest:

- `future/v4/evidence/v4_goal4759_final_review_evidence_manifest_2026-06-26.json`
- `future/v4/v4_goal4759_final_review_evidence_manifest_2026-06-26.md`

## User-Facing Files Updated

- `README.md`
- `docs/current_v4_status.md`
- `docs/app_level_benchmark_summary.md`
- `docs/README.md`
- `docs/learn/performance_wording.md`
- `tutorials/current/README.md`
- `tutorials/current/05_measurement_boundaries.md`
- `future/v4/README.md`
- `future/v4/tier2_operator_catalog.md`
- `examples/README.md`

The public front door now presents V4 as the current clean surface. Historical
and development records remain available for reviewers, but they are not the
user learning path.

## Goal-Level Decision Audit

1. Was I foolish?

Earlier V4 work was foolish when it treated bounded operator rows as enough to
avoid a complete app-level V2.14/V3/V4 matrix. Goal4756 corrects that.

2. What actions made that decision foolish?

The mistake was allowing partial surface scorecards and old wording gates to
stand in for the user's actual question: every promoted app, same RT-core
hardware, V2.14 vs V3 vs V4, no `n/a`, no Embree primary denominator.

3. Was there another path?

Yes. The correct path was to make V4 a V2/V3 superset, run all 30 rows on the
POD, repair toy/ambiguous rows, and only then update public wording.

4. Can we solve the problem on the corrected path?

Yes. Goal4756 produced the full matrix, Goal4757 aligned code/docs/tests to it,
and the remaining release decision is external authorization, not missing local
evidence.

## Reviewer Verdict Requested

Please choose exactly one:

- `approve_v4_0_release_candidate_for_public_tag`
- `approve_with_required_wording_or_evidence_amendments`
- `block_release_pending_specific_fixes`
- `reject_release_reframe_required`

Reviewers must explicitly state whether this packet is enough for public V4.0
tagging. If not, list the exact blocking fixes.

Current review-debt record:
`future/v4/reviews/v4_goal4757_final_release_external_review_debt_2026-06-26.md`

## Non-Authorization

This packet is ready for external review. It does not by itself authorize a
public V4.0 tag. Public tagging still requires the required 3-AI release
authorization record or an explicit release-owner override.
