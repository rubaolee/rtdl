# RayJoin Section 5.7 Polygon Overlay V4 Workload Status

This note records the current V4.0 paper-reproduction path for the RayJoin
Section 5.7 Polygon Overlay workload. It is not a tutorial and it does not teach
polygon overlay as an application algorithm. The purpose is to make the RTDL
workload contract, entrypoint, comparison protocol, and remaining run
requirements explicit.

## Current Status

RTDL now exposes a public paper-reproduction wrapper for the Section 5.7
workload:

```bash
python3 examples/paper_reproduction/rayjoin.py --section57-plan --dataset-root data/rayjoin_section57_cdb
python3 examples/paper_reproduction/rayjoin.py --section57-run --dataset-root data/rayjoin_section57_cdb --query-exec /workspace/RayJoin_fresh/release/bin/query_exec --polyover-exec /workspace/RayJoin_fresh/release/bin/polyover_exec
python3 examples/paper_reproduction/rayjoin.py --section57-compare-v214 --json
python3 examples/paper_reproduction/rayjoin.py --section57-preflight --dataset-root data/rayjoin_section57_cdb --query-exec /workspace/RayJoin_fresh/release/bin/query_exec --polyover-exec /workspace/RayJoin_fresh/release/bin/polyover_exec --json
python3 examples/paper_reproduction/rayjoin.py --section57-auto-numba --dataset-root data/rayjoin_section57_cdb --partner numba --select fastest_valid
```

The wrapper delegates to the existing Section 5.7 matrix runner:

```text
scripts/rayjoin_section57_overlay_matrix.py
```

The paper suite definition lives in:

```text
src/rtdsl/rayjoin_paper_suite.py
```

The V4+Numba auto-primitive planner lives in:

```text
src/rtdsl/rayjoin_numba_auto_planner.py
```

It is a semantic planner/evidence route: users name Section 5.7 and
`partner="numba"`; RTDL enumerates candidate primitive combinations and writes a
scoreboard. It does not count as a full paper-reproduction result until the
author-code, V2.14 exact-suite, and V4+Numba selected-plan columns all have
valid correctness and timing evidence.

The V4+Numba selected-plan column has one additional hard gate: the Section 5.7
candidate/refinement stream must be exposed as device-resident columns. Static
source inspection now finds the required LSI/PIP device-column components and
Numba continuation pieces, but that is not performance evidence. A real
Section 5.7 POD run must still validate the end-to-end composition on exact
inputs and the author baseline.

The Section 5.7 matrix runner also accepts `v4_numba` as an implementation:

```bash
python3 examples/paper_reproduction/rayjoin.py --section57-run \
  --implementations author_rt,rtdl_optix,rtdl_embree,v4_numba \
  --dataset-root /path/to/rayjoin_section57_cdb \
  --query-exec /workspace/RayJoin_fresh/release/bin/query_exec \
  --polyover-exec /workspace/RayJoin_fresh/release/bin/polyover_exec
```

This keeps the author-code baseline, RTDL exact-suite baseline, and V4+Numba
selected plan in one summary table.

## What Counts

A full Section 5.7 claim requires all of the following:

- the same RayJoin Section 5.7 overlay pair selection;
- the same dataset root for V2.14 and V4.0;
- exact paper-preprocessed CDB inputs, or same-source regenerated CDB inputs
  explicitly labeled as such;
- the RayJoin author binaries for the author baseline:
  `query_exec` and `polyover_exec`;
- separate result rows for `author_rt`, `rtdl_optix`, `rtdl_embree`, and
  `v4_numba`;
- for the V4+Numba auto planner, separate result columns for `author_code`,
  `v2_14_exact_suite`, and `v4_numba_selected_plan`;
- for the V4+Numba selected plan, a device-column producer for the Section 5.7
  candidate/refinement stream, not host row materialization;
- correctness/status and timing recorded together;
- an 8/8 overlay-pair completion summary before any full Section 5.7 claim.

