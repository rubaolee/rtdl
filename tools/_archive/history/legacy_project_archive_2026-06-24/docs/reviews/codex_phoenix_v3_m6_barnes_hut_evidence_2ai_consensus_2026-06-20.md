# Codex 2-AI Consensus: Phoenix V3 M6 Barnes-Hut Evidence

Date: 2026-06-20

Status: accepted as closed internal M6 route-parity evidence.

This is not V3 release authorization.

## Scope

Bounded goal:

```text
Close the Phoenix V3 M6 aggregate-frontier/vector evidence gap, if current pod
evidence supports it, without claiming Barnes-Hut RT-core speedup or release
readiness.
```

## External Review

External reviewer:

```text
Claude (Sonnet 4.6)
```

Review file:

```text
docs/reviews/claude_phoenix_v3_m6_barnes_hut_evidence_review_2026-06-20.md
```

Claude verdict:

```text
approve-with-required-fixes
```

Claude found no P0 issues.

Required P1 fixes:

1. Mark the route-ratio table as mixed timing basis because fused Numba CUDA
   uses CUDA-event kernel time while CPU/Numba and prepared OptiX routes use
   wall-clock hot median.
2. Add an end-to-end test that runs the intake script against the current raw
   partitioned rerank JSON rather than only checking the precomputed summary.

## Fixes Applied

P1-1 fixed:

- `scripts/v3_phoenix_m6_barnes_hut_intake.py` now emits
  `timing_basis_mixed: true`.
- The intake methodology note now states that route ratios compare CUDA-event
  kernel time against wall-clock hot median and are not kernel-to-kernel
  comparisons.
- `docs/rebuild/v3/evidence/phoenix_v3_m6_barnes_hut_20260620/m6_barnes_hut_intake_summary.json`
  and `.md` were regenerated with the timing-basis note.
- `docs/rebuild/v3/phoenix_v3_m6_barnes_hut_pod_evidence_2026-06-20.md`
  now states the same mixed-timing-basis boundary under the route matrix.

P1-2 fixed:

- `tests/v3_phoenix_m6_barnes_hut_intake_test.py` now runs
  `scripts/v3_phoenix_m6_barnes_hut_intake.py` against
  `m6_barnes_hut_rerank_32768_65536_131072_partitioned_r11.json` and verifies
  the recomputed status, claim flags, and fastest route classification.

## Evidence Accepted

Primary report:

```text
docs/rebuild/v3/phoenix_v3_m6_barnes_hut_pod_evidence_2026-06-20.md
```

Artifact root:

```text
docs/rebuild/v3/evidence/phoenix_v3_m6_barnes_hut_20260620
```

Accepted facts:

- The first single-process 32,768 / 65,536 / 131,072-body attempt failed with
  CUDA out-of-memory and is preserved as evidence.
- The successful run partitioned by body count and merged the outputs.
- Intake status is `pass`.
- Overall status is `internal_m6_route_parity_evidence`.
- All release/public/RT-core speedup claim flags remain false.
- Phoenix M7-qualified release rows remain `0`.
- Fused Numba CUDA was fastest on the current 32,768 / 65,536 / 131,072 rerun.
- Prepared RTDL/OptiX+Numba was slower than the fastest route by 7.328x,
  5.120x, and 13.912x on the current rerun.
- Those ratios are mixed timing basis and internal route guidance only.

## Verification

Focused M6 tests:

```text
py -3 -m unittest tests.v3_phoenix_m6_barnes_hut_intake_test tests.v3_phoenix_m6_barnes_hut_evidence_test
7 tests OK
```

V3 rebuild matrix:

```text
py -3 scripts/run_test_matrix.py --group v3_rebuild
19 modules / 67 tests OK
```

Release wording gate:

```text
py -3 scripts/v3_release_wording_gate.py --pretty
status: pass
violations: []
release_authorized: false
public_speedup_claim_authorized: false
```

## Consensus Decision

Codex accepts Claude's review and the required fixes as complete.

M6 is closed only as:

```text
internal-route-parity closed
```

M6 is not closed as:

- public release evidence;
- M7-qualified release rows;
- Barnes-Hut RT-core speedup;
- whole N-body speedup;
- paper reproduction;
- automatic route or partner selection.

## Goal-Level Decision Audit

Decision: close Phoenix M6 as internal route-parity evidence after Claude review
and P1 fixes.

1. Was I foolish?

   The corrected closure decision is not foolish. It is evidence-based,
   reviewed, and keeps release authorization false.

2. If yes, what actions made the decision foolish?

   The earlier foolish action was the single-process run design, which let the
   historical runner retain raw payloads and hit CUDA OOM. Another foolish
   action would have been closing M6 before addressing Claude's mixed-timing
   and end-to-end-test findings.

3. Was there another path?

   Yes. Partition by body count from the start, and require raw-artifact intake
   tests before writing a closure report.

4. Can I now try a different path that actually solves the problem?

   Yes. The current path preserves the failed run, accepts only the partitioned
   route-parity evidence, records mixed timing basis, and leaves all release
   decisions to M7.
