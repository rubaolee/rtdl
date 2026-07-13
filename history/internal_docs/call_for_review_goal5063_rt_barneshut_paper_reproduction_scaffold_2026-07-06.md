# Call For Review: Goal5063 RT-BarnesHut Paper-Reproduction Scaffold

Date: 2026-07-06

## Review Target

Please review:

- `history/internal_docs/goal5063_rt_barneshut_paper_reproduction_requirements_and_plan_2026-07-06.md`
- `Paper-reproduction-apps/rt-barneshut-paper/README.md`
- `Paper-reproduction-apps/rt-barneshut-paper/data/manifest.json`
- `Paper-reproduction-apps/rt-barneshut-paper/rt_barneshut_reproduction.py`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/apply_author_official_patch.py`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/check_pod_environment.sh`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/setup_author_official.sh`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_author_same_input.sh`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/compare_force_outputs.py`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_author_source_contract_gate.py`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_author_source_contract_gate.sh`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_author_comparator_gate.sh`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_author_contract_rtdl_cuda_gate.sh`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_same_input_rtdl_comparison_gate.sh`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_same_input_performance_gate.py`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_same_input_performance_gate.sh`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_local_contract_gate.py`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_local_contract_gate.sh`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_phase_boundary_review_gate.py`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_phase_boundary_review_gate.sh`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_full_pod_reproduction_gate.py`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_full_pod_reproduction_gate.sh`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_remote_full_pod_gate.py`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_completion_audit.py`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_completion_audit.sh`
- `Paper-reproduction-apps/rt-barneshut-paper/author_contract_reference.py`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/compare_author_contract_to_rtdl_reference.py`
- `scripts/goal2547_barnes_hut_3d_scalar_subtree_kernel.py`
- `tests/goal5063_rt_barneshut_paper_reproduction_scaffold_test.py`

## Requested Verdict

Use one of:

- `approve_rt_barneshut_paper_reproduction_scaffold`
- `approve_with_required_amendments`
- `block_due_to_false_reproduction_or_boundary_leak`

## Questions

1. Does the packet correctly separate existing Barnes-Hut benchmark evidence
   from a true RT-BarnesHut paper-reproduction app?
2. Does the new `Paper-reproduction-apps/rt-barneshut-paper/` user-facing
   directory avoid claiming completed paper reproduction?
3. Are the author artifact repository, branch, commit, sample path, and build
   workarounds accurately captured from prior evidence?
4. Does `apply_author_official_patch.py` correctly limit its author-source
   edits to build/device/body-count control plus `RTBH_FORCE_OUT` comparator
   observation?
5. Is the `NUM_POINTS` patch safe now that it targets the active
   `constexpr int NUM_POINTS` line rather than commented historical values?
6. Does the design correctly identify the same-input author comparator as the
   main open blocker?
7. Does the plan preserve the system/app boundary: RTDL generic machinery,
   Barnes-Hut force/opening/output logic in the app?
8. Is it acceptable that the current `rtdl-3d-diagnostic` entry point delegates
   to the historical RTDL diagnostic script while explicitly marking the result
   as non-reproduction?
9. Are the next POD steps sufficient: build author artifact, run author `new`
   with force dump, run author `treelogy` on the generated same input with
   force dump, compare the two author force files, then compare RTDL on the
   same input?
10. Does the RTDL `--force-out` addition provide the right comparison artifact
    while still making clear that current RTDL output is diagnostic rather than
    author-contract reproduction?
11. Is the Python author-contract reference correctly scoped as a debugging
    reference, not a replacement for the patched author binary comparator?
12. Does the same-input RTDL comparison gate correctly account for the author's
    post-sort force-output order by generating an author-sorted RTDL input?
13. Do the local probes justify the current diagnosis: one-bucket force law and
    index alignment are fixed, while multi-bucket cases still expose a
    tree/traversal contract gap under the historical RTDL diagnostic tree?
14. Should this line proceed to a POD author-comparator goal, or is more local
   cleanup required first?
15. Is the new `author-prepared-arrays` local route correctly scoped as
    app-layer author-contract preparation over generic flattened aggregate
    arrays, rather than a Barnes-Hut-specific RTDL core primitive?
16. Does the same-input POD gate now correctly route RTDL through the
    author-prepared aggregate arrays with `--traversal-policy author-opening`,
    instead of falling back to the historical RTDL diagnostic tree contract?
17. Is the new `run_author_contract_rtdl_cuda_gate.sh` a useful and correctly
    bounded POD diagnostic gate before the patched author binary comparator,
    while still avoiding any claim that the Python reference replaces the
    author binary paper comparator?
18. Is the new `check_pod_environment.sh` preflight useful and properly scoped,
    with separate readiness flags for author build and RTDL CUDA diagnostic
    execution?
19. Does the full POD gate runner sequence the preflight, RTDL author-contract
    CUDA gate, patched-author same-input gate, and author-vs-RTDL same-input
    gate without hiding failures or claiming completed paper reproduction?
20. Is the `setup_author_official.sh` forced checkout/reset acceptable because
    it is limited to the ignored generated author checkout under `_work/` and
    makes the compatibility patch step repeatable?
21. Does the same-input performance gate correctly summarize author and RTDL
    timing fields only after correctness gates close, while keeping the ratio
    scoped to a narrow force-kernel phase boundary and requiring human
    phase-boundary review before any performance claim?
22. Does the completion audit correctly require every completion requirement
    to be complete before setting `paper_reproduction_complete=true`, rather
    than treating scaffold tests or partial gates as enough?
23. Does `run_local_contract_gate` correctly formalize the three local probes:
    one-bucket current diagnostic match, multi-bucket current diagnostic gap,
    and multi-bucket author-prepared aggregate-array match, while keeping the
    patched author binary POD comparator as the required paper comparator?
24. Does the full POD gate correctly run `local_contract_gate` first and require
    it before the RTDL CUDA author-contract gate?
25. Does `run_phase_boundary_review_gate` prevent a false performance closeout
    by checking that the human review artifact is bound to the same performance
    summary path, accepted phase labels, and ratio?
26. Does the completion audit correctly require the phase-boundary review gate
    summary, rather than trusting raw review booleans alone?
27. Does `run_author_source_contract_gate` correctly audit the pinned raw author
    checkout for the source anchors assumed by the app, including raw
    `NUM_POINTS`, `NUM_STEPS`, `new`/`treelogy` input format, z-order sort,
    post-sort `idX`, bucket grouping, opening rule, force-law constants, and
    absence of the `RTBH_FORCE_OUT` comparator patch?
28. Does the full POD gate correctly require the author-source contract gate
    before the RTDL CUDA author-contract gate, without treating source audit
    success as a completed author-binary comparator?
29. Does `run_remote_full_pod_gate.py` correctly support POD execution from a
    local control machine by uploading only the minimal current source package,
    excluding generated `_work`/`_runs`/`_data` evidence, running the full POD
    gate remotely, and pulling the remote `_runs` evidence back?
30. Does the remote runner's `--package-only` mode provide a useful no-POD
    local gate by verifying required roots, excluded generated directories, and
    `safe_to_upload` before the next live POD attempt?

## Expected Answer Format

Please include:

```text
verdict_label:
pass/fail/required_amendments:
blocking_findings:
non_blocking_notes:
```
