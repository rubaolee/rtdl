# Call For Review - Goal5110 X-HD Paper App Requirements And Provenance Scaffold

Please strictly review Goal5110:

```text
history/internal_docs/goal5110_xhd_paper_app_requirements_and_provenance_scaffold_2026-07-07.md
Paper-reproduction-apps/x-hd-paper/README.md
Paper-reproduction-apps/x-hd-paper/data/README.md
Paper-reproduction-apps/x-hd-paper/data/manifest.json
Paper-reproduction-apps/x-hd-paper/results/README.md
tests/goal5110_xhd_paper_app_scaffold_test.py
examples/current/research_benchmarks/hausdorff_xhd/
history/internal_docs/docs_reports/hausdorff_v2_rt_acceleration_attempt_2026-05-15.md
```

## Context

The owner selected X-HD as the next major paper-reproduction app. Public paper
and source code are available from the owner's homepage and GitHub.

This goal creates the scaffold only. It must not claim paper reproduction.

## Claimed Outcome

```text
xhd_paper_app_scaffold_created__author_source_pinned__existing_rtdl_assets_mapped
```

The report claims:

- X-HD paper source and author code were located.
- Author repository `pwrliang/X-HD` is pinned at commit
  `7bf41c8442d059c94f4178355c6d5a10571d9658`.
- Author entrypoint is `hd_exec`.
- `variant=rt` maps to the paper's X-HD route.
- Author JSON includes `HDResult`, `Running.AvgTime`, repeats, and per-iteration
  phase fields.
- Existing RTDL Hausdorff/X-HD-style benchmark assets are mapped but not
  reclassified as paper reproduction.
- Prior Goal2110-2143 X-HD/Hausdorff evidence is treated as historical RTDL
  asset evidence, not exact X-HD paper reproduction.
- New app scaffold exists under `Paper-reproduction-apps/x-hd-paper`.

## Review Questions

1. Are the paper and author repository provenance fields accurate?
2. Is the source commit pin sufficient for a first scaffold?
3. Does the report correctly identify the author CLI / JSON contract?
4. Does it correctly distinguish existing `hausdorff_xhd` benchmark assets from
   paper-reproduction evidence?
5. Is the first target (`bounded_same_input_author_json_gate`) the right next
   milestone?
6. Does the scaffold avoid full paper, exact dataset, and performance claims?
7. Are the manifest/README files consistent with the paper-app template?
8. Are the tests sufficient for a scaffold-level goal?
9. Is any RTDL core semantic being changed or app-specific behavior being
   smuggled into the system?
10. Is the recommended Goal5111 direction correct: build author `hd_exec` and
    create a tiny same-input comparator before touching full paper datasets?

## Expected Answer Shape

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to the 10 review questions:
```

Preferred verdict label if approved:

```text
approve_goal5110_xhd_scaffold_author_source_pinned_no_reproduction_claim
```
