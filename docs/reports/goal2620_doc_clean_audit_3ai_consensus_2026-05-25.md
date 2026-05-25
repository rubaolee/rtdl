# Goal2620 v2.3 Documentation Cleanliness 3-AI Consensus

Date: 2026-05-25

## Verdict

ACCEPT.

The current public documentation surface is consistent with the v2.3/v2.x release
boundary, current public local links are clean, and the current public runnable
surface under `examples/v2_0` and `examples/visual_demo` passed pod smoke
validation.

This report does not duplicate the full per-file ledger because the generated
audit report already contains the required row for each Markdown file. The
canonical per-file state/action/verification ledger is:

- `docs/reports/goal2617_doc_audit_current_surface_2026-05-25.md`
- `docs/reports/goal2617_doc_audit_current_surface_2026-05-25.json`

Each row in that ledger records: file path, classification category, state,
stale-version hits, dead local links, and review or modification action.

## Scope And Classification

Current public docs are the only docs that must be learner-facing, release-current,
and free of stale release wording. Historical and support artifacts are preserved
for provenance, but are not first-run user documentation.

Current public scope:

- `README.md`
- current top-level `docs/*.md` pages selected by the audit script
- `docs/features/`
- `docs/learn/`
- `docs/rtdl/`
- `docs/tutorials/`
- `docs/release_reports/v2_3/`
- `examples/README.md`
- `examples/v2_0/`
- `examples/visual_demo/`

Historical/support scope:

- `docs/audit/`
- `docs/directives/`
- `docs/engineering/`
- `docs/handoff/`
- `docs/history/`
- `docs/reports/`
- `docs/reviews/`
- older `docs/release_reports/` packages
- generated, internal, legacy, or backend-proof example artifacts

The directory name `examples/v2_0` remains a stable path name, not a current
release claim. Current release wording is v2.3/v2.x.

## Documentation Audit Evidence

Audit command:

```bash
PYTHONPATH=src:. python3 scripts/goal2617_current_surface_audit.py \
  --json docs/reports/goal2617_doc_audit_current_surface_2026-05-25.json \
  --markdown docs/reports/goal2617_doc_audit_current_surface_2026-05-25.md
```

Audit result:

- Total Markdown files classified: 7,038
- Current public Markdown files: 72
- Current public files needing fixes: 0
- Current public stale-version hits: 0
- Current public dead local links: 0
- Non-current files with local link debt: 103

The 103 local-link debt files are historical/support artifacts only. They were
classified rather than rewritten so old audit trails do not masquerade as current
learner documentation.

Additional stale wording checks used during this goal:

```bash
rg -n 'v[0-1]\.\d|v2\.0|v2\.1|v1_|v0_' \
  README.md docs/*.md docs/learn docs/tutorials docs/features docs/rtdl \
  docs/release_reports/v2_3 examples/README.md examples/v2_0 --glob '*.md'

rg -n 'v[0-1]\.\d|v2\.0|v2\.1' \
  examples/v2_0 examples/visual_demo -g '*.py'
```

Both checks returned no current-surface matches.

Current public external-link check:

```bash
curl -L -I --max-time 20 https://www.youtube.com/watch?v=d3yJB7AmCLM
curl -L -I --max-time 20 https://youtu.be/d3yJB7AmCLM
```

Result: both current public external URL forms returned HTTP 200 on 2026-05-25.

## Runnable Surface Evidence

Pod requested by user:

```bash
ssh root@213.173.105.18 -p 44410 -i ~/.ssh/id_ed25519
```

Actual local key used:

```bash
~/.ssh/id_ed25519_rtdl_codex
```

Reason: `~/.ssh/id_ed25519` was not present on this Mac, while the RTDL working
key was present and authenticated successfully.

Pod evidence:

- Pod host observed: `93c7b71a51af`
- Python: 3.12.3
- GPU/driver observed: NVIDIA L4, driver 570.195.03
- Pod workspace: `/workspace/rtdl_goal2617_smoke`
- System prerequisites installed: `libgeos-dev`, `pkg-config`, `libembree-dev`
- Python prerequisites installed in venv: `numpy`, `pillow`, `imageio`,
  `imageio-ffmpeg`

Smoke command:

```bash
PYTHONPATH=src:. RTDL_EMBREE_PREFIX=/usr \
  .venv/bin/python scripts/goal2617_surface_smoke.py \
  --json docs/reports/goal2617_pod_surface_smoke_2026-05-25.json \
  --markdown docs/reports/goal2617_pod_surface_smoke_2026-05-25.md
```

Smoke result:

- Total current public Python cases: 54
- Passed: 54
- Failed: 0
- Missing manifest entries: 0
- Coverage kinds: tutorials, examples, apps, partners, benchmarks, learner app,
  and visual demos

The smoke is a runnable-surface gate, not a performance benchmark. Most cases
use portable CPU reference paths; `partner_anyhit` also verifies the Embree
native prerequisite path.

## 3-AI Review

Codex review: ACCEPT.

- Verified the generated per-file audit, current-surface stale wording scans,
  pod smoke result, and local regression tests.
- Agrees that historical/support link debt is acceptable only because those
  files are classified outside the first-run public docs.

Claude review: ACCEPT.

- Report: `docs/reports/goal2618_claude_doc_clean_audit_review_2026-05-25.md`
- Main findings: 72/72 current public Markdown files are clean, historical
  classification is acceptable, 54/54 pod smoke cases pass, and no blocking
  fixes remain.
- Residual risks: external links are not automatically checked, historical dead
  links remain by design, and the smoke gate is not yet wired into CI.

Gemini review: ACCEPT.

- Report: `docs/reports/goal2619_gemini_doc_clean_audit_review_2026-05-25.md`
- Main findings: public docs are sanitized for v2.3/v2.x, current public local
  links are clean, 54/54 public Python entrypoints pass, and the new regression
  test enforces the audit outcomes.
- Note: Gemini initially hit model-capacity 429 retries. The saved report keeps
  those failures for audit honesty and ends with an explicit ACCEPT verdict.

## Regression Tests

Local commands:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2617_doc_clean_audit_test \
  tests.goal2344_v2_1_internal_closure_test \
  tests.goal2613_v2_3_app_portfolio_release_test

git diff --check
```

Result:

- 11 unittest checks passed.
- `git diff --check` passed.

## Residual Risks

- External HTTP/HTTPS links are not checked by the generated local Markdown
  audit. The two current public YouTube URL forms were checked manually and
  returned HTTP 200 on 2026-05-25, but this remains point-in-time evidence.
- Historical and support artifacts still contain some dead local links. That is
  acceptable only because those files are classified non-current and not linked
  as the first-run user path.
- The pod smoke is point-in-time evidence. It should be promoted into CI or a
  repeatable release runbook if we want continuous enforcement.

## Closeout Decision

Goal2620 closes with 3-AI consensus. No release-blocking documentation or
runnable-surface issues remain for the v2.3 internal release cleanup.
