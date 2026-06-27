# Codex 2-AI Consensus: Phoenix V3 Grouped-Reduction M7 Rerun Packet

Date: 2026-06-20

Status: accepted as pre-pod execution packet, not executed.

This is not V3 release authorization.

## Scope

Bounded goal:

```text
Prepare a fresh M7-designated grouped_reduction rerun packet that standardizes
the next pod run, preserves claim boundaries, and forbids backfill from old
warmup=1/2 evidence.
```

Primary packet:

```text
docs/rebuild/v3/phoenix_v3_grouped_reduction_m7_rerun_packet_2026-06-20.md
docs/rebuild/v3/phoenix_v3_grouped_reduction_m7_rerun_packet_2026-06-20.json
```

Generator and tests:

```text
scripts/v3_phoenix_grouped_reduction_m7_rerun_packet.py
tests/v3_phoenix_grouped_reduction_m7_rerun_packet_test.py
```

## External Review

External reviewer:

```text
Claude (claude-sonnet-4-6)
```

Review file:

```text
docs/reviews/claude_phoenix_v3_grouped_reduction_m7_rerun_packet_review_2026-06-20.md
```

Claude verdict:

```text
approve-with-required-fixes
P0 issues: 1
P1 issues: 3
2ai_consensus_authorized: true after P0 and P1 fixes
```

## Required Fixes Applied

P0 and P1 fixes applied before this consensus:

1. The pod-side `claim_boundary_gate` now asserts
   `whole_app_speedup_claim_authorized is False` in addition to release,
   public speedup, and pre-run M7-promotion flags.
2. The claim-boundary gate now captures stderr into
   `claim_boundary_gate.txt` with `2>&1`, so assertion failures preserve a
   traceback artifact.
3. `post_run_intake` is now a required command. It runs
   `scripts/v3_phoenix_grouped_reduction_m7_feasibility.py` with the fresh
   warmup=3 source files and emits repeat-aware JSON/Markdown intake artifacts.
4. `env_probe` now includes `scripts/v3_gpu_python_env_gate.py`,
   `scripts/v3_phoenix_grouped_reduction_m7_feasibility.py`, and
   `scripts/v3_phoenix_grouped_reduction_m7_rerun_packet.py` in
   `source_manifest.sha256`.
5. Tests now assert the added claim flag, stderr capture, post-run intake
   command, source-manifest coverage, and planned-output/measurement-command
   consistency.

## Packet Accepted

The packet is accepted only as:

```text
ready_for_external_review_not_executed
```

Accepted execution shape:

- two scales: 262,144 rows / 1,024 groups and 524,288 rows / 2,048 groups;
- two modes per scale: count and sum;
- two backends per mode: Embree and OptiX;
- standardized warmup=3 for all measured rows;
- `--include-iteration-walls` enabled for both measurement commands;
- post-run repeat-aware intake required before interpretation;
- old warmup=1/2 evidence cannot be merged or backfilled into this M7 run.

Claim state remains:

```text
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
m7_promotion_authorized_before_run: false
```

## Verification

Focused tests after P0/P1 fixes:

```text
py -3 -m unittest tests.v3_phoenix_grouped_reduction_m7_feasibility_test tests.v3_phoenix_grouped_reduction_m7_rerun_packet_test tests.v3_release_wording_gate_test
16 tests OK
```

Release wording gate:

```text
py -3 scripts/v3_release_wording_gate.py --pretty
status: pass
violations: []
release_authorized: false
public_speedup_claim_authorized: false
```

V3 rebuild matrix:

```text
py -3 scripts/run_test_matrix.py --group v3_rebuild
25 modules / 102 tests OK
```

Note: local Python still prints `Could not find platform independent libraries
<prefix>` before test output, but the commands exit 0 and the suites pass.

## Consensus Decision

Codex accepts Claude's review and the required fixes as complete.

This packet may be used as the pre-pod execution plan for the fresh
grouped_reduction M7 rerun. It does not authorize:

- V3 release;
- public speedup wording;
- whole-database speedup;
- RayDB-style end-to-end speedup;
- M7 promotion before the run;
- mixing fresh warmup=3 evidence with old warmup=1/2 rows.

## Goal-Level Decision Audit

Decision: close the grouped_reduction rerun packet as reviewed pre-pod
execution plan.

1. Was I foolish?

   No. The packet is reviewed, tested, and still refuses release and M7
   promotion.

2. If yes, what actions made the decision foolish?

   The foolish action would have been to run the pod with an incomplete
   claim-boundary gate or without a defined post-run intake. Those were fixed.

3. Was there another path?

   Yes. I could have executed the old feasibility commands directly. That
   would have reused warmup-asymmetric evidence and left the post-run intake
   undefined.

4. Can I now try a different path that actually solves the problem?

   Yes. The next path is a clean, standardized pod run followed by post-run
   repeat-aware intake and another external review before any M7 promotion.
