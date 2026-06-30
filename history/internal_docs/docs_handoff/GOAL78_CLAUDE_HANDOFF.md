# Goal 78 Claude Handoff

## Mission

Finish **Goal 78: Vulkan positive-hit sparse redesign** in the RTDL repo.

Repo:

- `/Users/rl2025/rtdl_python_only`

Primary code target:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_vulkan.cpp`

You are expected to:

1. design and implement the Vulkan positive-hit `pip` redesign
2. preserve exact parity
3. preserve full-matrix behavior
4. add focused validation/tests/docs
5. write a concise result report

Do **not** publish or push anything.

I will review your code and report after you finish.

---

## Goal Definition

The current Vulkan positive-hit `pip` path is correctness-clean but structurally wasteful.

The goal is to replace the current dense host full-scan behavior with:

- **sparse GPU candidate generation**
- then **host exact finalize on candidates only**

This goal is about the **positive-hit** path only.

It is **not** about changing:

- full-matrix `pip`
- RTDL DSL semantics
- emitted schema
- parity requirements

---

## Current Problem

The current bottleneck is in:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_vulkan.cpp`

Function:

- `run_pip_vulkan(...)`

Inside the `if (positive_only != 0u)` / positive-hit logic, the effective behavior is still dense and host-heavy.

Current waste pattern:

1. GPU writes dense `point_count × poly_count` output
2. host downloads dense rows
3. host exact-finalizes all pairs

That defeats the point of the positive-hit contract on long workloads.

Relevant existing code excerpt is saved at:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal78_vulkan_positive_hit_sparse_redesign_code_excerpt_2026-04-04.txt`

Relevant context reports:

- `/Users/rl2025/rtdl_python_only/docs/goal_78_vulkan_positive_hit_sparse_redesign.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal78_vulkan_positive_hit_sparse_redesign_plan_2026-04-04.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal72_vulkan_long_county_prepared_exec_2026-04-04.md`

---

## Required End State

For `positive_only` Vulkan `pip`:

1. GPU must generate **candidate pairs only**
2. host exact finalize must run **only on those candidates**
3. final output rows must still be:
   - `point_id`
   - `polygon_id`
   - `contains = 1`
4. exact parity must remain preserved against the existing truth path

For full-matrix `pip`:

- behavior must remain unchanged

---

## Design Constraints

You must follow these constraints:

### 1. Preserve semantics

Do not change the external RTDL positive-hit contract.

Positive-hit means:

- emit only positive rows
- no false positives in final output
- no false negatives in final output

### 2. Keep host exact finalize

Do **not** weaken parity by trusting approximate GPU positives as final truth.

Allowed:

- GPU candidate generation
- host exact validation of those candidates

Not allowed:

- approximate GPU-only final answer
- parity weakening for speed

### 3. Do not broaden scope

Do not redesign unrelated workloads.

Do not change:

- LSI
- overlay
- ray hitcount
- segment-polygon hitcount
- point-nearest-segment

### 4. Full-matrix path must stay intact

The dense full-matrix `pip` path is not the target of this goal.

### 5. Keep patch bounded

Prefer changing only the minimum necessary files.

Expected main file:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_vulkan.cpp`

Possible supporting files only if truly needed:

- `/Users/rl2025/rtdl_python_only/src/rtdsl/vulkan_runtime.py`
- `/Users/rl2025/rtdl_python_only/tests/...`
- `/Users/rl2025/rtdl_python_only/docs/reports/...`

---

## Strongly Recommended Implementation Shape

This is the intended design direction.

### Positive-hit Vulkan redesign

Use a **two-stage positive-hit path**:

1. GPU stage:
   - generate sparse candidate pairs
   - candidate pair should identify at least:
     - point id or point index
     - polygon id or polygon index

2. Host stage:
   - exact finalize only those candidate pairs
   - use GEOS path when available
   - otherwise use exact CPU point-in-polygon fallback

3. Final materialization:
   - allocate output only for validated positives
   - return only positive rows

This is much better than the current dense `point_count × poly_count` path.

### Candidate representation

You can choose an internal representation, but it should be compact and unambiguous.

Practical options:

- `(point_index, polygon_index)` pairs
- `(point_id, polygon_id)` pairs

Index-based pairs are usually better internally because the exact finalize can map indices to original arrays cheaply.

### Candidate deduplication

Be careful about duplicate candidates from the GPU path.

You must ensure final emitted positives are unique and parity-clean.

Acceptable approaches:

- deduplicate candidate pairs before exact finalize
- or deduplicate after exact finalize before materialization

### Output contract

Final positive-hit rows must still be standard `RtdlPipRow` rows:

- `point_id`
- `polygon_id`
- `contains`

with `contains = 1u`

---

## What I Will Reject

I will reject the patch if it does any of the following:

1. still exact-finalizes all `point_count × poly_count` pairs on the host
2. weakens parity
3. changes full-matrix behavior
4. changes public RTDL semantics without a very strong reason
5. mixes in unrelated cleanup or paper edits

---

## Existing Review Boundary

This repo currently has unrelated unpublished paper/doc edits in the working tree.

Do **not** touch unrelated paper files or presentation files.

Ignore unrelated modified/untracked files unless they are directly required for Goal 78.

Expected clean write scope:

- `src/native/rtdl_vulkan.cpp`
- possibly one or two focused test/report files

---

## Required Tests

At minimum, add or update focused tests so the redesign is reviewable.

You must cover:

1. positive-hit parity still holds
2. positive-hit output contains only positives
3. full-matrix behavior is unchanged
4. no regression to row shape / field names

If there is already a good existing Vulkan PIP test surface, extend that rather than inventing a broad new suite.

Useful existing files to inspect:

- `/Users/rl2025/rtdl_python_only/tests/rtdsl_vulkan_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal71_prepared_backend_positive_hit_county_test.py`

If you add a new focused test file, keep it tightly scoped.

---

## Required Validation

Before handing back, run the smallest validation set that actually proves the patch.

At minimum:

```bash
cd /Users/rl2025/rtdl_python_only
python3 -m py_compile src/rtdsl/vulkan_runtime.py tests/rtdsl_vulkan_test.py
PYTHONPATH=src:. python3 -m unittest tests.rtdsl_vulkan_test
```

If you add a new Goal 78-specific test:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest tests.<your_goal78_test_module>
```

If you can run a stronger local validation safely, do it and report it.

If you cannot run some validation, say so explicitly.

---

## Required Deliverables

When you finish, produce these:

### 1. Code changes

Edit the needed code files directly.

### 2. Result report

Write:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal78_vulkan_positive_hit_sparse_redesign_status_2026-04-04.md`

The report must include:

- what changed
- why it changed
- exact files changed
- what tests you ran
- what still remains risky

### 3. Final handback message

In your final response, explicitly list:

- files changed
- tests run
- whether parity risk remains

---

## Final Success Condition

This handoff is successful if:

- the dense host full-scan path is gone from Vulkan positive-hit `pip`
- the redesign is bounded and reviewable
- full-matrix behavior is unchanged
- tests/report are present
- I can review the patch and decide whether to approve it for the next step

