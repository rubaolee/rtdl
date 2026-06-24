# Phoenix V3 M41 Grouped-Reduction Free Local CUDA Smoke Runbook

Date: 2026-06-23
Status: `small_smoke_executed_not_release`

## Purpose

If external review accepts or caveats M41 with a request for a free CUDA smoke,
use local Linux `192.168.1.20` rather than paid POD. This smoke is for harness
execution sanity only. It is not RT hardware evidence, not release evidence, and
not public speedup evidence.

Executed small smoke after Claude's M41 review and P1 fixes:

`docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m41_lx1_smoke_after_hotfix_20260623_145500/`

Local Linux inventory:

```text
host: lx1
gpu: NVIDIA GeForce GTX 1070
python: 3.12.3
numpy: present
numba: present
cupy: present
rtdsl: not installed
```

Use `PYTHONPATH=src:.` after syncing the current repo subset.

## Candidate Smoke Command

Small non-serious local smoke:

```bash
PYTHONPATH=src:. python3 scripts/v3_phoenix_grouped_reduction_m41_local_harness.py \
  --output-dir docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m41_lx1_smoke_$(date +%Y%m%d_%H%M%S) \
  --variant all \
  --row-count 8192 \
  --group-count 128 \
  --seed 20260623 \
  --warmup 1 \
  --repeat 5 \
  --allow-non-serious-local-smoke
```

Serious local smoke, only if the small smoke passes and reviewer asks:

```bash
PYTHONPATH=src:. python3 scripts/v3_phoenix_grouped_reduction_m41_local_harness.py \
  --output-dir docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m41_lx1_serious_$(date +%Y%m%d_%H%M%S) \
  --variant all \
  --row-count 262144 \
  --group-count 1024 \
  --seed 20260623 \
  --warmup 1 \
  --repeat 5
```

## Guardrails

- Do not use this as RT-hardware evidence.
- Do not use this as paid-POD evidence.
- Do not use this as public speedup wording.
- Do not run all-app.
- Do not claim V3 release readiness.
- Copy artifacts back before interpreting results.

## Goal-Level Decision Audit

1. Was I foolish?

   No. Preparing a free local smoke runbook avoids paid-POD waste and does not
   execute unauthorized benchmarks.

2. If yes, what actions made the decision foolish?

   The foolish action would be running a paid POD or promoting local GTX 1070
   numbers as RT evidence before review.

3. Was there another path?

   Yes. Wait for Claude and then improvise the local smoke. That is slower and
   risks another setup mistake.

4. Can I now try a different path that actually solves the problem?

   Yes. Keep this as a ready runbook and only execute it if M41 review asks for
   a CUDA smoke before Step-2 continuation.
