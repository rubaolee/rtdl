# Phoenix V3 M38 Component-Union Focused POD Protocol Report

Date: 2026-06-23

Status: `m38_protocol_accepted_after_external_review_harness_gate_required`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
focused_pod_spend_authorized_now: false
all_app_pod_spend_authorized: false
component_union_material_probe_closed: false
```

## Purpose

M38 converts the M37 component-union core node into a bounded focused-POD
protocol. It does not run POD and does not authorize POD spend.

Protocol files:

- `docs/rebuild/v3/phoenix_v3_m38_component_union_focused_pod_protocol_2026-06-23.json`
- `docs/rebuild/v3/phoenix_v3_m38_component_union_focused_pod_protocol_2026-06-23.md`

## Controlling Points

- The row is non-toy: clustered 3D fixed-radius component-union labels at
  `262144` points, warmup `1`, repeat `5`.
- Variant commands are proposed M39 harness commands only; M38 does not claim
  the runner script exists and does not authorize executing it.
- The productized route must use
  `run_radius_graph_component_union_3d_prepared_session`.
- Component-signature output cannot substitute for component-union labels.
- Success requires matching component-label-derived canonical signatures across
  all variants.
- Material candidate status requires at least `1.20x` over Embree same-contract
  control on both hot query median and runner-inclusive wall.
- Productized coverage must also avoid a legacy OptiX regression below `0.98x`.
- All-app POD remains blocked.

## Resource Estimate

If later authorized after review and harness gating:

```text
local M39 harness work: 1.5-3.0 h
focused POD wall time: 0.75-1.5 h
focused POD cost at $1 / 4 h: $0.19-$0.38
hard cap before new review: 2 h / $0.50
all-app POD: not authorized
```

## Recommended Review Outcome

Claude returned:

```text
accept_m38_authorize_one_focused_component_union_pod_after_harness_gate
```

Recorded review:

- `docs/reviews/claude_phoenix_v3_m38_component_union_focused_pod_protocol_recorded_review_2026-06-23.md`

Codex+Claude consensus:

- `docs/reviews/codex_claude_phoenix_v3_m38_component_union_focused_pod_protocol_2ai_consensus_2026-06-23.md`

Interpretation: M38 is accepted as the protocol. It still does not run POD.
The next step is M39 local harness implementation and local gates; after those
gates, one focused component-union POD run is authorized by the consensus.

## Validation

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_m38_component_union_focused_pod_protocol_test \
  tests.v3_release_wording_gate_test
Ran 9 tests in 4.881s
OK

PYTHONPATH=src;. py -3 scripts/run_test_matrix.py --group v3_rebuild
module_count: 118
Ran 614 tests in 76.082s
OK
stdout: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m38_protocol_tightening_20260623_140000.stdout.txt
stderr: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m38_protocol_tightening_20260623_140000.stderr.txt
```

## Goal-Level Decision Audit

Decision: create an externally reviewable focused component-union protocol
before any POD spend.

1. Was I foolish?

   No.

2. If yes, what actions made the decision foolish?

   It would be foolish to run POD from the fresh M37 helper without freezing
   controls, correctness, and labels-vs-signature semantics.

3. Was there another path?

   Yes. Directly run the pod. That risks spending money on an unreviewed
   harness and repeating the old measure-first failure mode.

4. Can I now try a different path that actually solves the problem?

   Yes. Review the protocol first, then implement a local harness or run a
   single focused POD only if a later 2-AI verdict authorizes it.

## Non-Authorization

This report authorizes no V3 release, no all-app POD spend, no immediate
focused POD spend, no public speedup claims, no broad V3-over-V2.x claims, no
true-zero-copy wording, no automatic partner selection, no V4 work, no C ABI
work, and no embedding work.
