# 2-AI Consensus: Phoenix V3 M39 Component-Union Harness

Date: 2026-06-23

Participants:

- Codex
- Claude

## Consensus Verdict

`accept_m39_authorize_one_focused_component_union_pod`

## What Is Authorized

Exactly one focused Phoenix V3 component-union POD run is authorized, using the
M39 harness:

```bash
PYTHONPATH=src:. python scripts/v3_phoenix_component_union_m38_pod_ab.py \
  --output-dir docs/rebuild/v3/evidence/phoenix_v3_component_union_m39_focused_pod_ab_$(date +%Y%m%d_%H%M%S) \
  --variant all \
  --dataset clustered3d \
  --point-count 262144 \
  --radius 3.0 \
  --min-neighbors 4 \
  --seed 20260623 \
  --warmup 1 \
  --repeat 5 \
  --heartbeat-sec 30 \
  --hard-cap-sec 7200 \
  --require-rt-hardware
```

## What Is Not Authorized

This consensus authorizes no V3 release, no all-app POD, no public speedup
wording, no broad V3-over-V2 wording, no true-zero-copy wording, no automatic
partner selection, no V4 work, no C ABI work, and no embedding work.

## Interpretation Rules

The focused POD result can count as material Set-A component-union evidence only
if all of these pass:

- all three variants complete;
- canonical component signatures match;
- productized runner uses component-label outputs;
- `runtime_trunk_executes_end_to_end=true`;
- `component_union_phase_accounting_visible=true`;
- `component_label_columns_present=true`;
- `component_signature_pass_executed=false`;
- runner vs Embree hot speedup is at least `1.20x`;
- runner vs Embree wall speedup is at least `1.20x`;
- runner vs legacy OptiX wall is at least `0.98x`.

If the process exits `124`, times out, fails hardware gate, fails correctness,
or misses metadata, the result is blocked/negative/coverage-only evidence. It is
not a release claim.

## Validation At Consensus Time

Focused local gate:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_m39_component_union_harness_test \
  tests.v3_release_wording_gate_test
Ran 8 tests in 4.400s
OK
```

Full V3 rebuild local gate:

```text
PYTHONPATH=src;. py -3 scripts/run_test_matrix.py --group v3_rebuild
module_count: 119
Ran 619 tests in 75.572s
OK
stdout: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m39_samples_cleanup_20260623_141900.stdout.txt
stderr: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m39_samples_cleanup_20260623_141900.stderr.txt
```

## Goal-Level Decision Audit

Decision: authorize one focused POD after M39 local harness acceptance.

1. Was I foolish?

   No.

2. If yes, what actions made the decision foolish?

   It would be foolish to run all-app or claim V3 speed from this authorization.
   This consensus allows only one focused component-union measurement.

3. Was there another path?

   Yes. Keep the work local. That would avoid cost but would not answer whether
   the M37/M39 runtime trunk produces material evidence on RT hardware.

4. Can I now try a different path that actually solves the problem?

   Yes. Run the single focused POD, preserve artifacts, and let the result
   decide whether this trunk path deserves more V3 work.
