# Goal 1398 - v1.5 Standalone Release Gate

Date: 2026-05-06

## Status

Implemented a machine-readable v1.5 standalone release gate after the Goal1397
roadmap consensus.

The new gate is intentionally separate from the older internal primitive
readiness gate:

- `validate_v1_5_internal_readiness_gate()` still represents the primitive
  packet and contract-readiness surface.
- `validate_v1_5_standalone_release_gate()` represents the expanded standalone
  v1.5 release boundary.

## Current Gate Result

Current status:

```text
blocked_pending_standalone_language_completion
```

Passed gates:

- `primitive_packet_prerequisite`
- `roadmap_consensus`

Failed gates:

- `collect_k_bounded_resolution`
- `app_migration_classification`
- `same_contract_per_app_correctness`
- `same_contract_per_app_benchmarks`
- `test_backed_support_maturity_matrix`
- `release_docs_and_public_wording`

The gate explicitly reports:

- primitive-only readiness is prerequisite evidence only;
- primitive-only readiness is not sufficient for standalone v1.5 release;
- no `v1.5` tag is authorized;
- no public release wording is authorized;
- no public speedup wording is authorized;
- `COLLECT_K_BOUNDED` remains unresolved until promoted or explicitly excluded;
- v1.6-v2.0 remain the partner-mechanism track.

## Added API

Exports added through `rtdsl`:

- `V1_5_STANDALONE_RELEASE_STATUS`
- `V1_5_STANDALONE_RELEASE_SCOPE_KIND`
- `V1_5_STANDALONE_RELEASE_REQUIRED_GATES`
- `V1_5_STANDALONE_RELEASE_BLOCKERS`
- `V1_5_STANDALONE_RELEASE_ALLOWED_NEXT_ACTIONS`
- `V1_5_STANDALONE_PARTNER_TRACK`
- `v1_5_standalone_release_gate`
- `validate_v1_5_standalone_release_gate`

## Validation

Focused tests:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1398_v1_5_standalone_release_gate_test tests.goal1367_v1_5_internal_readiness_gate_test
```

Result:

```text
Ran 14 tests in 0.004s
OK
```

The gate payload was also printed locally with:

```text
PYTHONPATH=src:. python3 - <<'PY'
import json
import rtdsl as rt
print(json.dumps(rt.validate_v1_5_standalone_release_gate(), indent=2, sort_keys=True))
PY
```

## Next Work

The next standalone v1.5 task should be `collect_k_bounded_resolution`, because
bounded row collection determines whether row-returning apps can be included in
standalone-complete v1.5 or must be explicitly excluded from the release scope.

