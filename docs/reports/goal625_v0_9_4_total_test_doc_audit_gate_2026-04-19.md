# Goal 625: v0.9.4 Total Test, Documentation, And Audit Gate

Date: 2026-04-19

Repository: `/Users/rl2025/rtdl_python_only`

Status: `ACCEPT, pending external AI review and explicit release authorization`

## Goal

Before tagging the next public release, perform the three required release gates:

1. Total test gate.
2. Total public documentation refresh.
3. Total release-flow and honesty-boundary audit.

This gate targets `v0.9.4`, which absorbs the untagged `v0.9.2` and `v0.9.3`
candidate work into the next public release line.

## Test Evidence

### Local macOS full suite

Command:

```bash
PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py' -v
```

Transcript:

`/Users/rl2025/rtdl_python_only/docs/reports/goal625_v0_9_4_local_full_unittest_goal_pattern_2026-04-19.txt`

Result:

- `1178 tests`
- `171 skips`
- `OK`
- Runtime: `110.632s`

Note: a default `test*.py` discovery was also run and passed `239 tests`, but it
is not the release gate because many RTDL goal tests use the `goal*_test.py`
filename convention. The release gate is the explicit `*_test.py` discovery
above.

### Public documentation smoke tests

Command:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal512_public_doc_smoke_audit_test tests.goal511_feature_guide_v08_refresh_test tests.goal531_v0_8_release_candidate_public_links_test tests.goal515_public_command_truth_audit_test -v
```

Result:

- `10 tests`
- `OK`

### Public entry smoke

Command:

```bash
PYTHONPATH=src:. python3 scripts/goal497_public_entry_smoke_check.py
```

Transcript:

`/Users/rl2025/rtdl_python_only/docs/reports/goal625_v0_9_4_public_entry_smoke_2026-04-19.json`

Result:

- `valid: true`
- all checked public entry commands succeeded.

### Public command truth audit

Command:

```bash
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py
```

Reports:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal515_public_command_truth_audit_2026-04-17.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal515_public_command_truth_audit_2026-04-17.md`

Result:

- `valid: true`
- public docs checked: `14`
- public commands checked: `244`
- classifications:
  - portable Python/CPU commands: `159`
  - optional native backend gated commands: `44`
  - Linux GPU backend gated commands: `33`
  - Linux PostgreSQL gated commands: `1`
  - visual demo or optional artifact commands: `7`

### Linux focused backend gate

Fresh synced checkout:

`/tmp/rtdl_goal625_release` on `lestat-lx1`

Transcript:

`/Users/rl2025/rtdl_python_only/docs/reports/goal625_v0_9_4_linux_backend_gate_2026-04-19.txt`

Host evidence:

- Python: `3.12.3`
- PostgreSQL: `16.13`, accepting local connections
- GPU: `NVIDIA GeForce GTX 1070`
- Embree probe: `(4, 3, 0)`
- OptiX probe: `(9, 0, 0)`
- Vulkan probe: `(0, 1, 0)`
- HIPRT probe: version `(2, 2, 15109972)`, API `2002`, device type `1`,
  device `NVIDIA GeForce GTX 1070`

Fresh-checkout backend builds performed:

- `make build-hiprt`
- `make build-optix`
- `make build-vulkan`

Focused Linux backend tests:

- OptiX/Vulkan nearest-neighbor, 3D, graph, and DB backend tests.
- HIPRT probe, closest-hit, 2D/3D geometry, neighbor, graph, DB, and prepared
  workload tests.

Result:

- `131 tests`
- `OK`
- Runtime: `64.706s`

### Mechanical checks

Command:

```bash
git diff --check
```

Result:

- clean

## Documentation Updates

The following release-facing documentation was created or refreshed:

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_4/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_4/release_statement.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_4/audit_report.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_4/tag_preparation.md`

The v0.9.4 package now gives a public reader a direct path from the root
README to:

- exact backend/workload support;
- Apple hardware/software boundary;
- HIPRT validation boundary;
- release statement;
- audit report;
- tag preparation status.

## Honesty-Boundary Audit

The release-facing docs were checked for stale or overstated claims. The audit
accepts these statements:

- `v0.9.2` and `v0.9.3` were internal/unreleased candidate milestones absorbed
  into `v0.9.4`.
- Embree remains the mature optimized baseline.
- OptiX, Vulkan, HIPRT, and Apple Metal/MPS RT are real but bounded.
- Apple Metal/MPS RT supports bounded native/native-assisted slices, but DB and
  graph workloads on Apple are Metal-compute/native-assisted, not accelerated
  by Apple ray-tracing hardware.
- HIPRT is validated through the official HIPRT SDK on the Linux NVIDIA CUDA
  path used in testing; no AMD GPU validation or CPU fallback is claimed.
- RTDL is not a DBMS, renderer, graph database, ANN system, or general app
  framework.

Searches for disallowed stale claims found only explicit non-claim sections in
the docs, not positive release claims.

## Flow Audit

Release flow state:

- Source tree is on the `v0.9.4` release target.
- Release docs exist and link the support matrix, release statement, audit
  report, and tag-preparation report.
- Full local test gate passed.
- Public documentation command/audit gates passed.
- Fresh Linux backend gate passed after rebuilding native backend libraries.
- External AI review is still required before this gate can be called fully
  closed.
- No tag or release publication is authorized by this report alone.

## Codex Verdict

Codex accepts Goal 625 as technically ready for external AI review.

No code, documentation, or flow blocker was found in the local and Linux gates
above. Final closure requires at least one external AI review verdict and then
explicit release authorization.
