This is a research/review task rather than a code implementation plan, so ExitPlanMode does not apply. Here is the full review directly:

---

## Verdict

**ACCEPTABLE** as focused internal RTX regression evidence that the opt-in extended 128-tile collect-k diagnostic (`RTDL_OPTIX_COLLECT_K_EXTENDED_128_TILE_DIAGNOSTIC=1`) and opt-in deferred merge-sync diagnostic (`RTDL_OPTIX_COLLECT_K_DEFER_MERGE_SYNC_DIAGNOSTIC=1`) can coexist over the collect-k test surface.

Verdict token `focused_collect_k_extended_defer_sweep_green` matches the report.

---

## Evidence Checked

**goal1631 report (MD)**
- GPU is a single named model only (`NVIDIA RTX A4500, 550.127.05, 20470 MiB`). No broad RTX/GPU generalisation present.
- Git commit pinned (`5adc806790ab09e9554e3f66c85cbf51a492db2e`).
- Both env vars listed explicitly in Scope.
- Result: `Ran 420 tests in 1.696s` / `OK present: True`.
- Claim boundary paragraph present and complete; all six prohibited categories negated.

**goal1631 transcript (TXT)**
- Confirms GPU, git commit, both env vars, module count (108), and `Ran 420 tests … OK` from test-runner output.
- Build command and nvcc invocation recorded.
- End-of-transcript JSON: `"decision": "defer_stable_promotion_keep_experimental"` is the correct disposition. `"accepted_as_gate": true` is gate acceptance only, not promotion. See Notes for one label worth watching.

**goal1631 test (Python)**
- `test_transcript_records_green_collect_k_sweep_with_both_diagnostics`: verifies git commit, GPU string, both env vars, module count, test count, and `\nOK\n`. All assertions are tight literal checks.
- `test_report_keeps_internal_claim_boundary`: verifies verdict token, test-count line, OK-status line, and all three explicit claim-boundary phrases (`"does not authorize public speedup wording"`, `"stable \`COLLECT_K_BOUNDED\` promotion"`, `"release action"`).
- Tests are read-only, no env mutation outside a properly restored try/finally. Correct evidence-gate pattern.

**goal1629 test (Python — prior guardrail)**
- Confirms source constants (`131072`, `64 tile segments`, `512 prefix blocks`) and the `RTDL_OPTIX_COLLECT_K_EXTENDED_128_TILE_DIAGNOSTIC` guard exist in native source.
- Confirms that without the diagnostic, counts > 131072 fall back to `dynamic_row_width_single_thread_fallback` — guardrail holds independently of goal1631.
- Establishes the correct prerequisite ordering: guardrail predates the sweep.

**goal1630 report (MD — prior diagnostic)**
- Extended 128-tile path is purely opt-in; default boundary remains 131072. Claim boundary is complete and consistent with goal1631's.
- `Next Work` section called for exactly the focused collect-k regression that goal1631 provides — prerequisite chain is closed.
- Workspace-growth-is-not-dynamic-reclamation caveat is documented; goal1631 inherits this scope constraint.

---

## Blockers

None.

---

## Notes

1. **`"accepted_reduced_copy_benchmark_evidence"` label in transcript JSON.** This string appears only in the raw transcript, not in the report or claim boundary. It most likely refers to goal1630's reduced merge-sync time delta, not a copy-optimisation claim. It carries no risk within this package, but the label must not be extracted and cited as copy-optimisation or zero-copy evidence in any summary, release note, or public document.

2. **Single-GPU scope.** All evidence is from one A4500 unit. Appropriate for an internal diagnostic sweep; must not be generalised to other RTX models or GPU families without separate evidence runs.

3. **Coexistence evidence, not interaction characterisation.** Goal1631 demonstrates that both diagnostics can be active together without collect-k test regression. It does not characterise whether enabling the 128-tile path affects defer-merge-sync timing at 262144 candidates. That is correctly out of scope and left to future work.
