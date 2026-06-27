The review is complete. Here are the findings, ordered by severity:

---

## Findings

### MEDIUM — `schemas/rayjoin_plan.schema.json` is an orphaned live file

`schemas/` now contains both `rtdl_plan.schema.json` (canonical, correctly wired in `plan_schema.py`) and `rayjoin_plan.schema.json` (old, `$id: rayjoin-plan-v1alpha1.json`, not referenced by any live code). The old file creates visual confusion by implying two co-equal schemas exist.

**Fix**: Move to `history/` or annotate as superseded.

---

### MEDIUM — `generated/` plan files carry the old schema ID

The four committed plan.json files under `generated/` still contain `"$schema": "https://rtdl.dev/schemas/rayjoin-plan-v1alpha1.json"`. The `tests/golden/` counterparts are correctly updated; `generated/` is not. These are committed artifacts, so they're part of the live surface.

**Fix**: Regenerate via the current pipeline, or update the schema ID strings in-place.

---

### LOW — Stale error message in `lowering.py:526`

`_build_output_record` — used by all six canonical lowering paths — raises:
```python
raise ValueError(f"unsupported emitted field for current RayJoin lowering: {name}")
```
This is in the canonical path, not in the legacy alias.

**Fix**: Change to `"current RTDL lowering"`.

---

## What Is Clean

Everything structural is correct:

- `ir.py`: `RTExecutionPlan` canonical, `RTDL_PLAN_SCHEMA_ID` correct, `RayJoinPlan` alias clearly labeled. `to_dict()` / `format()` both use neutral "RTDL Backend Plan" framing.
- `lowering.py`: All six paths emit `backend="rtdl"` unconditionally. `lower_to_rayjoin` is a one-line delegate with a correct docstring.
- `plan_schema.py`: Points to the new schema file only.
- `__init__.py`: Canonical names are primary; aliases are exported and labeled. `RAYJOIN_PAPER_TARGETS` / `RayJoinBoundedPlan` / `RayJoinPublicAsset` are paper/dataset reference names — not architectural identity claims — acceptable as-is.
- `README.md`: `backend="rtdl"` example, `lower_to_execution_plan` as canonical pipeline step, correct three-level hierarchy framing.
- `docs/rtdl/`: All live examples use `backend="rtdl"`; legacy spelling is noted as compatibility-only.
- `tests/rtdsl_py_test.py`: Canonical tests use `backend="rtdl"`. The compatibility test precisely asserts `compiled.backend == "rayjoin"` normalizes to `plan.backend == "rtdl"`. Golden file tests are consistent with updated goldens.

---

`Consensus to continue`
