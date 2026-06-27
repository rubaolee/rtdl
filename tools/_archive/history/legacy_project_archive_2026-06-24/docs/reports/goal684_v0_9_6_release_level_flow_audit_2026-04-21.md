# Goal684: v0.9.6 Release-Level Flow Audit

Date: 2026-04-21

Status: accepted by 3-AI release-level flow consensus.

## Scope

This audit checks whether the `v0.9.6` release can proceed after the public
docs were refreshed from "candidate" wording to the current released
prepared/prepacked repeated visibility/count boundary.

The audited release surface is:

- `v0.9.5` any-hit, visibility-row, and `reduce_rows` surface retained;
- Vulkan native early-exit any-hit after backend rebuild;
- Apple RT 3D MPS RT any-hit and Apple RT 2D MPS-prism native-assisted any-hit
  after backend rebuild;
- Apple RT prepared/prepacked scalar 2D visibility-count app path;
- OptiX prepared/prepacked scalar 2D any-hit count path;
- HIPRT prepared 2D any-hit reuse on the HIPRT/Orochi CUDA path;
- Vulkan prepared 2D any-hit plus packed-ray support;
- public docs, tutorials, examples, feature guide, support matrix, release
  package, and history records updated to the `v0.9.6` boundary.

## Public Documentation Audit

Updated public-facing documents:

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/current_main_support_matrix.md`
- `/Users/rl2025/rtdl_python_only/docs/quick_tutorial.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/examples/README.md`
- `/Users/rl2025/rtdl_python_only/docs/features/README.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/README.md`
- `/Users/rl2025/rtdl_python_only/docs/backend_maturity.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_6/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_6/release_statement.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_6/support_matrix.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_6/audit_report.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_6/tag_preparation.md`

Required public-doc facts now present:

- current released version is `v0.9.6`;
- `v0.9.5` remains visible as the previous any-hit / visibility-row /
  `reduce_rows` release;
- `v0.9.6` is scoped to prepared/prepacked repeated visibility/count
  optimization and native/native-assisted any-hit backend completion;
- scalar/compact-output contracts are distinguished from full emitted-row
  output;
- DB, graph, one-shot, broad speedup, AMD GPU HIPRT, GTX 1070 RT-core, and
  Apple MPS RT DB/graph claims are explicitly rejected.

## Multi-AI Flow Audit

No release-relevant goal in the `v0.9.6` chain is single-developer-only. The
minimum release policy is at least two AI reviewers for each goal class, with
three-AI consensus for important planning, closure, and release gates.

| Goal group | Main deliverable | Evidence | AI coverage | Flow verdict |
| --- | --- | --- | --- | --- |
| Goals650-652 | Vulkan native any-hit, Apple RT 3D any-hit, Apple RT 2D native-assisted any-hit | implementation reports, focused tests, history round | Codex + Gemini Flash; Apple goals also received Claude/Gemini review where available | accepted; not single-developer-only |
| Goal653 | Linux native any-hit validation | fresh Linux backend build/probe/test record | Codex + Gemini Flash; Claude stalled without verdict and was not counted | accepted by 2 AI; no false 3-AI claim |
| Goals654-657 | current-main support matrix, tutorial/example refresh, full local gate, history catch-up | public matrix/tests/history docs | Codex + Gemini Flash; Claude unavailable/stalled and not counted | accepted by 2 AI; no single-developer-only action |
| Goals658-667 | Apple RT performance/profile/prepacked visibility-count closure | Apple RT reports, source restoration, full local suite, public docs | Codex + Claude + Gemini Flash for closure/consensus stages | accepted by 3 AI |
| Goal669 | cross-engine performance lessons | optimization lessons report | Codex + Claude + Gemini Flash | accepted by 3 AI |
| Goal670 | OptiX/HIPRT/Vulkan optimization plan split | engine-specific review plan and handoffs | Codex + Claude + Gemini Flash | accepted by 3 AI |
| Goals671-673 | OptiX prepared/prepacked 2D any-hit/count optimization | implementation, Linux evidence, cleanup reports | Codex + Claude + Gemini Flash | accepted by 3 AI |
| Goal674 | HIPRT prepared 2D any-hit reuse | implementation and focused Linux validation | Codex + Claude + Gemini Flash | accepted by 3 AI |
| Goal675 | Vulkan prepared 2D any-hit + packed rays | implementation, Linux evidence, doc boundaries | Codex + Gemini Flash, with Claude unavailable/not counted | accepted by 2 AI; no single-developer-only action |
| Goals676-677 | cross-engine closure and public doc refresh | release-facing docs and closure report | Codex + Claude + Gemini Flash | accepted by 3 AI |
| Goals678-679 | local total gate and Linux backend gate | full local suite, public command truth audit, Linux backend gate | Codex + Claude + Gemini Flash | accepted by 3 AI |
| Goal680 | history catch-up and stale DB repair | history revisions/db/dashboard/tests | Codex + Claude + Gemini Flash | accepted by 3 AI |
| Goal681 | post-history release gate | full local gate and public docs tests | Codex + Claude + Gemini Flash | accepted by 3 AI |
| Goal682 | v0.9.6 release-candidate package | release package and package test | Codex + Claude + Gemini Flash | accepted by 3 AI |
| Goal683 | final local candidate gate | `1271` tests OK, public audits, consensus report | Codex + Claude + Gemini Flash | accepted by 3 AI |
| Goal684 | final public-doc release conversion and flow audit | this report, updated docs/tests, Claude review, Gemini Flash review | Codex + Claude + Gemini Flash | accepted by 3 AI |

## Test Evidence Entering This Audit

Most recent full release gate after public release conversion:

- `PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py' -v`
- result: `1274` tests OK, `187` skips
- public command truth audit: valid, `250` commands across `14` docs
- public entry smoke: valid
- `git diff --check`: clean

External review after this audit:

- Claude external review: ACCEPT in `/Users/rl2025/rtdl_python_only/docs/reports/goal684_external_review_claude_2026-04-21.md`;
- Gemini Flash external review: ACCEPT in `/Users/rl2025/rtdl_python_only/docs/reports/goal684_external_review_gemini_flash_2026-04-21.md`;
- consensus record: `/Users/rl2025/rtdl_python_only/docs/reports/goal684_consensus_2026-04-21.md`.

## Release Non-Claims

The release must not claim:

- broad DB, graph, full-row, or one-shot speedup;
- Apple RT full emitted-row performance win from the scalar count path;
- Apple MPS ray-tracing traversal for DB or graph workloads;
- AMD GPU validation for HIPRT;
- HIPRT CPU fallback;
- RT-core acceleration from GTX 1070 evidence;
- native backend acceleration for `reduce_rows`;
- any goal as consensus-backed when only one AI actually reviewed it.

## Codex Verdict

Codex verdict: ACCEPT.

The flow is release-eligible because the release-relevant implementation,
documentation, testing, history, and gate goals have at least two-AI review
coverage, and the major release gates have three-AI consensus. The final public
documentation conversion and flow audit also received 3-AI release-level
consensus from Codex, Claude, and Gemini Flash.
