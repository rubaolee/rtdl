# Goal 654: Current-Main Support Matrix

Date: 2026-04-20

Verdict: ACCEPT by Codex + Gemini Flash consensus.

## Goal

Add one public, current-main support matrix so users can distinguish:

- released `v0.9.5` tag claims;
- post-release current `main` backend improvements from Goals650-653;
- native/native-assisted any-hit support by backend;
- non-claims around speedup, Apple RT, HIPRT, AMD GPU validation, and
  `reduce_rows`.

## Files Changed

- `/Users/rl2025/rtdl_python_only/docs/current_main_support_matrix.md`
- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/current_architecture.md`
- `/Users/rl2025/rtdl_python_only/docs/backend_maturity.md`
- `/Users/rl2025/rtdl_python_only/tests/goal654_current_main_support_matrix_test.py`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal515_public_command_truth_audit_2026-04-17.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal515_public_command_truth_audit_2026-04-17.md`

The Goal515 report files changed only because README line numbers shifted after
adding the new public link; the command count and validity did not change.

## Matrix Content

The new matrix states:

- current public release is `v0.9.5`;
- current `main` adds post-release native/native-assisted any-hit work;
- backend libraries must be rebuilt before current-main native paths are
  available;
- stale backend libraries may fall back or reject missing-symbol shapes;
- the matrix is not a speedup claim.

It records current-main any-hit support:

- CPU reference: supported;
- Embree: native early-exit with `rtcOccluded1`;
- OptiX: native early-exit with `optixTerminateRay()`;
- Vulkan: native RT any-hit with `terminateRayEXT`;
- HIPRT: traversal-loop early-exit;
- Apple RT 3D: MPS RT nearest-intersection existence;
- Apple RT 2D: MPS-prism native-assisted traversal with per-ray mask
  early-exit plus exact 2D acceptance.

It also states that `visibility_rows` dispatches through any-hit, while
`reduce_rows` remains a Python helper over emitted rows.

## Honesty Boundaries

The matrix explicitly rejects:

- broad speedup across all engines;
- RT-core speedup from GTX 1070 Linux evidence;
- AMD GPU validation for HIPRT;
- HIPRT CPU fallback;
- Apple MPS ray-tracing-hardware traversal for DB or graph workloads;
- programmable shader-level Apple any-hit;
- native backend acceleration for `reduce_rows`;
- retroactive native Vulkan or Apple any-hit claims for the released `v0.9.5`
  tag.

## Verification

Commands run from `/Users/rl2025/rtdl_python_only`:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal654_current_main_support_matrix_test tests.goal646_public_front_page_doc_consistency_test tests.goal512_public_doc_smoke_audit_test -v
```

Result:

```text
Ran 10 tests in 0.010s
OK
```

```text
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py
```

Result:

```json
{"command_count": 248, "public_doc_count": 14, "valid": true}
```

```text
git diff --check
```

Result: clean.

## Review Status

Codex local verdict: ACCEPT.

Gemini Flash external verdict: ACCEPT.

- `/Users/rl2025/rtdl_python_only/docs/reports/goal654_external_review_2026-04-20.md`

Claude was also called with the same handoff request, but the CLI process
stalled without writing an additional verdict and was terminated. Goal654 is
closed under the standing 2-AI consensus rule using Codex + Gemini Flash.

External review request:

- `/Users/rl2025/rtdl_python_only/docs/handoff/GOAL654_CURRENT_MAIN_SUPPORT_MATRIX_REVIEW_REQUEST_2026-04-20.md`
