# Call For Review: Goal4886 RayJoin Numba Partner Acceleration

Please review:

```text
history/internal_docs/goal4886_rayjoin_numba_partner_acceleration_goal_2026-07-03.md
history/internal_docs/goal4886_rayjoin_numba_partner_acceleration_report_2026-07-03.md
history/internal_docs/goal4886_rayjoin_numba_overlay_kernels.py
history/internal_docs/goal4886_section57_public_primitives_overlay_numba_harness.py
history/internal_docs/goal4886_numba_synthetic_parity_summary.json
history/internal_docs/goal4886_numba_synthetic_parity_linux_summary.json
history/internal_docs/goal4886_pod_numba_synthetic_parity.json
history/internal_docs/goal4886_pod_current_au_repeat_summary.json
history/internal_docs/goal4886_pod_numba_au_cold_summary.json
history/internal_docs/goal4886_pod_numba_au_warm_summary.json
history/internal_docs/goal4886_pod_numba_synthetic_parity_skip.json
history/internal_docs/goal4886_pod_numba_au_skip_summary.json
history/internal_docs/goal4886_pod_numba_au_skip_repeat_summary.json
history/internal_docs/goal4886_pod_numba_synthetic_parity_skip_v2.json
history/internal_docs/goal4886_pod_numba_au_skip_v2_summary.json
history/internal_docs/goal4886_authorofficial_wall_attempt_invalid_summary.json
history/internal_docs/goal4886_authorofficial_wall_attempt_freshser_cwd_invalid_summary.json
```

## Requested Verdict

Preferred labels:

- `approve_goal4886_numba_writer_skip_speedup_bounded_australia`
- `approve_with_required_amendments`
- `block_until_numba_boundary_or_correctness_fixed`

## Review Questions

1. Does Goal4886 correctly preserve the current RayJoin correctness/comparator
   boundary?
2. Does it avoid modifying RTDL core or native code?
3. Are the chosen first Numba targets valid app-layer continuation targets
   rather than attempts to replace RTDL LSI/PIP primitives?
4. Do the synthetic parity tests prove the initial kernels preserve Python
   reference semantics?
5. Is the Numba-enabled harness appropriately conservative by wrapping the
   proven Goal4880 harness instead of rewriting the whole reproduction route?
6. Is the POD Australia full-harness evidence sufficient to prove that the
   Numba-enabled wrapper preserves Section 5.7 byte-equality?
7. Is the performance interpretation honest:
   - midpoint/dedupe-only Numba did **not** win (`121.647s` vs current
     `117.258s`);
   - writer-skip Numba did win (`100.531s` repeat vs current `117.258s`);
   - the bounded overall speedup is `1.166x` on the Australia representative
     input, not a broad RayJoin claim;
   - the later explicit skip-decision run is clearer but slightly slower
     (`103.786s`, `1.130x` overall, `8.10x` writer-phase), and should be read
     as the better-specified implementation evidence rather than a new broad
     claim?
8. Is the writer skip-plan semantically valid: it skips only no-intersection
   chains whose terminal-face keep rule would drop them under the current writer
   semantics, and the full output remains byte-equal?
9. Is `skipped_no_xsect_chains=399419` and
   `skipped_no_xsect_points=14996199` sufficient evidence that the Numba partner
   moved real app-layer work rather than only wrapping a tiny helper?
10. Is the AuthorOfficial comparison properly bounded:
   - final comparator phase timings may be cited;
   - older non-final `AUTHOR_WALL_SEC=146` must not be promoted;
   - Goal4886's two wall-time reruns must not be promoted because neither
     reproduced the final comparator SHA?
11. Should this phase close as:

```text
completed_numba_partner_writer_skip_speedup__byte_equal__bounded_australia_representative
```

or does it require another repeat / narrower regression before closure?

## Non-Authorization

This review does not authorize:

- broad RayJoin speedup claims;
- any Goal4886 speedup claim beyond the Australia representative Section 5.7
  public-primitives route;
- full hidden-input all-eight reproduction claims;
- Numba as correctness-critical for prior 5.2/5.3/5.7 evidence;
- changes to `src/rtdsl/**` or `src/native/**`;
- using local GTX 1070 runs as RT-core performance evidence;
- treating AuthorOfficial phase timings as a final wall-time speedup denominator.
- treating invalid AuthorOfficial wall attempts as comparator baselines.
