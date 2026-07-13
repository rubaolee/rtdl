# Goal5133 - X-HD PLY Input Bridge

## Verdict

`xhd_ply_input_bridge_ready_for_bounded_graphics_gate`

## Purpose

Goal5132 acquired Stanford Dragon / HappyBuddha same-source PLY meshes, but the
existing X-HD paper-app gates consumed only WKT fixtures. Goal5133 adds an
app-owned ASCII PLY vertex input bridge so the same author and RTDL gate runners
can consume bounded PLY fixtures.

This is an input bridge, not an algorithmic X-HD route and not a performance
claim.

## Code Changes

New app-owned input loader:

```text
Paper-reproduction-apps/x-hd-paper/scripts/xhd_input_loader.py
```

It supports:

- `load_wkt_points(path, n_dims=...)`;
- `load_ascii_ply_vertices(path, n_dims=...)`;
- `load_points(path, n_dims=..., input_type="wkt"|"ply")`.

Updated gate runners:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_author_json_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_route_gate.py
```

Both now accept:

```text
--input-type wkt|ply
```

For author runs, this parameter is forwarded to `hd_exec -input_type`. For RTDL
runs, it selects the app-owned loader. The RTDL route gate also renames the load
phase to `load_input_sec` so PLY runs are not mislabeled as WKT.

## Fixtures

New tiny PLY fixtures:

```text
Paper-reproduction-apps/x-hd-paper/data/fixtures/tiny3d_ply_a.ply
Paper-reproduction-apps/x-hd-paper/data/fixtures/tiny3d_ply_b.ply
```

The expected directed input1-to-input2 distance is `2.0`.

## Smoke Artifacts

```text
Paper-reproduction-apps/x-hd-paper/results/tiny3d_ply_local_reference_summary.json
Paper-reproduction-apps/x-hd-paper/results/tiny3d_ply_rtdl_route_summary.json
```

Observed smoke facts:

- local reference reads PLY and computes `directed_a_to_b=2.0`;
- RTDL public 3D column route reads PLY and matches exact reference with
  `rtdl_matches_exact_reference=true`;
- no author binary was run in this local smoke, so `matched=null`;
- no performance claim is authorized.

## Verification

New tests:

```text
tests/goal5133_xhd_ply_input_bridge_test.py
```

Test coverage:

- ASCII PLY vertices load correctly;
- author summary accepts PLY without requiring an author binary;
- RTDL route gate accepts a small PLY fixture and matches exact reference;
- binary PLY fails closed.

Regression command run:

```text
py -m unittest tests.goal5111_xhd_author_json_gate_test \
  tests.goal5115_xhd_rtdl_route_gate_test \
  tests.goal5118_xhd_bounded3d_rtdl_route_gate_test \
  tests.goal5133_xhd_ply_input_bridge_test
```

Result:

```text
Ran 15 tests in 0.346s
OK
```

## Boundary

This goal does not claim:

- author `hd_exec` success on Stanford Dragon / HappyBuddha;
- RTDL success on full-resolution Stanford meshes;
- exact paper dataset reproduction;
- representative correctness;
- paper Figure 5 graphics reproduction;
- performance ratio;
- RTDL implementation of the X-HD RT-core algorithm.

## Next

Goal5134 should run a bounded PLY gate on POD:

1. author `hd_exec` with `--input-type ply` on a reduced-resolution or tiny PLY
   pair;
2. RTDL exact/reference route on the same pair;
3. explicit Level B label unless exact file/hash/provenance is found;
4. no full-resolution exact route unless a scalable generic route exists.
