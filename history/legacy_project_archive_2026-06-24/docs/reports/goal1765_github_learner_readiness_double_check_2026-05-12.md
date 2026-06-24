# Goal1765 GitHub Learner Readiness Double Check

Date: 2026-05-12

## Verdict

`github_learner_path_ready_for_v1_8_source_tree_release`

The GitHub learner path is now coherent for v1.8: a new user can start from the
front page, run a portable source-tree example, learn the kernel shape, choose
an app example, and understand the Python/app versus RTDL/generic-engine
boundary without reading historical goal reports first.

This report does not authorize a tag, version bump, push, package upload, or
release.

## Learner Path Checked

| Step | File | What the learner should understand |
| --- | --- | --- |
| 1 | `README.md` | RTDL is Python-hosted; v1.8 is source-tree Python+RTDL; native engine stays app-agnostic |
| 2 | `docs/README.md` | docs order and the v1.8 learner rule |
| 3 | `docs/quick_tutorial.md` | first run, kernel shape, Python app / generic engine split |
| 4 | `examples/README.md` | which examples to run and how to read app names |
| 5 | `docs/app_example_quickstart.md` | how to pick an app and avoid overclaims |
| 6 | `docs/current_architecture.md` | why Python owns apps and RTDL owns generic kernel/runtime contracts |
| 7 | `docs/performance_model.md` | why backend selection is not a public speedup claim |

## Portable Commands

The learner path remains source-tree based:

```bash
PYTHONPATH=src:. python examples/rtdl_hello_world.py
PYTHONPATH=src:. python examples/rtdl_hello_world_backends.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_feature_quickstart_cookbook.py
```

No `pip install -e .` or package-install claim is made.

## Design Message

The docs now repeat one design message across front page, docs index, tutorial,
and examples:

```text
Python writes the application.
RTDL expresses the RT-shaped kernel.
Native backends execute generic engine contracts.
```

This is the right learner-level explanation of the v1.8 release boundary.

## Boundary

The GitHub learner path is ready for source-tree v1.8 release use, but only
after explicit user release authorization. The path remains conservative about
package installation, performance claims, backend maturity, partner support,
and zero-copy.
