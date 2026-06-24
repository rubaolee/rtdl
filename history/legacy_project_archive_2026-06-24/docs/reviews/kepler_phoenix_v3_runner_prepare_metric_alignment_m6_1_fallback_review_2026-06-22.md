# Kepler Fallback Review: Phoenix V3 Runner Prepare Metric Alignment M6.1

Date: 2026-06-22
Status: `fallback_review_not_external_not_release`

## Verdict

`accept_for_focused_hausdorff_m5_pod_no_regression_validation`

## Review Summary

Kepler accepted M6.1 as fair metric alignment, not runner-cost hiding.

Accepted facts:

- the shared runner records native prepare separately from outer prepare/cache;
- Hausdorff exposes both the aligned phase metric and runner outer metrics;
- the pod harness still gates wrapper wall independently at `0.98x`, so
  end-to-end runner tax remains visible and can still fail the run.

Local checks accepted:

- `py_compile`;
- focused 36-test suite;
- broader 56-test runner/wording suite.

## Authorized Non-Release POD Work

One focused Hausdorff M5 pod rerun is justified.

Success criteria:

- runner-vs-legacy phase-total >= `0.98x`;
- runner-vs-legacy wrapper wall >= `0.98x`;
- existing metadata/oracle/no-host-row boundaries remain clean.

Classification rules:

- If both phase-total and wrapper wall pass, record focused no-regression
  validation. This still does not by itself authorize V3 release or all-app.
- If phase-total passes but wrapper wall fails, classify as metric alignment
  plus remaining wrapper overhead, not a material Set-A win.
- If phase-total still fails, stop and do query-path work before any more
  Hausdorff POD time.

## Non-Authorization

This review does not authorize:

- V3 release.
- all-app pod rerun.
- public speedup wording.
- broad V3-over-V2 wording.
- true-zero-copy wording.
- V4 / external-buffer wording.

## Goal-Level Decision Audit

Decision: run exactly one focused Hausdorff M5 POD no-regression canary after
M6.1.

1. Was I foolish?

   No for this decision. The fallback reviewer accepted that the metric
   alignment is fair and kept wrapper wall as an independent cost gate.

2. If yes, what actions made the decision foolish?

   Not applicable. The foolish action would be using aligned phase-total alone
   to hide runner wrapper cost.

3. Was there another path that would have avoided getting stuck?

   Yes. If the canary fails phase-total, stop and work on the query path rather
   than repeating the run.

4. Can I now try a different path that actually solves the problem?

   Yes. The focused POD run tests whether the productized runner can match the
   legacy prepared OptiX front door under fair timing scope while preserving
   full wrapper-wall accountability.
