# Goal5205 Fast ASCII PLY Matrix Loader Result

Date: 2026-07-08

## Verdict

```text
completed_fast_ascii_ply_matrix_loader__user_visible_load_floor_reduced
```

## Purpose

After Goal5204, the route-local Dragon -> HappyBuddha Level-B line was already
down to:

```text
route_wall ~= 1.17-1.18s
max_nearest_reduction ~= 0.001s
```

But the user-visible full-public run still paid a large input front-door cost:

```text
load_full_inputs ~= 1.69s
total ~= 3.08-3.09s
```

Goal5205 attacks only this app-owned public PLY input bridge. It does not change
RTDL core semantics or the X-HD route algorithm.

## Implementation

Changed `Paper-reproduction-apps/x-hd-paper/scripts/xhd_input_loader.py`:

- extracted `_read_ascii_ply_vertex_header(...)`;
- changed `load_ascii_ply_vertex_matrix(...)` from per-line Python
  `split()/float()` loops to:

```python
np.loadtxt(
    path,
    dtype=np.float64,
    skiprows=header_lines,
    max_rows=vertex_count,
    usecols=coordinate_indices,
    ndmin=2,
)
```

- preserved fail-closed ASCII PLY validation;
- preserved arbitrary vertex property order through `usecols`;
- preserved the legacy row loader by converting the matrix output back to
  Python tuple rows.

No RTDL core file was changed for this goal. This remains app-owned input
handling.

## Validation

Local:

```text
py -m unittest \
  tests.goal5205_fast_ascii_ply_matrix_loader_test \
  tests.goal5203_numpy_point_matrix_input_loader_test \
  tests.goal5127_xhd_generic_nearest_pipeline_extraction_test \
  tests.goal5128_non_hausdorff_max_nearest_consumer_test

Ran 14 tests OK

py_compile = OK
```

Local loader probe on the public Stanford PLYs:

```text
dragon_vrip.ply manual matrix loader before this goal: ~=1.22s
dragon_vrip.ply np.loadtxt path:                  ~=0.42-0.51s
happy_vrip.ply np.loadtxt path:                   ~=0.54-0.61s
```

POD:

```text
host = 213.173.108.24
port = 13502
gpu = NVIDIA RTX 4000 Ada Generation
driver = 550.127.05

python -m unittest \
  tests.goal5205_fast_ascii_ply_matrix_loader_test \
  tests.goal5203_numpy_point_matrix_input_loader_test \
  tests.goal5127_xhd_generic_nearest_pipeline_extraction_test \
  tests.goal5128_non_hausdorff_max_nearest_consumer_test

Ran 14 tests OK
```

## Full-Public Evidence

Artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5205_fast_ply_matrix_loader_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5205_fast_ply_matrix_loader_confirm2_graphics_dragon_happy_buddha_2026-07-08.json
```

Both runs:

```text
matched = true
author_abs_diff ~= 2.3849e-9
max_reduction_strategy = finite_max_then_tie_lexsort
max_tie_candidate_count = 1
```

Run 1:

```text
load_full_inputs ~= 0.682s
route_wall       ~= 1.171s
case_total       ~= 1.384s
total            ~= 2.066s
frontier_rows    ~= 0.746s
initial_seed     ~= 0.230s
```

Run 2 confirmation:

```text
load_full_inputs ~= 0.681s
route_wall       ~= 1.165s
case_total       ~= 1.377s
total            ~= 2.058s
frontier_rows    ~= 0.739s
initial_seed     ~= 0.231s
```

Comparison to Goal5204:

```text
Goal5204 load_full_inputs ~= 1.688-1.693s
Goal5205 load_full_inputs ~= 0.681-0.682s

Goal5204 total            ~= 3.075-3.092s
Goal5205 total            ~= 2.058-2.066s

Goal5204 route_wall       ~= 1.172-1.183s
Goal5205 route_wall       ~= 1.165-1.171s
```

So this goal mainly removes about one second of app input loading. It does not
meaningfully change the route-local algorithmic floor.

## Claim Boundary

This goal claims:

- app-owned public ASCII PLY input loading is faster;
- the strongest current Dragon -> HappyBuddha Level-B run remains correct;
- user-visible total time for this gate drops from about `3.08s` to about
  `2.06s` under the same route settings.

This goal does not claim:

- exact paper dataset reproduction;
- full X-HD paper reproduction;
- author-vs-RTDL performance ratio;
- author performance parity;
- a new RTDL core primitive;
- native backend completion.

## Next

After Goal5205, solved or near-zero costs include:

```text
source+target columns ~= 0.001-0.002s
max_nearest_reduction ~= 0.001s
load_full_inputs      ~= 0.68s
```

Remaining major costs:

```text
frontier_rows / native inline-nearest ~= 0.74-0.75s
initial_state_seed                   ~= 0.23s
grid_cell_mbrs                       ~= 0.10s
```

The next route work should attack the generic native inline-nearest/frontier
execution model or stronger generic spatial work ordering. Further ASCII PLY
micro-optimizations are no longer the main route-local issue.
