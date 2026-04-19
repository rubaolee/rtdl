# Goal592 Public Doc Link And Freshness Audit

Date: 2026-04-19

Status: ACCEPTED with Claude + Gemini review consensus

## Scope

This goal follows Goal591 and checks the public-facing doc path after the Apple
RT Goal590 and backend-maturity updates.

Checked files:

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md`
- `/Users/rl2025/rtdl_python_only/docs/capability_boundaries.md`
- `/Users/rl2025/rtdl_python_only/docs/backend_maturity.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9/support_matrix.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_1/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_1/support_matrix.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_1/release_statement.md`

## Refresh File Update

`/Users/rl2025/refresh.md` still described `v0.8.0` as the current released
version. It was updated to the current state:

- current released version: `v0.9.1`
- current active line: post-`v0.9.1` stabilization and bounded backend expansion
- Apple RT native slices: 3D closest-hit, 3D hit-count, 2D segment-intersection
- backend maturity boundary: Embree is the only backend currently called
  optimized/mature; Apple Metal/MPS RT is correctness-validated but unoptimized
- adaptive native engine is parked and not release evidence

This file is outside the repository and is an environment-memory document, not
a release artifact.

## Link Check

Command used:

```bash
PYTHONPATH=src:. python3 - <<'PY'
from pathlib import Path
import re, json
public_docs = [
    Path('README.md'),
    Path('docs/README.md'),
    Path('docs/rtdl_feature_guide.md'),
    Path('docs/capability_boundaries.md'),
    Path('docs/backend_maturity.md'),
    Path('docs/release_facing_examples.md'),
    Path('docs/release_reports/v0_9/README.md'),
    Path('docs/release_reports/v0_9/support_matrix.md'),
    Path('docs/release_reports/v0_9_1/README.md'),
    Path('docs/release_reports/v0_9_1/support_matrix.md'),
    Path('docs/release_reports/v0_9_1/release_statement.md'),
]
link_re = re.compile(r'\\[[^\\]]+\\]\\(([^)]+)\\)')
issues = []
checked = 0
for doc in public_docs:
    text = doc.read_text()
    for match in link_re.finditer(text):
        if match.start() > 0 and text[match.start() - 1] == '!':
            continue
        target = match.group(1).split('#', 1)[0]
        if not target or re.match(r'^[a-z]+://', target) or target.startswith('mailto:'):
            continue
        checked += 1
        path = Path(target) if target.startswith('/') else (doc.parent / target).resolve()
        if not path.exists():
            line = text.count('\\n', 0, match.start()) + 1
            issues.append({'doc': str(doc), 'line': line, 'target': match.group(1), 'resolved': str(path)})
claims = {
    'root_current_v091': 'current released version is `v0.9.1`' in Path('README.md').read_text(),
    'docs_index_has_backend_maturity': 'backend_maturity.md' in Path('docs/README.md').read_text(),
    'feature_guide_has_goal590': 'Goal590' in Path('docs/rtdl_feature_guide.md').read_text(),
    'capability_has_goal590': 'Goal590' in Path('docs/capability_boundaries.md').read_text(),
    'maturity_embree_only_optimized': 'Embree is the only backend' in Path('docs/backend_maturity.md').read_text(),
    'v09_support_has_post_v091_addendum': 'Post-`v0.9.1` mainline addendum' in Path('docs/release_reports/v0_9/support_matrix.md').read_text(),
}
print(json.dumps({'checked_links': checked, 'broken_links': issues, 'claims': claims}, indent=2))
PY
```

Result:

```json
{
  "checked_links": 247,
  "broken_links": [],
  "claims": {
    "root_current_v091": true,
    "docs_index_has_backend_maturity": true,
    "feature_guide_has_goal590": true,
    "capability_has_goal590": true,
    "maturity_embree_only_optimized": true,
    "v09_support_has_post_v091_addendum": true
  }
}
```

## Findings

- No broken local Markdown links were found in the checked public-doc set.
- The root README identifies `v0.9.1` as the current released version.
- The docs index includes `backend_maturity.md` in the new-user path and live
  docs list.
- The feature guide and capability-boundary docs mention Goal590 Apple RT 2D
  segment-intersection coverage.
- The backend maturity doc explicitly limits optimized/mature backend wording to
  Embree.
- The v0.9 support matrix preserves the released `v0.9.1` scope while adding a
  labeled post-`v0.9.1` mainline addendum for Goals 582, 583, and 590.

## Verdict

No public-doc link or freshness blocker was found in this local audit.

## Review Consensus

External review artifacts:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal592_claude_review_2026-04-19.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal592_gemini_flash_review_2026-04-19.md`

Both reviews returned `ACCEPT`. They confirmed the public-facing docs honestly
reflect the `v0.9.1` release boundary, post-`v0.9.1` Apple RT mainline work,
backend maturity limits, and adaptive-engine hold state.