`overlay_seed` rows do not count as polygon overlay. Fixture, synthetic, or
analogue inputs do not count as exact paper reproduction.

## Fair V2.14 Versus V4.0 Protocol

The fair comparison is not "old wrapper versus new wrapper". It is:

```text
V2.14 exact-suite route on the Section 5.7 contract
versus
V4.0 paper-reproduction wrapper on the same Section 5.7 contract
```

Both sides must use the same dataset root, same pair ids, same author binaries,
same warmup/repeat policy, and the same input-provenance label.

The V4.0 helper prints the paired command contract:

```bash
python3 examples/paper_reproduction/rayjoin.py --section57-compare-v214 --pairs county_zipcode --json
```

## POD Run Requirements

A real POD run needs:

- NVIDIA GPU runtime for the RTDL OptiX route;
- the RayJoin author binaries:
  `/workspace/RayJoin_fresh/release/bin/query_exec`
  and `/workspace/RayJoin_fresh/release/bin/polyover_exec`;
- a dataset root with the expected `point_cdb/...` layout;
- enough time to run all eight Section 5.7 overlay pairs for the selected
  implementations.

Recommended sequence:

```bash
python3 examples/paper_reproduction/rayjoin.py --section57-preflight --dataset-root /path/to/rayjoin_section57_cdb --query-exec /workspace/RayJoin_fresh/release/bin/query_exec --polyover-exec /workspace/RayJoin_fresh/release/bin/polyover_exec --json

python3 examples/paper_reproduction/rayjoin.py --section57-plan --dataset-root /path/to/rayjoin_section57_cdb --output-dir artifacts/rayjoin_section57

python3 examples/paper_reproduction/rayjoin.py --section57-run --dataset-root /path/to/rayjoin_section57_cdb --output-dir artifacts/rayjoin_section57 --query-exec /workspace/RayJoin_fresh/release/bin/query_exec --polyover-exec /workspace/RayJoin_fresh/release/bin/polyover_exec

python3 examples/paper_reproduction/rayjoin.py --section57-summary --dataset-root /path/to/rayjoin_section57_cdb --output-dir artifacts/rayjoin_section57
```

The summary artifacts are:

```text
artifacts/rayjoin_section57/section57_overlay_summary.json
artifacts/rayjoin_section57/section57_overlay_summary.md
```

## Local Verification Already Performed

The following local checks were run successfully on the Windows workspace:

```bash
py -3 -m unittest tests.v4_rayjoin_section57_public_entry_test
py -3 -m unittest tests.v4_frontdoor_test
py -3 examples\paper_reproduction\rayjoin.py --section57-compare-v214 --pairs county_zipcode --json
```

These checks verify the public wrapper surface, the paired V2.14 comparison
protocol, and the public front-door gate. Maintainers also keep lower-level
suite, publication-decision, and public-doc cleanup tests for the 8-pair plan
shape, dry-run recording path, and public wording checks. Local tests do
not replace a real POD run with exact inputs and author binaries.

The local preflight command is:

```bash
python3 examples/paper_reproduction/rayjoin.py --section57-preflight --dataset-root data/rayjoin_section57_cdb --query-exec /workspace/RayJoin_fresh/release/bin/query_exec --polyover-exec /workspace/RayJoin_fresh/release/bin/polyover_exec --json
```

It shows the Section 5.7 device-column components are statically declared, while
the local Windows workspace is still missing exact CDB inputs, author binaries,
Numba CUDA, and an RT-core GPU.

## Remaining Work

The remaining work is execution, not curriculum:

1. Run `--section57-plan` on the real dataset root.
2. Confirm the plan shows 8/8 overlay pairs input-ready.
3. Run `--section57-run` with author binaries and RTDL routes.
4. Read `section57_overlay_summary.json` and compare V2.14 versus V4.0 only on
   rows that share the same input and timing contract.
5. Record whether the workload is a complete exact reproduction, a
   same-source-regenerated reproduction, or waiting on missing paper inputs.
