# Goal2476 Same-Root Culling A/B Toggle

Date: 2026-05-21

## Scope

Goal2476 converts the Goal2475 same-root grouped-union intersection cull from a
one-way internal optimization into a controlled A/B surface. The cull remains
default-on for existing callers, but current Python and benchmark paths can
disable it explicitly to compare enabled vs disabled behavior in the same build.

This is a generic fixed-radius grouped-union engine control. No DBSCAN-specific native ABI, app vocabulary, or clustering semantics were added.

## Implementation

- Native OptiX grouped-union launch params now carry `same_root_culling`.
- Existing C ABI symbols still call the implementation with same-root culling
  enabled, preserving Goal2475 behavior for old callers.
- New `_with_options` C ABI symbols allow explicit same-root culling control
  for host-query, self-query, self-query with telemetry, and self-range grouped
  union paths.
- Python runtime methods expose `same_root_culling: bool = True` and report
  `grouped_union_same_root_culling_enabled` plus the active policy.
- The CuPy grouped-stream continuation adapter and RT-DBSCAN benchmark runner
  thread the option through to the generic grouped-union primitive.

## Pod Evidence

Pod command used: `ssh root@69.30.85.177 -p 22181 -i ~/.ssh/id_ed25519_rtdl_codex`.

Environment:

- Host: `ecdc0a16bb30`
- GPU: `NVIDIA RTX A5000, 570.211.01`
- CUDA: `/usr/local/cuda-12.8`, `Build cuda_12.8.r12.8/compiler.35583870_0`
- OptiX headers: `/root/vendor/optix-dev-8.0.0`
- Backend build: `make build-optix CUDA_PREFIX=/usr/local/cuda-12.8 OPTIX_PREFIX=/root/vendor/optix-dev-8.0.0`

The pod tree was rsynced from the current local working tree because this
implementation is not yet committed. The runner therefore records
`source_commit: null`; use the copied artifacts below as working-tree evidence,
not release evidence.

Artifacts:

- `docs/reports/goal2476_same_root_ab_on/summary.json`
- `docs/reports/goal2476_same_root_ab_off/summary.json`

Same-build A/B results, column-signature mode, `repeat_count=5`, tail excludes
the first repeat:

| Point count | Signatures | Total median on | Total median off | Total speedup | Native median on | Native median off | Native speedup |
|---:|---|---:|---:|---:|---:|---:|---:|
| 32768 | match | 0.044802s | 0.053457s | 1.193x | 0.024914s | 0.032739s | 1.314x |
| 65536 | match | 0.107093s | 0.122379s | 1.143x | 0.068098s | 0.083150s | 1.221x |

This confirms the Goal2475 same-root cull remains beneficial when measured as a
controlled same-build switch.

## External Review

Gemini reviewed the implementation/report and accepted Goal2476 with no
blocking issues in
`docs/reviews/goal2476_gemini_review_same_root_ab_toggle_2026-05-21.md`.
Its first review included an incorrect illustrative timing example, so a narrow
follow-up exact-number check was recorded in
`docs/reviews/goal2476_gemini_followup_exact_numbers_same_root_ab_toggle_2026-05-21.md`.
The follow-up verified the table above against the raw JSON artifacts and found
no blockers.

## Evidence Boundary

Local validation checks the static contract and Python syntax. Pod evidence now
checks the controlled same-build performance comparison and same-signature
correctness for the default dataset sizes.

Until that same-build pod comparison exists and is reviewed, Public performance claims remain blocked. Goal2475's earlier positive evidence remains useful
internal engineering evidence, but Goal2476 is the stronger comparison surface
for future claims because it removes build-to-build drift.

## Intended Pod Commands

```bash
PYTHONPATH=src:. python3 scripts/goal2467_grouped_stream_baseline_pod_runner.py \
  --signature-mode column \
  --repeat-count 5 \
  --output-dir docs/reports/goal2476_same_root_ab_on

PYTHONPATH=src:. python3 scripts/goal2467_grouped_stream_baseline_pod_runner.py \
  --signature-mode column \
  --repeat-count 5 \
  --disable-grouped-union-same-root-culling \
  --output-dir docs/reports/goal2476_same_root_ab_off
```

The comparison must require matching signatures before timing ratios are
interpreted.
