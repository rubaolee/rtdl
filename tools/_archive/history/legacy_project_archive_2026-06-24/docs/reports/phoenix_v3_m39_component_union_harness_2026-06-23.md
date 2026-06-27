# Phoenix V3 M39 Component-Union Harness Report

Date: 2026-06-23

Status: `m39_harness_accepted_one_focused_pod_authorized_not_run_yet`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
focused_pod_spend_authorized_now: false
all_app_pod_spend_authorized: false
true_zero_copy_claim_authorized: false
external_embedding_or_zero_copy_claim_authorized: false
```

## Purpose

M39 implements the local harness required by the accepted M38 protocol. It does
not run POD and does not provide performance evidence.

Harness:

- `scripts/v3_phoenix_component_union_m38_pod_ab.py`

Local gate:

- `tests/v3_phoenix_m39_component_union_harness_test.py`

Source consensus:

- `docs/reviews/codex_claude_phoenix_v3_m38_component_union_focused_pod_protocol_2ai_consensus_2026-06-23.md`

## What The Harness Does

By default, the harness runs `--variant all` so the same in-process generated
point set is shared by:

```text
embree_same_contract_component_union_control
legacy_optix_grouped_stream_component_labels
productized_prepared_execution_runner
```

The Embree control uses prepared Embree fixed-radius count-threshold rows plus
generic Numba component-label continuation. It does not substitute a
component-signature-only path for labels.

The legacy OptiX control uses the existing grouped-stream component-label route.

The productized route uses:

```text
run_radius_graph_component_union_3d_prepared_session
```

## Required Gates Implemented

- serious scale floor: `point_count >= 262144` unless explicit local-smoke
  override is passed;
- `repeat >= 5`;
- `min_neighbors >= 1`;
- same generated point set for default all-variant runs;
- component-label contract fields for all variants;
- component-signature shortcut fails closed;
- productized runner metadata gates for runtime execution, component-label
  columns, component-union phase accounting, and no component-signature pass;
- heartbeat output;
- process-level hard-cap watchdog exits with code `124`;
- no release, public speedup, all-app, V4, C ABI, embedding, or true-zero-copy
  authorization.

## Local Validation

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_m39_component_union_harness_test \
  tests.v3_release_wording_gate_test
Ran 8 tests in 4.400s
OK

PYTHONPATH=src;. py -3 scripts/v3_phoenix_component_union_m38_pod_ab.py --dry-run --output-dir build\m39_component_union_dry_run_latest
status: component_union_m39_harness_ready_not_pod_run
failed_check_count: 0
```

Focused combined gate:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_m38_component_union_focused_pod_protocol_test \
  tests.v3_phoenix_m39_component_union_harness_test \
  tests.v3_release_wording_gate_test
Ran 14 tests in 4.704s
OK
```

Full `v3_rebuild` gate:

```text
PYTHONPATH=src;. py -3 scripts/run_test_matrix.py --group v3_rebuild
module_count: 119
Ran 619 tests in 75.572s
OK
stdout: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m39_samples_cleanup_20260623_141900.stdout.txt
stderr: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m39_samples_cleanup_20260623_141900.stderr.txt
```

## Known Risk Before POD

The reviewed M38 row uses `radius=3.0` on the `clustered3d` generator. In the
current app coordinate space, that can create a very dense all-neighbor row.
The harness therefore preserves the reviewed parameters but enforces heartbeat
and a hard cap. If the focused POD times out or fails the cap, the result must
be treated as negative or blocked evidence, not massaged into a speed claim.

## Next Review Question

Does M39 satisfy the M38 harness gate strongly enough that the one focused POD
allowed by M38 consensus may be run, with no all-app run and no release claim?

## External Review

Claude returned:

```text
accept_m39_authorize_one_focused_component_union_pod
```

Recorded review:

- `docs/reviews/claude_phoenix_v3_m39_component_union_harness_recorded_review_2026-06-23.md`

Codex+Claude consensus:

- `docs/reviews/codex_claude_phoenix_v3_m39_component_union_harness_2ai_consensus_2026-06-23.md`

Interpretation: one focused component-union POD run is authorized, using
`--variant all --require-rt-hardware`. This still authorizes no release, no
all-app POD, and no public speedup wording.

## Goal-Level Decision Audit

Decision: implement a reviewed local harness instead of spending POD directly.

1. Was I foolish?

   No.

2. If yes, what actions made the decision foolish?

   It would be foolish to run paid POD without local proof that the three
   variants share the same row, use labels, emit metadata, and fail closed.

3. Was there another path?

   Yes. Run the productized helper directly on the pod. That would again risk
   measuring a route without same-contract controls.

4. Can I now try a different path that actually solves the problem?

   Yes. Finish local validation, obtain external review of the harness, then
   run exactly one focused POD if the review accepts the harness gate.

## Non-Authorization

This report authorizes no V3 release, no all-app POD, no immediate focused POD,
no public speedup wording, no broad V3-over-V2 wording, no true-zero-copy
wording, no automatic partner selection, no V4 work, no C ABI work, and no
embedding work.
