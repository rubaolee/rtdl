# V4 Goal4746 Final Release-Candidate Review Packet

Date: 2026-06-26

Status: `complete_pending_external_review_debt`

Decision:
`final_v4_release_candidate_packet_ready_for_external_review`

## Current Product Claim

RTDL V4 is a Python eDSL/operator-pushdown release candidate for generic
RT-core operators and constrained user predicates.

Authorized release-candidate label:

```text
RTDL V4 Python eDSL/operator-pushdown release candidate: 10 measured generic RT-core operator surfaces including constrained custom predicate early-exit at serious scale; broad legacy all-app speedup remains unauthorized
```

Current app-level decision label:

```text
bounded_high_performance_python_edsl_release_candidate__not_all_benchmark_apps_faster
```

## What V4 Adds Over V2.14

V2.14 already had many high-performance primitives and partner routes. V4's
real advancement is not "every old app is faster." It is:

- a unified Python V4 front door: `import rtdsl.v4 as rtdl_v4`;
- a measured generic operator catalog with 10 measured operator/workflow
  surfaces;
- operator pushdown for constrained predicates, including the custom predicate
  early-exit workflow;
- explicit partner scope for Torch CUDA, Numba, RTDL native, and named CuPy
  continuation rows;
- fail-closed callback planning for unsupported complex logic;
- current public docs and machine release state aligned on the same boundary.

## Current Benchmark-App Boundary

V4 does not claim that all 10 historical benchmark apps are faster than V2.14.

| App | V4/V2.14 hot | V4/V3.0.2 hot | Current reading |
| --- | ---: | ---: | --- |
| Hausdorff XHD | `201581.860x` denominator outlier | `2.546x` | Candidate row, but the V2.14 denominator is an Embree directed-summary route; do not headline the raw V2 ratio. |
| Triangle counting | `6.381x` | `1.043x` | App-level candidate win after high-repeat focused rerun. |
| Barnes-Hut | `282.468x` | `1.003x` | App-level candidate versus V2.14, V3 no-regression; no RT-core force-law claim. |
| RayDB-style | `1.103x` | `1.105x` | Regression repaired; modest device-output win below candidate bar. |
| RTDBSCAN | `1.086x` | `1.083x` | Modest gain, below formal high-performance bar. |
| LibRTS spatial index | `1.003x` | `1.004x` | Parity, not a V4 speed win. |
| RTNN | `0.999x / 0.994x` | `1.005x / 0.993x` | Measured no-win at serious scales. |
| Robot collision | full-app V4/V2.14 not certified; OptiX flags subroute `5.053x` over Embree control | full-app V4/V3.0.2 not certified | V2.14 already had prepared OptiX any-hit flags; current V4 evidence repairs the native boundary but does not prove a new same-primitive V4 speed win. |
| Contact manifold | blocked: no fresh generic V4 bounded-witness route | blocked: no fresh generic V4 bounded-witness route | V2.14 already had bounded OptiX collect-k; current target would rebrand existing collect-k/partner witness work, so it needs a new generic route before timing. |
| Spatial RayJoin | `0.963x` subprobe | `0.977x` subprobe | No current full V4 route; shape-pair subprobe failed bars. |

Candidate benchmark-app rows versus V2.14 with V3 no-regression:

1. `hausdorff_xhd`
2. `triangle_counting`
3. `barnes_hut`

Hausdorff caveat: the raw V4/V2.14 hot ratio compares V4's OptiX/CuPy route with
a V2.14 Embree directed-summary denominator at 262,144 points/side. The
same-family V4/V3.0.2 hot comparison is `2.546x`; the 1,048,576 points/side
coordinate-normalized row is correctness-boundary evidence, not a speed
headline.
The app matrix must not use `n/a`: incomplete ratios are explicit blockers, not
blank data.

## V4-Only Workflow Win

| Workflow | API surface | V4/V2.14 | V4/V3.0.2 | Reading |
| --- | --- | ---: | ---: | --- |
| Custom predicate early-exit | `v4_ray_triangle_custom_predicate_early_exit_3d_numba` | `4.633x` | `4.633x` | True V4 operator-pushdown workflow win versus materialized-device fallback. |

## Local Validation

- Full V4 unittest discover: `561` tests, `OK`.
- Public examples and catalog dry-run gate: `OK`.
- Current-path stale Goal label scan: no current user/front-door matches.
- Quickstart payload front-door status:
  `v4_python_edsl_operator_pushdown_front_door_goal4742_current_release_framing`.
- Scope gate status:
  `v4_python_edsl_operator_pushdown_scope_goal4742_current_release_framing`.

## Current Evidence Chain

- Goal4742: current release framing after blocker closure.
- Goal4743: public docs/current front-door cleanup.
- Goal4744: full V4 local gate after front-door cleanup.
- Goal4745: machine release decision and guardrail refresh to current boundary.

## External Review Request

External reviewers should answer:

1. Is this a coherent V4 release candidate for a Python eDSL/operator-pushdown
   surface?
2. Is the product claim honest given the app-level matrix?
3. Is the custom predicate early-exit row correctly framed as V4-specific value?
4. Do docs, quickstart, scope gate, and machine release decision align?
5. Is the 561-test local gate sufficient for local engineering confidence?
6. Should final public tag be authorized now, or should release remain blocked
   pending specific amendments?

## Required Verdict Labels

- `authorize_final_v4_tag_under_bounded_release_candidate_label`
- `approve_release_candidate_but_block_final_tag_until_amendments`
- `reject_release_candidate_overclaim_or_incomplete`

## Goal-Level Decision Audit

1. Was I being foolish?

No. After changing docs and machine state, a final review packet is required so
external reviewers inspect one coherent current truth instead of scattered
evidence.

2. If yes, what action made the decision foolish?

Not applicable.

3. Was there another path?

Yes. Continue engineering without an external packet. That would violate the
project's review discipline at the release boundary.

4. Can I now try a different path that actually solves the problem?

Yes. Send this packet for external review while continuing only safe,
non-claim-changing cleanup.

## Non-Authorization

Goal4746 itself authorizes no final V4 tag, no all-benchmark speedup claim, no
broad V4-over-V2.14 wording, no arbitrary callback claim, no raw OptiX callback
claim, no true-zero-copy claim, no non-Python embedding/C ABI claim, and no
app-specific native kernel.
