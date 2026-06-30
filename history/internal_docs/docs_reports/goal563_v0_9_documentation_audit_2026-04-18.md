# Goal 563: v0.9 Documentation Audit

Date: 2026-04-18

Repository: `/Users/rl2025/rtdl_python_only`

## Verdict

ACCEPT for the v0.9 documentation audit gate.

After the Goal 561 public-doc refresh and Goal 562 test gate, this audit checked
the user-facing v0.9 documentation path for stale HIPRT wording, broken local
links, and release-boundary overclaims. Two minor stale phrases were found and
fixed during the audit:

- `/Users/rl2025/rtdl_python_only/examples/rtdl_hiprt_ray_triangle_hitcount.py`
  still emitted a JSON `scope` string saying "experimental HIPRT dispatch";
  it now says this is a v0.9 HIPRT candidate prepared-path example and points
  readers to the broader 18-workload `run_hiprt` matrix.
- `/Users/rl2025/rtdl_python_only/docs/current_architecture.md` still used the
  phrase `HIPRT-preview`; it now says `HIPRT-candidate`.

## Audited Public Files

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/current_architecture.md`
- `/Users/rl2025/rtdl_python_only/docs/capability_boundaries.md`
- `/Users/rl2025/rtdl_python_only/docs/quick_tutorial.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/README.md`
- `/Users/rl2025/rtdl_python_only/examples/README.md`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_hiprt_ray_triangle_hitcount.py`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9/support_matrix.md`

## Stale Wording Check

Command:

```bash
rg -n 'experimental HIPRT|Experimental HIPRT|HIPRT preview|preview backend|HIPRT-preview|only for 3D|one workload only|narrow single-workload' \
  README.md \
  docs/README.md \
  docs/current_architecture.md \
  docs/quick_tutorial.md \
  docs/release_facing_examples.md \
  docs/rtdl_feature_guide.md \
  docs/tutorials/README.md \
  docs/capability_boundaries.md \
  examples/README.md \
  examples/rtdl_hiprt_ray_triangle_hitcount.py \
  docs/release_reports/v0_9
```

Result: no matches.

## Link Check

Checked local Markdown links in the 11 main public/v0.9 docs:

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/current_architecture.md`
- `/Users/rl2025/rtdl_python_only/docs/capability_boundaries.md`
- `/Users/rl2025/rtdl_python_only/docs/quick_tutorial.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/README.md`
- `/Users/rl2025/rtdl_python_only/examples/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9/support_matrix.md`

Result:

```text
checked 11 files
bad_links 0
```

## Focused Tests

Command:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal544_hiprt_docs_examples_test \
  tests.goal560_hiprt_backend_perf_compare_test
```

Result:

```text
Ran 3 tests in 0.103s
OK
```

## Documentation State

The current public documentation now consistently states:

- current released version is still `v0.8.0`
- HIPRT is an active `v0.9` candidate, not a released `v0.9.0` surface
- `run_hiprt` has Linux parity coverage for the 18-workload matrix
- `prepare_hiprt` is currently limited to prepared 3D
  `ray_triangle_hit_count`
- HIPRT validation is on Linux NVIDIA/CUDA/Orochi, not AMD GPU
- no RT-core speedup claim is made for the tested GTX 1070 path
- no HIPRT CPU fallback is claimed
- Goal 560 and Goal 562 artifacts are the canonical evidence for current v0.9
  candidate status

## Remaining Release Work

The documentation audit gate is complete. The remaining v0.9 pre-release gate
is the whole-flow audit: verify goal sequence, handoffs/reviews, reports,
testing evidence, and release-boundary wording as a single release candidate
package.
