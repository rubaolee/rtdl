# 2-AI Consensus: Phoenix V3 M38 Component-Union Focused POD Protocol

Date: 2026-06-23

Participants:

- Codex
- Claude

## Consensus Verdict

`accept_m38_authorize_one_focused_component_union_pod_after_harness_gate`

## What Is Now Accepted

M38 is accepted as the focused same-contract component-union POD protocol for
the M37 productized prepared-execution runner path.

The accepted row is:

```text
component_union_clustered3d_262144_points_repeat5_m38_focused_probe
```

The accepted productized route is:

```text
run_radius_graph_component_union_3d_prepared_session
```

The accepted variants are:

```text
embree_same_contract_component_union_control
legacy_optix_grouped_stream_component_labels
productized_prepared_execution_runner
```

## Operational Authorization

M38 itself does not run POD.

The next allowed step is M39 local harness implementation and local gates. If
M39 implements the reviewed harness, passes local dry-run/unit tests, enforces
same generated input across all variants, confirms RT hardware, prints heartbeat
output, emits the required M37 metadata, and preserves the `2h / $0.50` hard cap,
then one focused component-union POD run is authorized by this consensus.

No all-app POD run is authorized.

## Material Success Bar

The focused run can count as a material Set-A component-union candidate only if
the productized runner:

- produces component-label outputs, not only component signatures;
- matches canonical component signatures across variants;
- sets `runtime_trunk_executes_end_to_end=true`;
- sets `component_union_phase_accounting_visible=true`;
- sets `component_label_columns_present=true`;
- sets `component_signature_pass_executed=false`;
- beats Embree same-contract control by at least `1.20x` on both hot query
  median and runner-inclusive wall;
- avoids legacy OptiX runner-inclusive wall regression below `0.98x`.

Failure to meet those bars is negative or coverage-only evidence, not release
evidence.

## Validation At Consensus Time

Focused local gate:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_m38_component_union_focused_pod_protocol_test \
  tests.v3_release_wording_gate_test
Ran 9 tests in 4.870s
OK
```

Full V3 rebuild local gate:

```text
PYTHONPATH=src;. py -3 scripts/run_test_matrix.py --group v3_rebuild
module_count: 118
Ran 614 tests in 76.082s
OK
stdout: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m38_protocol_tightening_20260623_140000.stdout.txt
stderr: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m38_protocol_tightening_20260623_140000.stderr.txt
```

Gemini and Antigravity were attempted as fallbacks. Gemini failed with
`UNSUPPORTED_CLIENT`; Antigravity failed because `ANTIGRAVITY_LS_ADDRESS` is not
set. Claude provided the usable external review.

## Non-Authorization

This consensus authorizes no V3 release, no all-app POD spend, no public
speedup wording, no broad V3-over-V2.x wording, no true-zero-copy wording, no
automatic partner selection, no V4 work, no C ABI work, and no embedding work.

## Goal-Level Decision Audit

Decision: close M38 as an accepted protocol and move next to M39 local harness
work.

1. Was I foolish?

   No.

2. If yes, what actions made the decision foolish?

   It would be foolish to skip the local harness gate and spend POD directly.
   This consensus does not do that.

3. Was there another path?

   Yes. Treat the external review as blocked because Gemini and Antigravity
   failed. Claude succeeded, so that path would waste time.

4. Can I now try a different path that actually solves the problem?

   Yes. Build the local harness and use the accepted protocol to decide whether
   a single focused POD run is worth spending.
