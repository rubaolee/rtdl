# Goal3520: v2.8 Claim-Boundary And Stale-Doc Audit

Date: 2026-06-05

Status: internal closeout audit; not release authorization.

## Purpose

Goal3520 blocks accidental overclaiming before the v2.8 internal closeout packet. It audits active learner docs, research benchmark docs, and selected example Python strings for stale version wording, unsupported release/package-install claims, broad speedup claims, true-zero-copy claims, RayJoin/paper-reproduction claims, hidden partner selection, and stray future-version notes.

## Audit Results

| Area | Scan result | Action | Residual risk |
| --- | --- | --- | --- |
| Active learner Markdown | Goal3519 had already removed stale v2.6/v2.x current wording | Added recursive Goal3520 test coverage over root/docs/learn/tutorial/research README paths and rephrased root history links from release-package wording to evidence-archive wording | Historical v2.6/v2.3 links remain only in root README history/audit section |
| Claim-boundary wording | Matches were negative boundaries such as "not a package-install promise" or "cannot claim paper reproduction" | Preserved negative boundary text; test blocks positive authorization phrases | Human reviewers still need to judge nuanced marketing text in final packet |
| Example Python CLI/docstrings | Found stale user-facing `v2.x`/`v2.5` wording in Hausdorff, RayJoin, RT-DBSCAN | Updated user-facing strings to v2.8/current wording | Compatibility helper names remain intentionally versioned |
| Versioned helper names | Found `v2_5`/`v2_6` function names, metadata keys, and protocol constants in selected benchmark Python files | Quarantined them as compatibility/protocol names and added future work item | Goal3520 does not rename APIs; later alias/migration work should decide |
| Future-version notes | Found one active future-list item using `v2.x` wording | Changed to `v2.8-or-later` and added explicit "Legacy Versioned Helper Names" section | Future ideas remain in `docs/research/future_version_to_do_list.md`, not learner docs |

## Files Modified

| File | Problem | Action |
| --- | --- | --- |
| `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_function.py` | User-facing docstrings/parser text said `v2.x` or `v2.5 default` | Updated to `v2.8` / current warmed default wording |
| `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_language_lab.py` | CLI description said `v2.x` | Updated to `v2.8` |
| `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_user_benchmark.py` | User-visible strings said `v2.x` | Updated to `v2.8` |
| `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py` | Benchmark route docstring said `v2.x` | Updated to `v2.8` |
| `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py` | CLI description said `v2.x` | Updated to `v2.8` |
| `docs/research/future_version_to_do_list.md` | Future item used broad `v2.x` wording and did not record helper-name debt | Changed wording to `v2.8-or-later` and added `Legacy Versioned Helper Names` section |
| `README.md` | Root history links used `Release Package`, which could be mistaken for current package-install/release wording | Rephrased to `Evidence Archive` while preserving historical links |
| `tests/goal3520_v2_8_claim_boundary_stale_audit_test.py` | No audit guard existed | Added recursive stale-current-doc, positive-overclaim, literal Python authorization, versioned-Python quarantine, and future-work checks |

## Quarantined Compatibility Names

The following Python files still contain `v2_5`, `v2_6`, or related historical labels. They are accepted as quarantined compatibility/protocol names for this closeout:

- `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py`
- `examples/v2_0/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py`
- `examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `examples/v2_0/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py`

These names are not taught in the active learner Markdown as the current path. They should be handled by a later alias/migration goal, not renamed casually inside the closeout audit.

## Validation

Local validation:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal3520_v2_8_claim_boundary_stale_audit_test \
  tests.goal3519_v2_8_learner_docs_cleanup_test \
  tests.goal3518_v2_8_benchmark_matrix_test

Ran 14 tests in 0.173s
OK
```

The Goal3520 test enforces:

- stale current-version terms stay out of active Markdown except root README history;
- positive overclaim authorization phrases are absent;
- Python benchmark source does not literally set critical claim-boundary flags to `True`;
- versioned Python residuals are limited to the known compatibility files;
- the future-version to-do list records the legacy helper-name migration idea.

## Verdict

`accept-with-boundary`

Goal3520 closes the stale-doc and claim-boundary audit for active v2.8 learner docs and visible benchmark strings. It does not authorize release, public speedup wording, broad RT-core wording, true-zero-copy wording, package-install claims, paper-reproduction claims, hidden partner selection, or app-specific native-engine behavior.

The remaining boundary is deliberate: legacy versioned helper names in Python source remain quarantined compatibility debt and should be addressed by a later alias/migration goal, not by this audit.
