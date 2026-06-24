# Next Primary AI V3 Continuation Handoff

Date: 2026-06-18

## Situation

The user asked Codex to stop being the primary worker after repeated permission
approval interruptions. The immediate engineering task was completed before this
handoff: V3 current-scope completion is now closed by `Goal4614 / V3 M215`.

The next primary AI should continue from GitHub `main`, not from memory in this
thread.

## Repository

Local workspace:

```text
C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review
```

Remote:

```text
origin https://github.com/rubaolee/rtdl
```

Branch:

```text
main
```

Important recent commits before this handoff document:

```text
0d4ffcb7 Add V3 current-scope completion gate
8dbcd46d Add prefix-stage C examples smoke
7360689a Add staged C ABI last-error example
2cb56ad3 Add C ABI last-error diagnostics smoke
3a16f9d1 Add C ABI independent context concurrency smoke
```

After this handoff is committed, run:

```bash
git log -5 --oneline
```

to see the final handoff commit hash.

## Pod

Known pod access from this thread:

```bash
ssh root@157.157.221.29 -p 22234 -i ~/.ssh/id_ed25519_rtdl_codex_current_pod
```

Pod workspace:

```text
/workspace/rtdl_v3_main
```

At the time of this handoff, the pod had already validated the V3 completion
gate. After pulling the latest GitHub `main`, align the pod before doing new
work:

```bash
cd /workspace/rtdl_v3_main
git fetch origin main
git reset --hard origin/main
git status --short
```

Only do that reset if the pod still contains the old temporary Codex-generated
commit. That temporary pod commit was superseded by the pushed GitHub `main`.

## V3 Status

V3 current scope is complete.

What "complete" means here:

- all ten benchmark-app current routes are closed;
- runtime, claim/evidence, design-blocker, and future-design queues are empty;
- the app-author route policy is documented;
- the canonical validation surface is `scripts/run_test_matrix.py --group v3_current`;
- V4 embeddability work is explicitly deferred and is not a V3 blocker.

Final completion report:

```text
docs/reports/goal4614_v3_0_m215_current_scope_completion_gate_2026-06-18.md
```

Final completion script/test:

```text
scripts/goal4614_m215_v3_current_scope_completion_gate.py
tests/goal4614_v3_0_m215_current_scope_completion_gate_test.py
```

Current matrix:

```text
scripts/run_test_matrix.py --group v3_current
104 modules / 353 tests on the pod
```

## Validation Already Run On Pod

Focused tests:

```text
python3 -m unittest \
  tests.goal4544_v3_0_m145_app_author_strategy_doc_test \
  tests.goal4546_v3_0_m147_current_test_matrix_gate_test \
  tests.goal4614_v3_0_m215_current_scope_completion_gate_test

Result: 13 tests OK
```

Full V3 current matrix:

```text
PYTHONPATH=src:. python3 scripts/run_test_matrix.py --group v3_current

Result: 104 modules / 353 tests OK
```

Source-tree doctor:

```text
PYTHONPATH=src:. python3 scripts/rtdl_source_tree_doctor.py --json

Result: ok=true
Warnings: optional imageio and imageio_ffmpeg missing
```

## V3 Claim Boundary

Do not expand V3 into public claims without a new reviewed release packet.

Blocked by Goal4614:

- public release tag authorization;
- public speedup tables;
- broad RT-core speedup wording;
- paper-reproduction wording;
- RTDL-beats-specialized-code wording;
- automatic partner selection;
- stable SDK wording;
- generated binding package wording;
- device-buffer query execution wording;
- external CUDA stream ordering wording;
- public true-zero-copy wording;
- app-specific native-engine logic.

## V4 Deferrals

Treat these as future V4 work, not V3 blockers:

- stable packaged SDK;
- generated language bindings;
- device-buffer query route;
- external CUDA stream ordering;
- public true-zero-copy proof;
- OptiX/Embree C ABI execution;
- optional device-callable fusion;
- AMD/HIPRT evidence when hardware exists.

## Benchmark Apps Covered By V3 Current Scope

- Hausdorff / X-HD
- Spatial RayJoin
- RT-DBSCAN
- Robot collision
- Contact manifold
- RayDB-style
- Barnes-Hut
- LibRTS spatial index
- RTNN
- Triangle counting

Route policy is documented in:

```text
docs/learn/v3_0_app_author_implementation_strategy.md
docs/learn/benchmark_evidence_index.md
```

## Successor Work Rules

- Start from `git pull --ff-only origin main`.
- Run `git status --short` before edits.
- If the user asks for V4, begin from the V4 deferrals above.
- Do not reopen V3 benchmark-app current scope unless a concrete bug is found.
- Do not compare RTDL to specialized C++/CUDA/OptiX/Embree code without matching
  data, output contract, partner policy, and timing basis.
- Do not hide partner timing or data movement.
- If partner logic is needed, test the best measured choice and a no-C++ Numba
  path when the claim depends on user accessibility.
- If a command environment becomes blocked, change execution path instead of
  repeatedly asking the user for permissions.
- For every goal-level decision, answer the four-question self-audit before
  proceeding or when reporting the decision:
  1. Was I foolish?
  2. If yes, what actions made the decision foolish?
  3. Was there another path that would have avoided getting stuck on that idea?
  4. Can I now try a different path that actually solves the problem?
- Treat that self-audit as a periodic reminder after context compaction, user
  correction, paid-pod decisions, release wording changes, benchmark
  interpretation decisions, and any plan reroute.

## First Commands For The Successor

Local:

```powershell
cd C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review
git pull --ff-only origin main
git status --short
$env:PYTHONPATH = "src;."
py -3 scripts\rtdl_source_tree_doctor.py --json
py -3 scripts\run_test_matrix.py --group v3_current
```

Pod:

```bash
ssh root@157.157.221.29 -p 22234 -i ~/.ssh/id_ed25519_rtdl_codex_current_pod
cd /workspace/rtdl_v3_main
git fetch origin main
git reset --hard origin/main
PYTHONPATH=src:. python3 scripts/rtdl_source_tree_doctor.py --json
PYTHONPATH=src:. python3 scripts/run_test_matrix.py --group v3_current
```

## Human Context

The user is angry because the prior agent repeatedly interrupted work for
permissions after the user had already granted broad permission. Do not argue
about that. The correct response is to keep the repo clean, show verifiable
state, and continue only from clear Git-backed evidence.
