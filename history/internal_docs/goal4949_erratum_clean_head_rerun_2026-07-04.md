# Goal4949 Erratum: Clean-HEAD Rerun

Date: 2026-07-04

Status: erratum_supersedes_stale_remote_numba_phase_details

## Why This Erratum Exists

After Goal4949 was committed, I found that the POD directory used for the first
Goal4949 measurement was not a git checkout. It was a copied runtime directory
that still contained stale experimental writer code from an earlier path-split
line.

That means the original Goal4949 Numba writer subphase fields such as
`path_split_materialize_map*_sec` came from stale remote code, not from the
current tracked source.

This was not acceptable evidence. I therefore created a clean POD copy directly
from local `HEAD`, copied only the already-built OptiX library and public sample
data into it, converted shell scripts to LF for Linux execution, and reran the
public sample from that clean source tree.

Clean POD directory:

```text
/root/rtdl_goal4951_clean
```

Source construction:

```text
git archive HEAD -> /root/rtdl_goal4951_clean
copy /root/rtdl_goal4937/build/librtdl_optix.so
copy public RayJoin sample data
```

## Clean-HEAD Correctness

Both routes remained byte-identical to the author answer:

| Route | Byte Equal | SHA256 |
|---|---:|---|
| `section57_overlay.py` | true | `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e` |
| `section57_overlay_numba.py` | true | `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e` |

## Clean-HEAD Performance

| Route | Elapsed | Writer | Reprojection | Sort Total | Vertex PIP |
|---|---:|---:|---:|---:|---:|
| baseline `section57_overlay.py` | 6.917s | 2.093s | 0.691s | 0.794s | 0.019s |
| current `section57_overlay_numba.py` | 7.337s | 3.281s | 0.758s | 0.796s | 0.020s |

The current tracked Numba route is still slower than baseline:

- elapsed: `7.337s` vs `6.917s`
- writer: `3.281s` vs `2.093s`

## Correct Current-Source Writer Breakdown

The clean current-source Numba writer path reports:

| Writer Subphase | Seconds |
|---|---:|
| `skip_plan_sec` | 0.330 |
| `group_xsects_map0_sec` | 0.087 |
| `group_xsects_map1_sec` | 0.013 |
| `chain_loop_map0_sec` | 1.318 |
| `chain_loop_map1_sec` | 0.981 |
| `generic_output_assembly_sec` | 0.353 |
| `bulk_writelines_sec` | 0.079 |

So the corrected source of the slowdown is:

- current Numba writer still pays large chain-loop costs;
- then it adds generic output assembly overhead;
- final file writing remains small.

This is consistent with Goal4930 / Goal4938 / Goal4940: the expensive structural work is still in host-side chain/path assembly, and a downstream generic assembly pass is too late.

## Superseded Evidence

The original Goal4949 artifact's path-split-specific fields are disqualified as
evidence for current `HEAD`.

Disqualified fields include:

- `path_split_materialize_map0_sec`
- `path_split_materialize_map1_sec`
- `path_split_format_map0_sec`
- `path_split_format_map1_sec`

Those fields were produced by stale POD code. They must not be cited as current-source evidence.

## What Does Not Change

The engineering conclusion does not change:

1. The current Numba app-layer helper is not a RayJoin Section 5.7 performance win.
2. Prepared-hot PIP traversal is not the bottleneck.
3. Layer 1/2 connector capability remains proven by Goals 4942-4948.
4. The plausible remaining performance target is Layer 3 structural output/path assembly, not more app-layer Numba writer wrapping.

## Exit Label

`erratum_clean_head_rerun_confirms_current_numba_helper_not_performance_win`
