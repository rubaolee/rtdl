# Goal 410: Tutorial And Example Cross-Platform Check

## Scope

This goal checked the public tutorial ladder and release-facing example surface
for the corrected `v0.6.1` line.

The checked command surface is encoded in:

- [goal410_tutorial_example_check.py](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/scripts/goal410_tutorial_example_check.py)

That harness covers:

- the front-door hello-world/tutorial commands
- the sorting tutorial
- the released `v0.2.0` segment/polygon examples
- the released `v0.4.0` nearest-neighbor examples
- the released `v0.6.1` graph examples
- the release-facing app examples
- the bounded visual demo sanity commands

Total public command cases:

- `35`

## Public-surface changes made

New public graph examples:

- [rtdl_graph_bfs.py](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/examples/rtdl_graph_bfs.py)
- [rtdl_graph_triangle_count.py](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/examples/rtdl_graph_triangle_count.py)

New tutorial:

- [graph_workloads.md](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/tutorials/graph_workloads.md)

Updated front-door docs:

- [README.md](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/README.md)
- [quick_tutorial.md](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/quick_tutorial.md)
- [release_facing_examples.md](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_facing_examples.md)
- [tutorials/README.md](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/tutorials/README.md)
- [examples/README.md](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/examples/README.md)

Most important setup corrections:

- the public docs now use a local virtual environment instead of assuming a
  writable global `pip` environment
- the public docs now explicitly note Debian/Ubuntu `python3-venv` as the fix
  when `ensurepip` is unavailable
- the public docs now explicitly show the Linux GPU backend build step:
  - `make build-optix`
  - `make build-vulkan`

## Machine results

### macOS local

- machine label: `macos-local`
- raw report:
  - [goal410_macos_tutorial_example_check_2026-04-15.json](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal410_macos_tutorial_example_check_2026-04-15.json)
- backend availability:
  - `cpu_python_reference = True`
  - `cpu = True`
  - `embree = True`
  - `optix = False`
  - `vulkan = False`
- result:
  - `29` passed
  - `0` failed
  - `6` skipped
- skip reason:
  - the skipped cases are the Linux-only GPU commands

### Linux `lestat-lx1`

- machine label: `linux-lestat-lx1`
- raw report:
  - [goal410_linux_tutorial_example_check_2026-04-15.json](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal410_linux_tutorial_example_check_2026-04-15.json)
- backend availability:
  - `cpu_python_reference = True`
  - `cpu = True`
  - `embree = True`
  - `optix = True`
  - `vulkan = True`
- result:
  - `35` passed
  - `0` failed
  - `0` skipped

Important Linux note:

- this host lacked the `python3-venv` OS package, so the release docs were
  updated to call that out explicitly
- the host already had the required Python packages available for the
  validation run
- after repo sync, the Linux GPU backend libraries were rebuilt with:
  - `make build-optix`
  - `make build-vulkan`

### Windows `lestat-win`

- machine label: `windows-lestat-win`
- raw report:
  - [goal410_windows_tutorial_example_check_2026-04-15.json](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal410_windows_tutorial_example_check_2026-04-15.json)
- backend availability:
  - `cpu_python_reference = True`
  - `cpu = True`
  - `embree = True`
  - `optix = False`
  - `vulkan = False`
- result:
  - `29` passed
  - `0` failed
  - `6` skipped
- skip reason:
  - the skipped cases are the Linux-only GPU commands

## Final status

Goal 410 is accepted as a public-surface check and correction pass.

What is now true:

- users have a correct fresh-checkout setup path for the public tutorial and
  example surface
- the released graph line now has real top-level example CLIs
- `cpu_python_reference` and `cpu` were validated on all three maintained
  machines
- `embree` was validated on all three maintained machines
- `optix` and `vulkan` were validated on the Linux GPU host

Bounded honesty note:

- the command matrix intentionally covers the public tutorial ladder and
  release-facing example surface
- it does not claim that every internal, historical, generated, or preserved
  artifact under `examples/` is part of the public first-run contract
