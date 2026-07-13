# Call For Review: Goal5222 Range Hood Hybrid Comparator Probe

Date: 2026-07-09

Please strictly review Goal5222:

```text
history/internal_docs/goal5222_range_hood_hybrid_comparator_probe_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5222_range_hood_comparator_regime_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5222_range_hood_paper_branch_hybrid_repeat5_probe_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5222_range_hood_paper_branch_build_and_probe_artifacts_2026-07-09.tar.gz
```

## Context

Goal5221 extended the ModelNet40 normalized-public-OFF gate to 20 selected
pairs/categories. Nineteen cases passed directly with current author `main/rt`.
One case failed:

```text
range_hood_0124.off -> range_hood_0004.off
paper log HDResult       = 0.46497631072998047
current main/rt HDResult = 0.466653436422348
RTDL normalized route    = 0.46497629417671404
```

The paper-branch log for that case reports `Algorithm=Hybrid`, while the
current rerun reports `Algorithm=XHD`.

Goal5222 builds and runs the actual `origin/paper` branch author binary with
`variant=hybrid` to decide whether the failure is RTDL error or comparator
regime mismatch.

## Review Questions

1. Does the evidence prove that the paper-branch `variant=hybrid` author binary
   reproduces the `range_hood` paper-log HDResult exactly?
2. Does the evidence show that the current `main/rt` author comparator reports
   `Algorithm=XHD` and does **not** match the same paper-log HDResult?
3. Does the RTDL normalized route for this case match the paper log and the
   paper-branch Hybrid comparator within tolerance?
4. Is the conclusion correct that Goal5221's one failing case is a
   comparator-regime mismatch rather than an RTDL route correctness failure?
5. Are the build patches correctly classified as author/toolchain
   compatibility patches rather than algorithm changes?
6. Does the report avoid claiming all ModelNet40 reproduction, exact dataset
   byte identity, author parity, or author-vs-RTDL performance ratio?
7. Is the proposed next step correct: make ModelNet40 comparator selection
   algorithm-aware (`Hybrid` logs require paper-branch Hybrid comparator)?

## Expected Answer Shape

```text
Verdict: approve / approve_with_required_amendments / reject

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Question answers:
1. ...
2. ...
...
7. ...
```

Requested verdict label if approved:

```text
approve_goal5222_range_hood_failure_is_hybrid_comparator_mismatch
```
