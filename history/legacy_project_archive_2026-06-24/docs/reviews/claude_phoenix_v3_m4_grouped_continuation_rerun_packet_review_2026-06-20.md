# Claude Review: Phoenix V3 M4 Grouped-Continuation Rerun Packet

Date: 2026-06-20

Scope: external review of the Phoenix V3 M4 grouped/fused-continuation rerun
packet before pod execution.

## Prompt Summary

Claude was asked to review whether the packet was ready to run on the RT
hardware pod as the next Phoenix V3 P0 step. The prompt stated that V3 is
governed by Goal4392, that C ABI / embedding / SDK packaging /
external-runtime zero-copy interop / public true-zero-copy claims are out of
V3, and that the packet is not release evidence or public speedup evidence.

## Verdict

VERDICT: ACCEPT_WITH_REQUIRED_AMENDMENTS

## Required Amendments

- Add an explicit pre-run gate check in the packet confirming
  `release_authorized=false`, `public_speedup_claim_authorized=false`, and
  `m7_qualified_rows=0` are read by the runner itself, not just declared in
  packet metadata, so config drift cannot silently flip these before the pod
  run.
- Add an explicit written rule that a failed run at the stated scale, such as
  M18 at 65,536 rays, must be recorded as a failed M4 evidence row at that
  scale, and must not be backfilled, averaged, or footnoted against the old
  8,192-ray M18 result in any downstream report.
- Confirm the artifact target path
  `/root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_m4_grouped_continuation_20260620`
  is pre-created with write permission and sufficient free space before the run
  starts, instead of discovering that as a failure mid-run.
- Add a single explicit statement in the packet header that none of
  M9/M10/M11/M18/M23/M28 results are to be cited, quoted, or paraphrased in any
  public-facing or partner-facing material until a separate, distinct
  authorization step changes `public_speedup_claim_authorized` to true.
- Require that Embree and OptiX backends in M28 are run and recorded as
  separate, independently labeled evidence rows, not merged or averaged.

## Risk Notes

- Scale is appropriate for serious internal M4 grouped-continuation evidence:
  65,536 points or rays, 1,024 groups, 524,288 points for M23, and 262,144 rows
  for M28.
- The V3 hard-out items are absent from the packet scope.
- The main residual risk was procedural: safeguards needed to be converted from
  policy statements into runner-visible checks.
- M23 copy/point count must be double-checked at runtime so recorded evidence is
  unambiguous.

## Codex Follow-Up

The required amendments were applied to:

- `docs/rebuild/v3/phoenix_v3_m4_grouped_continuation_rerun_packet_2026-06-20.json`
- `docs/rebuild/v3/phoenix_v3_m4_grouped_continuation_rerun_packet_2026-06-20.md`
- `tests/v3_phoenix_m4_grouped_continuation_packet_test.py`

